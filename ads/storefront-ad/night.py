"""Night variant of the storefront openers: the same three dealer-yard stills
graded dark and moody (the After hours look from ads/after-hours/build.py),
then padded to 4:3 with their own blurred edge strips, into stills-night/.

Usage: python3 ads/storefront-ad/night.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

B = Path(__file__).resolve().parent
SRC = B / "stills"
OUT = B / "stills-night"
# sky: how much the top of the frame falls to night; exposure: overall pull-down
# blur boxes are fractions of the source (x0, y0, x1, y1): dealer watermark, unit numbers
STILLS = {
    "grapple-truck": {"sky": 0.8, "exposure": 0.82, "blur": []},
    "skytrak-telehandler": {"sky": 0.8, "exposure": 0.80,
                            "blur": [(0.80, 0.05, 0.96, 0.20), (0.26, 0.60, 0.33, 0.67)]},
    "f350-supercab": {"sky": 0.75, "exposure": 0.84, "blur": []},
}


def blur_boxes(im, boxes):
    for x0, y0, x1, y1 in boxes:
        b = (int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height))
        im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(max(8, (b[2] - b[0]) // 10))), b)
    return im


def grade(im, sky, exposure):
    a = np.asarray(im).astype(np.float32) / 255.0
    h, w, _ = a.shape
    lum = a.mean(axis=2, keepdims=True)
    a = a * exposure * (0.55 + 0.45 * lum)
    y = np.linspace(0, 1, h)[:, None, None]
    top = np.clip(y / 0.6, 0, 1) ** 0.8
    a = a * (1 - sky * (1 - top))
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 0.8
    shadow = np.array([0.055, 0.13, 0.25], np.float32)
    warm = np.array([1.06, 1.0, 0.90], np.float32)
    a = a * (1 - 0.25 * (1 - lum)) + shadow * 0.25 * (1 - lum) * 0.5
    a = a * (1 + (warm - 1) * lum)
    a = np.clip(a, 0, 1)
    a = a * a * (3 - 2 * a) * 0.6 + a * 0.4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.55) / (h / 2)) ** 2)
    a = a * (1 - 0.55 * np.clip(r - 0.45, 0, 1) ** 1.4)[..., None]
    rng = np.random.default_rng(7)
    a = a + rng.normal(0, 0.012, a.shape).astype(np.float32)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def pad_4x3(im, W=1440, H=1080):
    """Whole photo at full width, the gap above and below from its own blurred edge strips."""
    s = W / im.width
    fg = im.resize((W, round(im.height * s)), Image.LANCZOS)
    if fg.height >= H:
        y = (fg.height - H) // 2
        return fg.crop((0, y, W, y + H))
    top = fg.crop((0, 0, W, 24)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(60))
    bot = fg.crop((0, fg.height - 24, W, fg.height)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(60))
    canvas = Image.new("RGB", (W, H))
    canvas.paste(top.crop((0, 0, W, H // 2)), (0, 0))
    canvas.paste(bot.crop((0, H // 2, W, H)), (0, H // 2))
    canvas.paste(fg, (0, (H - fg.height) // 2))
    return canvas


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for slug, p in STILLS.items():
        im = ImageOps.exif_transpose(Image.open(SRC / f"{slug}.jpg")).convert("RGB")
        im = blur_boxes(im, p["blur"])
        g = grade(im, p["sky"], p["exposure"])
        g.save(OUT / f"{slug}.jpg", quality=92)
        pad_4x3(g).save(OUT / f"{slug}-4x3.jpg", quality=92)
        print(slug, im.size)
