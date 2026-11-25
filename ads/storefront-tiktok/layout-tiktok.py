# TikTok-safe 9:16 assets for the storefront ad (11-25, Alan: "We should post our awesome storefront ads there").
# TikTok lays its caption over the bottom of the frame and its like/comment/share buttons down the right edge, so at
# 1080x1920 no text or call to action goes in the right 140 px or the bottom 400 px. Starts from vr-9x16-paid/ (the
# cut live on Meta: big logo, listing cards, founding end card) and writes vr-9x16-tiktok/ for build-viral4.sh RATIO=9x16-tiktok:
#   - the five captions are redrawn with 140 px of clear space on their right, so build-viral4.sh's centring lands
#     them 70 px left of centre, clear of the button column;
#   - the phone stage, the /dealers screen and the founding end card (flat backgrounds) are scaled down and moved
#     up and left inside the safe area; phone.json and the phone mask follow the phone stage.
# vr-9x16-paid/ and every earlier cut are left as they were.
import os, json, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(D, "vr-9x16-paid"); OUT = os.path.join(D, "vr-9x16-tiktok")
S = os.path.join(D, "../parts-ad/source"); B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
W, H, RIGHT, BOTTOM = 1080, 1920, 140, 400
SAFE_X1, SAFE_Y1 = W - RIGHT, H - BOTTOM
WHITE, SLATE = (255, 255, 255, 255), (26, 51, 83, 255)
os.makedirs(OUT, exist_ok=True)
for n in os.listdir(SRC):
    shutil.copy(os.path.join(SRC, n), OUT)

LINES = ["Your whole yard.", "One page.", "Every unit.", "Your hours.", "Your links."]
z = json.load(open(os.path.join(SRC, "viral.json"))); PAD = 48
for i, text in enumerate(LINES, 1):
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10))); fs = z["font"]
    while True:  # the line plus its shadow pad must fit between x=40 and the button column
        F = B(fs); x0, y0, x1, y1 = d0.textbbox((0, 0), text, font=F, stroke_width=10)
        if x1 - x0 + 2 * PAD <= SAFE_X1 - 40: break
        fs -= 4
    tw, th = x1 - x0 + 2 * PAD, y1 - y0 + 2 * PAD
    img = Image.new("RGBA", (tw + RIGHT, th), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((PAD - x0, PAD - y0 + 6), text, font=F, fill=(0, 0, 0, 150), stroke_width=10, stroke_fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(img).text((PAD - x0, PAD - y0), text, font=F, fill=WHITE, stroke_width=10, stroke_fill=SLATE)
    # centred by build-viral4.sh: text right edge = (W + w) / 2 - RIGHT - PAD
    assert (W + img.width) / 2 - RIGHT - PAD <= SAFE_X1 and (W - img.width) / 2 >= 0, (text, img.width)
    img.save(os.path.join(OUT, f"cap{i}.png")); print("cap", i, fs, img.size)

def fit(name, k, ox, oy):
    """Scale a flat-background full frame by k and place it at (ox, oy) on the same background."""
    im = Image.open(os.path.join(SRC, name)).convert("RGB"); bg = im.getpixel((5, 5))
    out = Image.new("RGB", (W, H), bg); sm = im.resize((round(W * k), round(H * k)), Image.LANCZOS)
    out.paste(sm, (round(ox), round(oy))); out.save(os.path.join(OUT, name)); return out

def bbox(im):
    from PIL import ImageChops
    bg = im.getpixel((5, 5))
    return ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()

# phone stage: content 208..873 x 317..1760 -> heading near y 200, phone bottom above the caption zone
k = 0.86; ox = 470 - 540 * k; oy = 200 - 317 * k
im = fit("stage-store.png", k, ox, oy); print("stage-store", bbox(im))
pj = json.load(open(os.path.join(SRC, "phone.json"))); p = pj["phone"]
ev = lambda v: int(round(v / 2) * 2)
p2 = dict(x=ev(p["x"] * k + ox), y=ev(p["y"] * k + oy), w=ev(p["w"] * k), h=ev(p["h"] * k))
pj["phone"] = p2; json.dump(pj, open(os.path.join(OUT, "phone.json"), "w")); print("phone", p2)
Image.open(os.path.join(SRC, "phone-mask.png")).resize((p2["w"], p2["h"]), Image.LANCZOS).save(os.path.join(OUT, "phone-mask.png"))
# /dealers screen: content 64..1017 x 494..1583
k = 0.84; im = fit("stage-dealers.png", k, 470 - 540 * k, 1440 - 1583 * k); print("stage-dealers", bbox(im))
# founding end card: content 44..1037 x 419..1255 (question pill reaches x 1037)
k = 0.84; im = fit("endcard-founding.png", k, 470 - 540 * k, 960 - 960 * k); print("endcard-founding", bbox(im))
json.dump(dict(z, tiktok_safe=dict(right=RIGHT, bottom=BOTTOM)), open(os.path.join(OUT, "viral.json"), "w"))
