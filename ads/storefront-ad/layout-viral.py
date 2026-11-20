# Per-size assets for the "viral format" storefront ad: big centred captions (white, slate outline, soft shadow) that
# pop in on hard cuts; the wordmark, AI label, phone stage, mask and end card are reused from v3-<size>/ (layout-v3.py).
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(D, "../parts-ad/source")
B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
WHITE, SLATE = (255, 255, 255, 255), (26, 51, 83, 255)
W = 1080
# H, caption font, caption centre y for full-frame cuts, 4:3 band top, caption centre y for band cuts
# badgeY: top of the logo pill (top-left, below Meta's top overlay zone in 9:16); the 9:16 band and its caption sit
# lower than in the first viral cut so the caption clears the pill.
SIZES = {"9x16-paid": dict(H=1920, font=132, capY=810, bandY=640, capBandY=500, badgeY=290),
         "4x5": dict(H=1350, font=116, capY=560, bandY=270, capBandY=1190, badgeY=48),
         "1x1": dict(H=1080, font=100, capY=450, bandY=150, capBandY=1005, badgeY=40)}
WM = os.path.join(D, "../../broll/in/brand-kit/wordmark/yardswaps-wordmark-on-light.png")  # the real wordmark, slate + blue

def badge(H, y, x=48, glyph_h=52, pad_x=34, pad_y=22):
    """The logo as a lockup that reads on any shot: the brand-kit wordmark on a white pill with a soft shadow,
    pinned top-left. Returns a full-frame RGBA layer."""
    wm = Image.open(WM).convert("RGBA"); wm = wm.crop(wm.getbbox())
    wm = wm.resize((round(wm.width * glyph_h / wm.height), glyph_h), Image.LANCZOS)
    pw, ph = wm.width + 2 * pad_x, glyph_h + 2 * pad_y
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x, y + 6, x + pw, y + ph + 6), radius=ph // 2, fill=(0, 0, 0, 110))
    layer = Image.alpha_composite(layer, sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(layer).rounded_rectangle((x, y, x + pw, y + ph), radius=ph // 2, fill=(255, 255, 255, 255))
    layer.alpha_composite(wm, (x + pad_x, y + pad_y)); return layer
LINES = ["Your whole yard.", "One page.", "Every unit.", "Your hours.", "Your links."]
for key, z in SIZES.items():
    out = os.path.join(D, "vr-" + key); os.makedirs(out, exist_ok=True); F = B(z["font"]); PAD = 48
    for i, text in enumerate(LINES, 1):
        d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10))); fs = z["font"]
        while True:  # shrink a long line until it fits with side margins
            F = B(fs); x0, y0, x1, y1 = d0.textbbox((0, 0), text, font=F, stroke_width=10)
            if x1 - x0 + 2 * PAD <= W - 80: break
            fs -= 4
        img = Image.new("RGBA", (x1 - x0 + 2 * PAD, y1 - y0 + 2 * PAD), (0, 0, 0, 0))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((PAD - x0, PAD - y0 + 6), text, font=F, fill=(0, 0, 0, 150), stroke_width=10, stroke_fill=(0, 0, 0, 150))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(14)))
        ImageDraw.Draw(img).text((PAD - x0, PAD - y0), text, font=F, fill=WHITE, stroke_width=10, stroke_fill=SLATE)
        assert img.width <= W - 40, (text, img.width)
        img.save(os.path.join(out, f"cap{i}.png"))
    Image.new("RGBA", (W, z["H"]), (0, 0, 0, 0)).save(os.path.join(out, "blank.png"))
    badge(z["H"], z["badgeY"]).save(os.path.join(out, "brand.png"))
    for name in ("ai.png", "stage-store.png", "phone-mask.png", "phone.json", "endcard.png"):
        os.system(f"cp {os.path.join(D, 'v3-' + key, name)} {out}/")
    json.dump(z, open(os.path.join(out, "viral.json"), "w")); print(key, "ok")
