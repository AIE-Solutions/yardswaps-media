# Founding-price end card (11-20): the viral4 card (endcard-v3.png) with the founding offer on screen.
# Claims checked on main 11-20: first-time storefronts get 30 days free, then FOUNDINGDEALER = $20 off x 3 paid months
# ($29/mo), capped at the first 100 storefronts (PR #421), then $49/mo. Writes endcard-founding.png (base, 1080x1920)
# and vr-<ratio>/endcard-founding.png cropped like layout-v3.py. The older cards are left as they were.
import os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(D, "../parts-ad/source")
B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
M = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_500Medium.ttf"), s)
SLATE, GRAY, BLUE, BLUE_LIGHT = (26, 51, 83), (84, 84, 86), (37, 99, 235), (226, 235, 253)
SHIFT = 72  # the badges, url and question move down to make room for the second offer line

base = Image.open(os.path.join(D, "endcard-v3.png")).convert("RGB"); W, H = base.size; bg = base.getpixel((20, 20))
im = Image.new("RGB", (W, H), bg)
im.paste(base.crop((0, 0, W, 790)), (0, 0))                     # wordmark, unchanged (headline is redrawn below)
im.paste(base.crop((0, 960, W, H - SHIFT)), (0, 960 + SHIFT))    # badges, url, question pill, shifted down
d = ImageDraw.Draw(im)

def center(text, font, y, fill):
    w = d.textlength(text, font=font); assert w <= 1000, (text, w); d.text(((W - w) / 2, y), text, font=font, fill=fill)

# "FOUNDING PRICE" pill between the wordmark and the headline
t = "FOUNDING PRICE"; f = B(30); sp = 3
tw = sum(d.textlength(c, font=f) for c in t) + sp * (len(t) - 1); ph, px = 50, 26; y0 = 752
x0 = (W - tw) / 2 - px
d.rounded_rectangle((x0, y0, x0 + tw + 2 * px, y0 + ph), radius=ph // 2, fill=BLUE_LIGHT)
x = (W - tw) / 2
for c in t:
    d.text((x, y0 + 8), c, font=f, fill=BLUE); x += d.textlength(c, font=f) + sp

center("Open your storefront.", B(62), 826, SLATE)
center("30 days free, then $29 a month for 3 months.", M(40), 912, GRAY)
center("First 100 storefronts. Then $49 a month.", M(34), 970, GRAY)
im.save(os.path.join(D, "endcard-founding.png"))

for key, top, h in (("9x16-paid", 180, 1920), ("4x5", 300, 1350), ("1x1", 440, 1080)):
    card = Image.new("RGB", (W, h), bg); card.paste(im.crop((0, top, W, min(1920, top + h))), (0, 0))
    card.save(os.path.join(D, "vr-" + key, "endcard-founding.png")); print(key, card.size)
