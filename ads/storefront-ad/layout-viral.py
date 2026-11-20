# Per-size assets for the "viral format" storefront ad: big centred captions (white, slate outline, soft shadow) that
# pop in on hard cuts; the wordmark, AI label, phone stage, mask and end card are reused from v3-<size>/ (layout-v3.py).
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(D, "../parts-ad/source")
B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
WHITE, SLATE = (255, 255, 255, 255), (26, 51, 83, 255)
W = 1080
# H, caption font, caption centre y for full-frame cuts, 4:3 band top, caption centre y for band cuts
SIZES = {"9x16-paid": dict(H=1920, font=132, capY=810, bandY=555, capBandY=430),
         "4x5": dict(H=1350, font=116, capY=560, bandY=270, capBandY=1190),
         "1x1": dict(H=1080, font=100, capY=450, bandY=135, capBandY=1000)}
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
    for name in ("brand.png", "ai.png", "stage-store.png", "phone-mask.png", "phone.json", "endcard.png"):
        os.system(f"cp {os.path.join(D, 'v3-' + key, name)} {out}/")
    json.dump(z, open(os.path.join(out, "viral.json"), "w")); print(key, "ok")
