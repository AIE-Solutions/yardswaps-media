# Live /dealers page (yardswaps.com, re-captured 2026-11-25 after the "Storefront plan" rename (first capture 11-20) on a 390x844 mobile viewport at 3x, signed out, light theme)
# shown as a real-screen card: the top of the page down to "30 days free", cut above the price row so the
# founding $29 stays off screen (it lives in the caption only). Writes vr-<size>/stage-dealers.png.
import os
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
SHOT = Image.open(os.path.join(D, "rec", os.environ.get("SHOT", "dealers-mobile-live-1125.png"))).convert("RGB")
CUT = int(os.environ.get("CUT", 1334))  # first row of the price divider: 1335 on the 11-25 capture (1348 on 11-20)
crop = SHOT.crop((0, 0, SHOT.width, CUT))
BG = (245, 245, 247)
for key, (H, maxh) in {"9x16-paid": (1920, 1180), "4x5": (1350, 1050), "1x1": (1080, 900)}.items():
    W = 1080
    w = min(900, int(crop.width * maxh / crop.height)); h = int(crop.height * w / crop.width)
    card = crop.resize((w, h), Image.LANCZOS)
    r = 44; m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    img = Image.new("RGB", (W, H), BG)
    x = (W - w) // 2; y = (H - h) // 2 + (60 if key == "9x16-paid" else 0)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x, y + 18, x + w, y + h + 18), r, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(28)); img.paste((26, 51, 83), (0, 0), sh)
    img.paste(card, (x, y), m)
    ImageDraw.Draw(img).rounded_rectangle((x, y, x + w - 1, y + h - 1), r, outline=(216, 216, 218), width=2)
    img.save(os.path.join(D, "vr-" + key, "stage-dealers.png")); print(key, w, h, x, y)
