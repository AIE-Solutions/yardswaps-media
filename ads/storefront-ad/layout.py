# Per-size assets for the storefront ad: 9x16 (Reels, Stories, Shorts, TikTok, Meta vertical placements), 4x5 (feed)
# and 1x1. Each size gets its caption cards (lower-left, Space Grotesk Bold with the blue bar), the two phone stages,
# the phone mask, the end card (the 9x16 card cropped) and phone.json with the band and phone geometry build.sh reads.
# Text stays inside Meta's vertical safe zone (top 250 px and bottom 340 px of 1080x1920 can sit under the ad UI).
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(D, "../parts-ad/source")
B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
BG, SLATE, BLUE = (246, 246, 248), (26, 51, 83), (37, 99, 235)
LINES = {"c1": "Your yard.", "c2": "On one page.", "c3": "Every unit,|one link."}
STAGES = {"store": ["Your storefront", "on YardSwaps."], "plans": ["30 days free.", "Then $49 a month."]}
# H, band y (band is 1080x810 from the 4:3 stills), caption font/line height/bottom, stage font/top, phone x y w h, end card crop top
SIZES = {
 "9x16": dict(H=1920, bandY=300, cap=(88, 100, 1560), stage=(64, 250), phone=(210, 430, 660, 1307), cardTop=0),
 "4x5":  dict(H=1350, bandY=210, cap=(80, 92, 1250), stage=(56, 60), phone=(280, 240, 520, 1030), cardTop=300),
 "1x1":  dict(H=1080, bandY=20,  cap=(72, 84, 1056), stage=(52, 50), phone=(330, 210, 420, 832), cardTop=440),
 # Paid Meta placements (Reels, Stories, Feed vertical): text between 15 and 62 percent of the height, so the captions sit
 # on the band's lower left (over the gradient) and the end card's content is shifted up 180 px.
 "9x16-paid": dict(H=1920, bandY=300, cap=(88, 100, 1090), stage=(64, 300), phone=(220, 480, 640, 1267), cardTop=180),
}
W = 1080
for key, z in SIZES.items():
    H = z["H"]; out = os.path.join(D, "r" + key); os.makedirs(out, exist_ok=True)
    fs, LH, BOTTOM = z["cap"]; F = B(fs); X = 84
    for k, text in LINES.items():
        g = Image.new("L", (1, H), 0); g0 = BOTTOM - 510
        for y in range(H): g.putpixel((0, y), 0 if y < g0 else min(150, int(150 * ((y - g0) / 600) ** 1.4)))
        img = Image.composite(Image.new("RGBA", (W, H), (8, 14, 24, 255)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), g.resize((W, H)))
        d = ImageDraw.Draw(img); ls = text.split("|")
        assert all(d.textlength(l, font=F) <= 912 for l in ls), (key, k)
        top = BOTTOM - LH * len(ls)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        for i, l in enumerate(ls): sd.text((X, top + i * LH), l, font=F, fill=(0, 0, 0, 170))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(img)
        d.rounded_rectangle((X, top - 40, X + 84, top - 28), radius=6, fill=BLUE + (255,))
        for i, l in enumerate(ls): d.text((X, top + i * LH), l, font=F, fill=(255, 255, 255, 255))
        img.save(os.path.join(out, k + ".png"))
    sf, st = z["stage"]; px, py, pw, ph = z["phone"]; rad = round(pw * 0.086)
    for name, lines in STAGES.items():
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im); f = B(sf)
        for i, l in enumerate(lines):
            w = d.textlength(l, font=f); assert w <= 960, (key, l)
            d.text(((W - w) / 2, st + i * round(sf * 1.19)), l, font=f, fill=SLATE if i == 0 else BLUE)
        d.rounded_rectangle((px - 12, py - 12, px + pw + 12, py + ph + 12), radius=rad + 12, fill=SLATE)
        im.save(os.path.join(out, f"stage-{name}.png"))
    m = Image.new("L", (pw, ph), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pw - 1, ph - 1), radius=rad, fill=255)
    m.save(os.path.join(out, "phone-mask.png"))
    base = Image.open(os.path.join(D, "endcard.png")).convert("RGB")
    card = Image.new("RGB", (W, H), BG); card.paste(base.crop((0, z["cardTop"], W, min(1920, z["cardTop"] + H))), (0, 0)); card.save(os.path.join(out, "endcard.png"))
    json.dump(dict(W=W, H=H, bandY=z["bandY"], phone=dict(x=px, y=py, w=pw, h=ph)), open(os.path.join(out, "phone.json"), "w"))
    print(key, "ok")
