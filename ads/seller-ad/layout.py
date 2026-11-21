# Per-size assets for the seller ad (Nov 21 2026): five real new listings, then the real app listing the first one,
# then the end card. Seller-first (Alan 11-21: "put it towards just sellers ... or anyone wanting to sell equipment"),
# so no storefront or founding pitch. Style follows r1-yard-biglogo (ads/storefront-ad on PR #73): the big brand-kit
# wordmark on a white pill top-left, big white captions with a slate outline that pop in on hard cuts, the phone on
# the light stage, the light end card.
# Writes out/<size>/{cap1..5,head1..4,brand-big,stage,phone-mask}.png, endcard.png, phone.json, layout.json,
# and out/9x16-shorts/endcard.png (the end card moved inside the YouTube Shorts safe box).
import os, json, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(D, "source"); FONTS = os.path.join(D, "../parts-ad/source/fonts")
B = lambda s: ImageFont.truetype(os.path.join(FONTS, "SpaceGrotesk_700Bold.ttf"), s)
M = lambda s: ImageFont.truetype(os.path.join(FONTS, "SpaceGrotesk_500Medium.ttf"), s)
WHITE, SLATE, BLUE, GRAY = (255, 255, 255, 255), (26, 51, 83, 255), (37, 99, 235, 255), (84, 84, 86, 255)
WM = os.path.join(D, "../../broll/in/brand-kit/wordmark/yardswaps-wordmark-on-light.png")
W = 1080

# Opener captions: one per real listing photo, in order (the photos are source/photos/1..5).
CAPS = ["Equipment sitting idle?", "Cranes.", "Rollers.", "Racking.", "Packaging machines."]
# Headlines over the phone, one per app segment (build.sh SEGS): what the screen shows at that moment.
HEADS = [("Snap a photo.", SLATE), ("AI writes the listing.", SLATE), ("Set your price.", SLATE), ("Listed free.", BLUE)]

# H, caption font, caption centre y, photo box (x0, y0, x1, y1), logo pill top, glyph height, end-card crop top
SIZES = {"9x16-paid": dict(H=1920, font=124, capY=530, box=(40, 670, 1040, 1500), badgeY=290, glyph=66, cardTop=180, head=70),
         "4x5": dict(H=1350, font=108, capY=1200, box=(40, 196, 1040, 1066), badgeY=48, glyph=74, cardTop=300, head=60)}

def badge(H, y, glyph_h, x=48):
    """The brand-kit wordmark on a white pill with a soft shadow, top-left (same lockup as brand-big.py)."""
    k = glyph_h / 52; pad_x, pad_y = round(34 * k), round(22 * k)
    wm = Image.open(WM).convert("RGBA"); wm = wm.crop(wm.getbbox())
    wm = wm.resize((round(wm.width * glyph_h / wm.height), glyph_h), Image.LANCZOS)
    pw, ph = wm.width + 2 * pad_x, glyph_h + 2 * pad_y
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x, y + 6, x + pw, y + ph + 6), radius=ph // 2, fill=(0, 0, 0, 110))
    layer = Image.alpha_composite(layer, sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(layer).rounded_rectangle((x, y, x + pw, y + ph), radius=ph // 2, fill=WHITE)
    layer.alpha_composite(wm, (x + pad_x, y + pad_y)); return layer, y + ph

def caption(text, size):
    """White Space Grotesk Bold with a slate outline and a soft shadow, shrunk until it fits with side margins."""
    PAD = 48; d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10))); fs = size
    while True:
        F = B(fs); x0, y0, x1, y1 = d0.textbbox((0, 0), text, font=F, stroke_width=10)
        if x1 - x0 + 2 * PAD <= W - 80: break
        fs -= 4
    img = Image.new("RGBA", (x1 - x0 + 2 * PAD, y1 - y0 + 2 * PAD), (0, 0, 0, 0)); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((PAD - x0, PAD - y0 + 6), text, font=F, fill=(0, 0, 0, 150), stroke_width=10, stroke_fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(img).text((PAD - x0, PAD - y0), text, font=F, fill=WHITE, stroke_width=10, stroke_fill=SLATE)
    return img, fs

def endcard_base():
    """endcard-v3 with the seller lines in place of the storefront lines (same geometry as endcard-founding.py)."""
    base = Image.open(os.path.join(SRC, "base/endcard-v3.png")).convert("RGB"); Wb, Hb = base.size; bg = base.getpixel((20, 20))
    SHIFT = 72; im = Image.new("RGB", (Wb, Hb), bg)
    im.paste(base.crop((0, 0, Wb, 790)), (0, 0))                      # wordmark
    im.paste(base.crop((0, 960, Wb, Hb - SHIFT)), (0, 960 + SHIFT))   # badges, url, question pill
    d = ImageDraw.Draw(im)
    def center(text, font, y, fill):
        w = d.textlength(text, font=font); assert w <= 1000, (text, w); d.text(((Wb - w) / 2, y), text, font=font, fill=fill)
    center("List it free.", B(70), 808, SLATE[:3])
    center("AI writes the listing from your photos.", M(40), 904, GRAY[:3])
    center("No selling fee.", M(36), 962, GRAY[:3])
    return im, bg

card, CARD_BG = endcard_base(); card.save(os.path.join(D, "endcard-base.png"))
for key, z in SIZES.items():
    out = os.path.join(D, "out", key); os.makedirs(out, exist_ok=True); H = z["H"]; base = os.path.join(SRC, "base", key)
    lay = dict(z); lay["caps"] = []
    for i, text in enumerate(CAPS, 1):
        img, fs = caption(text, z["font"]); img.save(os.path.join(out, f"cap{i}.png")); lay["caps"].append([text, fs, img.size])
    pill, pill_bottom = badge(H, z["badgeY"], z["glyph"]); pill.save(os.path.join(out, "brand-big.png")); lay["pillBottom"] = pill_bottom
    # phone stage: the storefront stage with its headline removed (everything above the phone repainted in the bg)
    ph = json.load(open(os.path.join(base, "phone.json")))["phone"]; lay["phone"] = ph
    st = Image.open(os.path.join(base, "stage-store.png")).convert("RGB")
    ImageDraw.Draw(st).rectangle((0, 0, W, ph["y"] - 6), fill=st.getpixel((20, 20))); st.save(os.path.join(out, "stage.png"))
    shutil.copy(os.path.join(base, "phone-mask.png"), os.path.join(out, "phone-mask.png"))
    for i, (text, col) in enumerate(HEADS, 1):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); fs = z["head"]
        while d.textlength(text, font=B(fs)) > W - 120: fs -= 2
        w = d.textlength(text, font=B(fs)); top = ph["y"] - 40 - fs * 1.15
        d.text(((W - w) / 2, top), text, font=B(fs), fill=col); img.save(os.path.join(out, f"head{i}.png"))
    top = z["cardTop"]; c = Image.new("RGB", (W, H), CARD_BG); c.paste(card.crop((0, top, W, min(1920, top + H))), (0, 0))
    c.save(os.path.join(out, "endcard.png"))
    json.dump(lay, open(os.path.join(out, "layout.json"), "w"), indent=1); print(key, "ok", [c[1] for c in lay["caps"]])

# YouTube Shorts: the same 9:16 cut with the end card's content scaled into the safe box x 48-888, y 288-1248
# (the box SHORTS-AD.md uses for the storefront Shorts cut; the right rail and the bottom title cover the rest).
nine = Image.open(os.path.join(D, "out/9x16-paid/endcard.png")).convert("RGB")
diff = Image.eval(Image.merge("RGB", [Image.eval(ch, lambda v: v) for ch in nine.split()]), lambda v: v)
mask = Image.new("L", nine.size, 0); px, mp = nine.load(), mask.load()
for y in range(0, nine.height, 2):
    for x in range(0, nine.width, 2):
        if sum(abs(a - b) for a, b in zip(px[x, y], CARD_BG)) > 24: mp[x, y] = 255
bb = mask.getbbox(); content = nine.crop(bb); bw, bh = 840, 960
k = min(bw / content.width, bh / content.height, 0.82); content = content.resize((round(content.width * k), round(content.height * k)), Image.LANCZOS)
sc = Image.new("RGB", nine.size, CARD_BG); sc.paste(content, (48 + (bw - content.width) // 2, 288 + (bh - content.height) // 2))
os.makedirs(os.path.join(D, "out/9x16-shorts"), exist_ok=True); sc.save(os.path.join(D, "out/9x16-shorts/endcard.png"))
print("shorts endcard scale", round(k, 3), "content", bb)
