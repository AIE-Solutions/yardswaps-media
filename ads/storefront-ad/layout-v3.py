# Per-size assets for the v3 storefront ad (full-frame vertical openers): caption cards for the two opener lines,
# the wordmark for early branding, the small AI label, all inside Meta's vertical safe zone (text between 15 and 62
# percent of the height). The phone stage, mask and end card are reused from r9x16-paid / r4x5 (layout.py).
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(D, "../parts-ad/source")
B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
M = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_500Medium.ttf"), s)
BLUE, WHITE = (37, 99, 235), (255, 255, 255)
W = 1080
# H, caption font / line height / baseline bottom, brand y, ai-label y
SIZES = {"9x16-paid": dict(H=1920, cap=(104, 118, 1060), brand=330, ai=1130, src="r9x16-paid", cardTop=180),
         "4x5": dict(H=1350, cap=(92, 104, 760), brand=90, ai=820, src="r4x5", cardTop=300),
         "1x1": dict(H=1080, cap=(80, 92, 640), brand=60, ai=690, src="r1x1", cardTop=440)}
LINES = {"cap-a": "Your yard.", "cap-b": "On one page."}

def shadowed(img, draw_fn, blur=10, alpha=170):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(sh), (0, 0, 0, alpha))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(blur)))
    draw_fn(ImageDraw.Draw(img), None); return img

for key, z in SIZES.items():
    H = z["H"]; out = os.path.join(D, "v3-" + key); os.makedirs(out, exist_ok=True)
    fs, LH, BOTTOM = z["cap"]; F = B(fs); X = 84
    for k, text in LINES.items():
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); top = BOTTOM - LH
        def d_(d, col, text=text, top=top):
            d.text((X, top), text, font=F, fill=col or WHITE + (255,))
        img = shadowed(img, d_)
        ImageDraw.Draw(img).rounded_rectangle((X, top - 40, X + 84, top - 28), radius=6, fill=BLUE + (255,))
        img.save(os.path.join(out, k + ".png"))
    # wordmark: "Yard" white, "Swaps" blue, centred
    f = B(64); img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    w1, w2 = d.textlength("Yard", font=f), d.textlength("Swaps", font=f); x0 = (W - w1 - w2) / 2; y = z["brand"]
    def brand(d, col):
        d.text((x0, y), "Yard", font=f, fill=col or WHITE + (255,)); d.text((x0 + w1, y), "Swaps", font=f, fill=col or BLUE + (255,))
    shadowed(img, brand, blur=8, alpha=150).save(os.path.join(out, "brand.png"))
    f = M(30); img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def ai(d, col): d.text((X, z["ai"]), "AI-generated scene", font=f, fill=col or (255, 255, 255, 220))
    shadowed(img, ai, blur=6, alpha=140).save(os.path.join(out, "ai.png"))
    for name in ("stage-store.png", "phone-mask.png", "phone.json"):
        os.system(f"cp {os.path.join(D, z['src'], name)} {out}/")
    # end card without "Listing is free." (this ad pitches dealers the storefront): endcard-v3.png cropped like layout.py
    base = Image.open(os.path.join(D, "endcard-v3.png")).convert("RGB"); top = z["cardTop"]
    card = Image.new("RGB", (W, H), base.getpixel((20, 20))); card.paste(base.crop((0, top, W, min(1920, top + H))), (0, 0))
    card.save(os.path.join(out, "endcard.png"))
    print(key, "ok")
