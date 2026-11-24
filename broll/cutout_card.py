#!/usr/bin/env python3
"""Brand covers from a real listing photo, cut out with Runway's Seedream 5.5 Layers.

Runway (Nov 12 2026) added `seedream5.5_layers`: it splits one photo into a base
image plus transparent PNG layers. We use Runway ONLY for the outline. The item's
pixels on every card come from the real listing photo, never from the model:

  1. pick the layer that is the item (largest layer that is not the whole frame),
  2. check the layer against the photo inside its outline; if the model redrew the
     item (colours or shape moved) the card is refused and nothing is published,
  3. take the real photo's pixels through that outline (alpha) and place the whole
     item on the brand background, with the title, price and wordmark.

Outputs in broll/cutouts/<slug>/:
  item.png          the real item, transparent background (for video editors)
  cover-9x16.jpg    1080x1920 Reels / Shorts / TikTok cover and Story
  card-4x5.jpg      1080x1350 feed card (IG/FB) or storefront promo
  check.jpg         photo | outline | cover side by side, for the review step
  check.json        the numbers behind the pass/fail

Run by runway.yml after a seedream5.5_layers run, or by hand:
  python3 broll/cutout_card.py --photo broll/in/x.jpg --layers broll/layers/x --slug x \
      --title "<listing title>" --price "<listing price>"
--mask <png> uses any alpha PNG instead of Runway layers (tests only).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "listings", "fonts")
WORDMARK = os.path.join(ROOT, "broll", "in", "brand-kit", "wordmark", "yardswaps-wordmark-on-light.png")
SLATE = (26, 51, 83)        # --slate-brand #1A3353
SLATE_DEEP = (14, 34, 64)   # --slate-deep  #0E2240
BLUE = (37, 99, 235)        # --accent-fill #2563EB
WHITE = (255, 255, 255)
MUTED = (255, 255, 255, 200)
PAGE = (243, 243, 245)      # light page, as in the Runway ad-builder ads
INK = (32, 32, 32)          # --text-primary #202020
LOGO = os.path.join(ROOT, "broll", "in", "brand-kit", "logo", "yardswaps-logo-512.png")

# A layer whose pixels inside its own outline differ from the photo by more than this
# (mean absolute difference, 0-255) was redrawn by the model, not cut out.
MAX_MEAN_DIFF = 14.0
MAX_P95_DIFF = 60.0
MIN_COVER, MAX_COVER = 0.04, 0.88   # share of the frame the item layer may cover


def die(msg):
    print(f"cutout_card: {msg}", file=sys.stderr)
    sys.exit(2)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def bold(size):
    f = font("SpaceGrotesk.ttf", size)
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    return f


def place_layer(layer, row, size, photo=None):
    """Return the layer as RGBA on the photo's canvas (layers may be cropped to a box)."""
    W, H = size
    if layer.size == (W, H):
        return layer
    box = (row or {}).get("boundingBox") or {}
    norm = box.get("normalized") if isinstance(box, dict) else None
    absb = box.get("absolute") if isinstance(box, dict) else None
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if norm and all(k in norm for k in ("x", "y", "width", "height")):
        x, y = round(norm["x"] * W), round(norm["y"] * H)
        w, h = max(1, round(norm["width"] * W)), max(1, round(norm["height"] * H))
        canvas.paste(layer.resize((w, h), Image.LANCZOS), (x, y))
        return canvas
    if absb and all(k in absb for k in ("x", "y", "width", "height")):
        # absolute coords are in the model's working size; scale by the base image
        sx = W / (absb.get("canvasWidth") or W)
        sy = H / (absb.get("canvasHeight") or H)
        x, y = round(absb["x"] * sx), round(absb["y"] * sy)
        w, h = max(1, round(absb["width"] * sx)), max(1, round(absb["height"] * sy))
        canvas.paste(layer.resize((w, h), Image.LANCZOS), (x, y))
        return canvas
    if abs(layer.size[0] / layer.size[1] - W / H) < 0.01:
        return layer.resize((W, H), Image.LANCZOS)
    if photo is not None:
        # Results fetched through the Runway MCP come without boundingBox, on a
        # padded canvas of their own size. Find where the layer sits by matching
        # it against the photo; judge() still refuses a poor fit.
        fit = align_layer(photo, layer)
        if fit:
            w, h = round(layer.width * fit["scale"]), round(layer.height * fit["scale"])
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            canvas.paste(layer.resize((w, h), Image.LANCZOS), (round(fit["x"]), round(fit["y"])))
            return canvas
    return None


def _corr(img, k):
    """Valid cross-correlation of a 2-D image with kernel k (FFT, numpy only)."""
    H, W = img.shape
    h, w = k.shape
    sh = (H + h - 1, W + w - 1)
    r = np.fft.irfft2(np.fft.rfft2(img, sh) * np.fft.rfft2(k[::-1, ::-1], sh), sh)
    return r[h - 1:H, w - 1:W]


def _ssd_map(p, t, m):
    """Mean masked squared difference for every placement of t inside p."""
    out = 0.0
    for c in range(3):
        I, T = p[..., c], t[..., c]
        out = out + (m * T * T).sum() - 2 * _corr(I, m * T) + _corr(I * I, m)
    return out / (3 * m.sum())


def align_layer(photo, layer, coarse=4):
    """Scale and offset that put the layer's canvas on the photo (full-res pixels)."""
    bb = layer.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    if not bb:
        return None
    T = layer.crop(bb)
    k = 1000 / max(photo.size)
    P = photo.convert("RGB").resize((round(photo.width * k), round(photo.height * k)), Image.LANCZOS)

    def search(img, scales, near=None):
        p = np.asarray(img, np.float32) / 255
        best = None
        for sc in scales:
            s = sc * max(img.size) / max(layer.size)
            tw, th = round(T.width * s), round(T.height * s)
            if tw < 8 or th < 8 or tw >= img.width or th >= img.height:
                continue
            t = np.asarray(T.resize((tw, th), Image.LANCZOS), np.float32) / 255
            m = (t[..., 3] > 0.9).astype(np.float32)
            if m.sum() < 50:
                continue
            d = _ssd_map(p, t[..., :3], m)
            if near:
                x0, y0, r = near
                keep = np.full_like(d, np.inf)
                ys = slice(max(0, y0 - r), y0 + r + 1)
                xs = slice(max(0, x0 - r), x0 + r + 1)
                keep[ys, xs] = d[ys, xs]
                d = keep
            y, x = np.unravel_index(np.argmin(d), d.shape)
            if best is None or d[y, x] < best[0]:
                best = (float(d[y, x]), sc, int(x), int(y), s)
        return best

    small = P.resize((P.width // coarse, P.height // coarse), Image.LANCZOS)
    b = search(small, np.arange(0.80, 1.25, 0.01))
    if not b:
        return None
    b = search(P, np.arange(b[1] - 0.012, b[1] + 0.0121, 0.002),
               near=(b[2] * coarse, b[3] * coarse, coarse * 3))
    if not b:
        return None
    _, _, x, y, s = b
    f = photo.width / P.width
    return {"scale": s * f, "x": (x - bb[0] * s) * f, "y": (y - bb[1] * s) * f}


def judge(photo, layer):
    """How well a full-canvas RGBA layer matches the photo inside its outline."""
    a = np.asarray(layer.getchannel("A"), dtype=np.float32) / 255.0
    cover = float((a > 0.5).mean())
    inside = a > 0.9
    if inside.sum() < 500:
        return {"cover": cover, "mean_diff": None, "p95_diff": None}
    p = np.asarray(photo, dtype=np.float32)
    l = np.asarray(layer.convert("RGB"), dtype=np.float32)
    d = np.abs(p - l).mean(axis=2)[inside]
    return {"cover": round(cover, 4), "mean_diff": round(float(d.mean()), 2),
            "p95_diff": round(float(np.percentile(d, 95)), 2)}


def pick_item(photo, layers_dir, forced=None):
    rows = []
    meta_path = os.path.join(layers_dir, "layers.json")
    meta = json.load(open(meta_path)) if os.path.isfile(meta_path) else []
    files = [r["file"] for r in meta] if meta else sorted(
        os.path.join(layers_dir, f) for f in os.listdir(layers_dir) if f.endswith(".png"))
    for i, f in enumerate(files):
        path = f if os.path.isabs(f) or os.path.isfile(f) else os.path.join(ROOT, f)
        img = Image.open(path).convert("RGBA")
        placed = place_layer(img, meta[i] if i < len(meta) else None, photo.size, photo)
        if placed is None:
            rows.append({"i": i, "file": f, "skip": "size does not match the photo"})
            continue
        j = judge(photo, placed)
        j.update({"i": i, "file": os.path.relpath(path, ROOT) if path.startswith(ROOT) else f, "name": (meta[i] if i < len(meta) else {}).get("name")})
        ok = (j["mean_diff"] is not None and MIN_COVER <= j["cover"] <= MAX_COVER
              and j["mean_diff"] <= MAX_MEAN_DIFF and j["p95_diff"] <= MAX_P95_DIFF)
        j["ok"] = bool(ok)
        j["_img"] = placed
        rows.append(j)
    cands = [r for r in rows if r.get("ok")]
    if forced is not None:
        cands = [r for r in rows if r.get("i") == forced and r.get("ok")]
    best = max(cands, key=lambda r: r["cover"]) if cands else None
    return best, rows


def clean_alpha(alpha):
    """Small feather so the edge sits on the background without a halo."""
    a = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    return a


def real_cutout(photo, alpha):
    """The real photo's pixels through the model's outline, cropped to the item."""
    item = photo.convert("RGBA")
    item.putalpha(clean_alpha(alpha))
    bbox = alpha.point(lambda v: 255 if v > 24 else 0).getbbox()
    if not bbox:
        die("empty outline")
    return item.crop(bbox)


def gradient(w, h):
    top = np.array(SLATE, dtype=np.float32)
    bot = np.array(SLATE_DEEP, dtype=np.float32)
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    g = top * (1 - t) + bot * t
    g = np.repeat(g, w, axis=1)
    # soft light pool behind the item
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h * 0.42
    r = np.sqrt(((xx - cx) / (w * 0.62)) ** 2 + ((yy - cy) / (h * 0.36)) ** 2)
    glow = np.clip(1 - r, 0, 1)[..., None] ** 2 * 34
    return Image.fromarray(np.clip(g + glow, 0, 255).astype(np.uint8), "RGB")


def wrap(draw, text, f, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while draw.textlength(lines[-1] + "…", font=f) > width and " " in lines[-1]:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] += "…"
    return lines


def render(item, W, H, title, price, line, out):
    """Runway ad-builder house style (the Nov 9 "Idle gear" / "Snap it" ads):
    light page, big slate headline with a short blue rule, the real item with a
    soft floor shadow, price in blue, one plain line, app icon + wordmark."""
    tall = H / W > 1.5
    canvas = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(canvas)
    pad = round(W * 0.087)
    # headline: the listing title as written, set tight and condensed like the
    # ad-builder headlines (Space Grotesk Bold squeezed to 80 % width)
    squeeze = 0.80
    hf = bold(round(W * (0.125 if tall else 0.105)))
    lines = wrap(d, title, hf, round((W - 2 * pad) / squeeze), 3)
    while len(lines) == 3 and hf.size > W * 0.08 and \
            d.textlength(lines[-1], font=hf) > (W - 2 * pad) / squeeze:
        hf = bold(hf.size - 4)
        lines = wrap(d, title, hf, round((W - 2 * pad) / squeeze), 3)
    lh = round(hf.size * 0.98)
    y = round(H * (0.05 if tall else 0.045))
    for ln in lines:
        tw = round(d.textlength(ln, font=hf)) + 8
        layer = Image.new("RGBA", (tw, round(hf.size * 1.3)), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((0, 0), ln, font=hf, fill=SLATE)
        layer = layer.resize((max(1, round(tw * squeeze)), layer.height), Image.LANCZOS)
        canvas.alpha_composite(layer, (pad, y))
        y += lh
    y += round(hf.size * 0.22)
    d.rectangle((pad, y, pad + round(W * 0.24), y + max(4, round(W * 0.0065))), fill=BLUE)
    top = y + round(H * (0.035 if tall else 0.03))
    # bottom block: price, one line, icon + wordmark, url
    pf = bold(round(W * (0.075 if tall else 0.064)))
    lf = font("Inter.ttf", round(W * (0.036 if tall else 0.032)))
    icon_h = round(W * (0.13 if tall else 0.105))
    uf = font("Inter.ttf", round(W * (0.034 if tall else 0.03)))
    url_y = H - pad - uf.size
    icon_y = url_y - round(H * 0.018) - icon_h
    line_y = icon_y - round(H * (0.04 if tall else 0.03)) - lf.size
    price_y = line_y - round(lf.size * 0.7) - pf.size if price else line_y
    box = (pad, top, W - pad, price_y - round(H * 0.035))
    bw, bh = box[2] - box[0], box[3] - box[1]
    sc = min(bw / item.width, bh / item.height)
    it = item.resize((max(1, round(item.width * sc)), max(1, round(item.height * sc))), Image.LANCZOS)
    x = box[0] + (bw - it.width) // 2
    yi = box[1] + (bh - it.height) // 2
    # soft floor shadow from the item's own outline
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    a = it.getchannel("A").resize((it.width, max(1, it.height // 12)))
    shadow = Image.new("RGBA", a.size, (20, 30, 45, 0))
    shadow.putalpha(a.point(lambda v: v * 90 // 255))
    sh.paste(shadow, (x, yi + it.height - a.height // 2), shadow)
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(round(W * 0.014))))
    canvas.alpha_composite(it, (x, yi))
    d = ImageDraw.Draw(canvas)
    if price:
        d.text((pad, price_y), price, font=pf, fill=BLUE)
    d.text((pad, line_y), line, font=lf, fill=INK)
    if os.path.isfile(LOGO):
        ic = Image.open(LOGO).convert("RGBA").resize((icon_h, icon_h), Image.LANCZOS)
        m = Image.new("L", ic.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, icon_h - 1, icon_h - 1), radius=round(icon_h * 0.22), fill=255)
        ic.putalpha(m)
        canvas.alpha_composite(ic, (pad, icon_y))
    if os.path.isfile(WORDMARK):
        wm = Image.open(WORDMARK).convert("RGBA")
        wh = round(icon_h * 0.78)
        wm = wm.resize((round(wm.width * wh / wm.height), wh), Image.LANCZOS)
        canvas.alpha_composite(wm, (pad + icon_h + round(W * 0.03), icon_y + (icon_h - wh) // 2))
    dd = ImageDraw.Draw(canvas)
    ux = pad
    for ch in "yardswaps.com":      # medium weight, a little tracking, as in the ads
        dd.text((ux, url_y), ch, font=uf, fill=SLATE, stroke_width=1, stroke_fill=SLATE)
        ux += dd.textlength(ch, font=uf) + round(uf.size * 0.06)
    canvas.convert("RGB").save(out, quality=90, optimize=True, progressive=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True)
    ap.add_argument("--layers", help="broll/layers/<slug> from a seedream5.5_layers run")
    ap.add_argument("--mask", help="tests only: an alpha PNG the size of the photo")
    ap.add_argument("--layer", type=int, help="force this layer index (still checked)")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--price", default="")
    ap.add_argument("--line", default="Find used equipment near you.")
    a = ap.parse_args()

    photo = Image.open(a.photo).convert("RGB")
    out_dir = os.path.join(ROOT, "broll", "cutouts", a.slug)
    os.makedirs(out_dir, exist_ok=True)
    if a.mask:
        alpha = Image.open(a.mask).convert("L").resize(photo.size)
        report = {"source": "mask", "mask": a.mask}
    else:
        if not a.layers:
            die("--layers or --mask is required")
        best, rows = pick_item(photo, a.layers, a.layer)
        report = {"source": "seedream5.5_layers", "layers": [
            {k: v for k, v in r.items() if k != "_img"} for r in rows]}
        if not best:
            json.dump(report, open(os.path.join(out_dir, "check.json"), "w"), indent=1)
            die("no layer matches the real photo closely enough (the model redrew the item "
                "or split it up); nothing was made. See check.json")
        alpha = best["_img"].getchannel("A")
        report["picked"] = best["i"]
    item = real_cutout(photo, alpha)
    item.save(os.path.join(out_dir, "item.png"))
    title = a.title or a.slug.replace("-", " ").title()
    cover = render(item, 1080, 1920, title, a.price, a.line, os.path.join(out_dir, "cover-9x16.jpg"))
    card = render(item, 1080, 1350, title, a.price, a.line, os.path.join(out_dir, "card-4x5.jpg"))
    # review sheet: photo | outline | cover
    h = 960
    p = photo.resize((round(photo.width * h / photo.height), h))
    m = alpha.resize(p.size).convert("RGB")
    c = Image.open(cover).resize((round(1080 * h / 1920), h))
    sheet = Image.new("RGB", (p.width + m.width + c.width + 40, h), (240, 240, 240))
    sheet.paste(p, (0, 0)); sheet.paste(m, (p.width + 20, 0)); sheet.paste(c, (p.width + m.width + 40, 0))
    sheet.save(os.path.join(out_dir, "check.jpg"), quality=85)
    report.update({"title": title, "price": a.price,
                   "files": [os.path.relpath(f, ROOT) for f in (cover, card)]})
    json.dump(report, open(os.path.join(out_dir, "check.json"), "w"), indent=1)
    print(f"cutout_card: {out_dir} ({os.path.basename(cover)}, {os.path.basename(card)})")


if __name__ == "__main__":
    main()
