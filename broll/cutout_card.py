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
    bg = gradient(W, H)
    pad = round(W * 0.074)
    # wordmark on a white pill, top-left (house style)
    if os.path.isfile(WORDMARK):
        wm = Image.open(WORDMARK).convert("RGBA")
        wh = round(W * 0.052)
        wm = wm.resize((round(wm.width * wh / wm.height), wh), Image.LANCZOS)
        pill = Image.new("RGBA", (wm.width + 2 * round(wh * 0.55), wh + 2 * round(wh * 0.38)), (0, 0, 0, 0))
        ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, pill.height - 1),
                                               radius=pill.height // 2, fill=WHITE)
        pill.alpha_composite(wm, (round(wh * 0.55), round(wh * 0.38)))
        bg.paste(pill, (pad, pad), pill)
        top = pad + pill.height + round(H * 0.03)
    else:
        top = pad + round(H * 0.06)
    text_h = round(H * (0.27 if H / W > 1.5 else 0.30))
    box = (pad, top, W - pad, H - text_h)          # the whole item fits in here
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = min(bw / item.width, bh / item.height)
    it = item.resize((max(1, round(item.width * s)), max(1, round(item.height * s))), Image.LANCZOS)
    x = box[0] + (bw - it.width) // 2
    y = box[1] + (bh - it.height) // 2
    # ground shadow from the item's own outline
    sh = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    a = it.getchannel("A").resize((it.width, max(1, it.height // 10)))
    shadow = Image.new("RGBA", a.size, (0, 0, 0, 150))
    shadow.putalpha(a.point(lambda v: v * 150 // 255))
    sh.paste(shadow, (x, y + it.height - a.height // 2), shadow)
    sh = sh.filter(ImageFilter.GaussianBlur(round(W * 0.018)))
    canvas = bg.convert("RGBA")
    canvas.alpha_composite(sh)
    canvas.alpha_composite(it, (x, y))
    d = ImageDraw.Draw(canvas)
    # lower-left text block with the blue bar
    ty = H - text_h + round(H * 0.02)
    tf = bold(round(W * (0.064 if H / W > 1.5 else 0.058)))
    lines = wrap(d, title, tf, W - 2 * pad - round(W * 0.04), 2)
    lh = round(tf.size * 1.16)
    bar_h = lh * len(lines) + (round(tf.size * 1.2) if price else 0)
    d.rounded_rectangle((pad, ty + 4, pad + round(W * 0.011), ty + bar_h - 4), radius=6, fill=BLUE)
    tx = pad + round(W * 0.035)
    for i, ln in enumerate(lines):
        d.text((tx, ty + i * lh), ln, font=tf, fill=WHITE)
    yy = ty + lh * len(lines) + round(H * 0.008)
    if price:
        pf = bold(round(W * 0.056))
        pw = d.textlength(price, font=pf)
        d.rounded_rectangle((tx - 6, yy, tx + pw + 34, yy + round(pf.size * 1.32)),
                            radius=round(pf.size * 0.66), fill=BLUE)
        d.text((tx + 14, yy + round(pf.size * 0.12)), price, font=pf, fill=WHITE)
        yy += round(pf.size * 1.32)
    ff = font("Inter.ttf", round(W * 0.034))
    d.text((pad, H - pad - ff.size), line, font=ff, fill=MUTED)
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
    ap.add_argument("--line", default="Find it on YardSwaps · yardswaps.com")
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
