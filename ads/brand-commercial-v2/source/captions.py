# Caption cards for "Every shop has one" v2: 1080x1920 RGBA, lower-left, Space Grotesk Bold
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "fonts/SpaceGrotesk_700Bold.ttf"), 88)
W, H, X, MAXW, LH, BOTTOM = 1080, 1920, 84, 860, 100, 1560
BLUE = (37, 99, 235, 255)
lines = {
 "t1": "Every shop has one.",
 "t2": "The fryer from|the old menu.",
 "t3": "The backup|for the backup.",
 "t4": "The welder that|became a shelf.",
 "t5": "The washer the|bigger one replaced.",
 "t6": "Someone close by|needed it.",
 "t7": "You get the|space back.",
 "t8": "And extra cash flow|for the business.",
}
def wrap(text, d):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=F) <= MAXW: cur = t
        else: out.append(cur); cur = w
    out.append(cur); return out
for k, text in lines.items():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # bottom gradient for legibility
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        a = 0 if y < 1050 else min(150, int(150 * ((y - 1050) / 600) ** 1.4))
        g.putpixel((0, y), a)
    img.putalpha(g.resize((W, H)))
    img = Image.composite(Image.new("RGBA", (W, H), (8, 14, 24, 255)), Image.new("RGBA", (W, H), (0,0,0,0)), g.resize((W, H)))
    d = ImageDraw.Draw(img)
    ls = text.split("|")
    assert all(d.textlength(l, font=F) <= 912 for l in ls), (k, [d.textlength(l, font=F) for l in ls])
    top = BOTTOM - LH * len(ls)
    # soft shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for i, l in enumerate(ls): sd.text((X, top + i * LH), l, font=F, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, sh); d = ImageDraw.Draw(img)
    d.rounded_rectangle((X, top - 40, X + 84, top - 28), radius=6, fill=BLUE)
    for i, l in enumerate(ls): d.text((X, top + i * LH), l, font=F, fill=(255, 255, 255, 255))
    img.save(os.path.join(D, k + ".png"))
    print(k, ls)
