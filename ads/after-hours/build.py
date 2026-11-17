"""After-hours photo posts: one real listing photo, graded dark and moody,
on a 1080x1350 feed canvas. No text on the image (the reference look).

Usage: python3 ads/after-hours/build.py <out_dir>
Sources come from broll/in/brand-kit/site-listings (real live-site listing
photos, already checked for faces). Plates, door numbers and watermarks are
blurred by the boxes in POSTS below.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "broll/in/brand-kit/site-listings"
W, H = 1080, 1350

# blur boxes are fractions of the source image (x0, y0, x1, y1)
# sky: how much to pull the top of the frame down (outdoor shots)
POSTS = [
    {"slug": "peterbilt-379", "file": "fleet-2004-peterbilt-379-sleeper-truck-a-c.jpg",
     "sky": 0.8, "exposure": 0.80, "blur": [], "crop": (0.06, 0.0, 0.92, 1.0), "size": (1080, 1080)},
    {"slug": "komatsu-engine", "file": "parts-komatsu-hd785-7-engine-for-sale-worldwide-shipping.jpg",
     "sky": 0.35, "exposure": 0.78, "blur": [], "anchor": 1.0},
    {"slug": "hotsy-pressure-washer", "file": "pressure-hotsy-hot-water-pressure-washer-cart.jpg",
     "sky": 0.15, "exposure": 0.90, "blur": []},
    {"slug": "micrometer-set", "file": "machining-mitutoya-outside-micrometer-set-large.jpg",
     "sky": 0.2, "exposure": 0.85, "blur": []},
    {"slug": "telehandler", "file": "forklifts-2014-sky-trak-6042-telehandler.jpg",
     "sky": 0.8, "exposure": 0.80, "crop": (0.03, 0.0, 0.88, 1.0), "size": (1080, 1080),
     # dealer watermark top right, unit number on the white truck door
     "blur": [(0.80, 0.04, 0.96, 0.16), (0.26, 0.60, 0.33, 0.66)]},
]


def blur_boxes(im, boxes):
    for x0, y0, x1, y1 in boxes:
        b = (int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height))
        region = im.crop(b).filter(ImageFilter.GaussianBlur(max(8, (b[2] - b[0]) // 10)))
        im.paste(region, b)
    return im


def grade(im, sky, exposure):
    a = np.asarray(im).astype(np.float32) / 255.0
    h, w, _ = a.shape
    # darken midtones, keep highlights (chrome, lights) bright
    lum = a.mean(axis=2, keepdims=True)
    a = a * exposure * (0.55 + 0.45 * lum)
    # top of frame falls off to night (sky, ceilings)
    y = np.linspace(0, 1, h)[:, None, None]
    top = np.clip(y / 0.6, 0, 1) ** 0.8
    a = a * (1 - sky * (1 - top))
    # cool, desaturated shadows; warm highlights
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 0.8
    shadow = np.array([0.055, 0.13, 0.25], np.float32)  # slate-deep tint
    warm = np.array([1.06, 1.0, 0.90], np.float32)
    a = a * (1 - 0.25 * (1 - lum)) + shadow * 0.25 * (1 - lum) * 0.5
    a = a * (1 + (warm - 1) * lum)
    # contrast s-curve
    a = np.clip(a, 0, 1)
    a = a * a * (3 - 2 * a) * 0.6 + a * 0.4
    # radial vignette
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.55) / (h / 2)) ** 2)
    a = a * (1 - 0.55 * np.clip(r - 0.45, 0, 1) ** 1.4)[..., None]
    # fine grain
    rng = np.random.default_rng(7)
    a = a + rng.normal(0, 0.012, a.shape).astype(np.float32)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def compose(im, size=(W, H), anchor=0.5):
    """Whole photo on the feed canvas. When the photo is within 8% of the
    canvas shape it fills it (crop <= 1.07x, cut from the side named by
    anchor); otherwise it is fit and the gap fades to night from its own
    edge colours, so no stretched or mirrored copy shows."""
    cw, ch = size
    s_fit = min(cw / im.width, ch / im.height)
    s_cov = max(cw / im.width, ch / im.height)
    if s_cov / s_fit <= 1.08:
        big = im.resize((round(im.width * s_cov), round(im.height * s_cov)), Image.LANCZOS)
        x = (big.width - cw) // 2
        y = round((big.height - ch) * anchor)
        return big.crop((x, y, x + cw, y + ch))
    fw, fh = round(im.width * s_fit), round(im.height * s_fit)
    fg = np.asarray(im.resize((fw, fh), Image.LANCZOS)).astype(np.float32)
    canvas = np.zeros((ch, cw, 3), np.float32)
    x = (cw - fw) // 2
    y = (ch - fh) // 2
    # gap above: top-row colour fading to near black; gap below: bottom-row colour fading
    top = fg[:8].mean(axis=0).mean(axis=0)
    bot = fg[-8:].mean(axis=0).mean(axis=0)
    night = np.array([6, 9, 14], np.float32)
    if y > 0:
        t = np.linspace(0, 1, y, dtype=np.float32)[:, None, None] ** 1.5
        canvas[:y] = night + (top - night) * t
    if y + fh < ch:
        t = np.linspace(1, 0, ch - y - fh, dtype=np.float32)[:, None, None] ** 1.5
        canvas[y + fh:] = night + (bot - night) * t
    canvas[y:y + fh, x:x + fw] = fg
    # soften the seams
    f = 90
    img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
    soft = img.filter(ImageFilter.GaussianBlur(26))
    m = np.zeros((ch, cw), np.float32)
    for edge in (y, y + fh):
        if 0 < edge < ch:
            lo, hi = max(0, edge - f), min(ch, edge + f)
            m[lo:hi] = 1 - np.abs(np.arange(lo, hi) - edge)[:, None] / f
    img.paste(soft, (0, 0), Image.fromarray((m * 255).astype(np.uint8)))
    return img


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for p in POSTS:
        im = ImageOps.exif_transpose(Image.open(SRC / p["file"])).convert("RGB")
        im = blur_boxes(im, p["blur"])
        if "crop" in p:
            x0, y0, x1, y1 = p["crop"]
            im = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
        im = grade(im, p["sky"], p["exposure"])
        canvas = compose(im, p.get("size", (W, H)), p.get("anchor", 0.5))
        ratio = "4x5" if canvas.size == (W, H) else "1x1"
        dst = out / f"after-hours-{p['slug']}-{ratio}.jpg"
        canvas.save(dst, quality=90, optimize=True, progressive=True)
        print(dst, canvas.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ads/after-hours/out")
