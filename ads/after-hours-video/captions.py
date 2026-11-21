# Caption cards for "After hours" (optional variant; the reference look has no text on the image): 1080x1920 RGBA, lower-left, Space Grotesk Bold 88 (same as brand-commercial-v2)
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "../parts-ad/source/fonts/SpaceGrotesk_700Bold.ttf"), 88)
W, H, X, LH, BOTTOM = 1080, 1920, 84, 100, 1560
BLUE = (37, 99, 235, 255)
lines = {
 "c1": "Parked for|the night.",
 "c2": "Waiting on its|next machine.",
 "c3": "Every size|in the box.",
}
for k, text in lines.items():
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        g.putpixel((0, y), 0 if y < 1050 else min(150, int(150 * ((y - 1050) / 600) ** 1.4)))
    g = g.resize((W, H))
    img = Image.composite(Image.new("RGBA", (W, H), (8, 14, 24, 255)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), g)
    d = ImageDraw.Draw(img)
    ls = text.split("|")
    assert all(d.textlength(l, font=F) <= 912 for l in ls), (k, [d.textlength(l, font=F) for l in ls])
    top = BOTTOM - LH * len(ls)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for i, l in enumerate(ls): sd.text((X, top + i * LH), l, font=F, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(img)
    d.rounded_rectangle((X, top - 40, X + 84, top - 28), radius=6, fill=BLUE)
    for i, l in enumerate(ls): d.text((X, top + i * LH), l, font=F, fill=(255, 255, 255, 255))
    img.save(os.path.join(D, k + ".png")); print(k, ls)
