# Light end card for "Snap it": the brand-commercial-v2 card (wordmark, store badges, url kept), seller copy per MESSAGING.md
import os, sys
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); FONTS = sys.argv[1]
im = Image.open(os.path.join(D, "endcard-v2-base.png")).convert("RGB")
W, H = im.size; bg = im.getpixel((20, 20)); d = ImageDraw.Draw(im)
B = lambda s: ImageFont.truetype(os.path.join(FONTS, "SpaceGrotesk_700Bold.ttf"), s)
M = lambda s: ImageFont.truetype(os.path.join(FONTS, "SpaceGrotesk_500Medium.ttf"), s)
SLATE, GRAY, BLUE = (26, 51, 83), (84, 84, 86), (37, 99, 235)
d.rectangle((0, 760, W, 972), fill=bg); d.rectangle((0, 1240, W, 1380), fill=bg)
def center(text, font, y, fill):
    w = d.textlength(text, font=font); assert w < W - 80, (text, w); d.text(((W - w) / 2, y), text, font=font, fill=fill)
center("Equipment sitting idle?", B(58), 768, SLATE)
center("List it free.", B(58), 834, BLUE)
center("Snap a photo. The AI writes the listing.", M(36), 908, GRAY)
q = "What's sitting idle in your yard?"; f = B(48); w = d.textlength(q, font=f)
d.rounded_rectangle(((W - w) / 2 - 44, 1262, (W + w) / 2 + 44, 1360), radius=49, fill=BLUE)
d.text(((W - w) / 2, 1284), q, font=f, fill=(255, 255, 255))
im.save(sys.argv[2]); print("endcard", im.size)
