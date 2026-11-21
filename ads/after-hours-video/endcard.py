# Light end card for "After hours": the brand-commercial-v2 card with the text swapped (wordmark, badges, url kept)
import os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(D, "../parts-ad/source")
im = Image.open(os.path.join(S, "endcard-v2-base.png")).convert("RGB")
W, H = im.size; bg = im.getpixel((20, 20)); d = ImageDraw.Draw(im)
B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
M = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_500Medium.ttf"), s)
SLATE, GRAY, BLUE = (26, 51, 83), (84, 84, 86), (37, 99, 235)
d.rectangle((0, 790, W, 965), fill=bg); d.rectangle((0, 1240, W, 1380), fill=bg)
def center(text, font, y, fill):
    w = d.textlength(text, font=font); assert w <= 1000, (text, w); d.text(((W - w) / 2, y), text, font=font, fill=fill)
center("Lights off? List it free.", B(62), 820, SLATE)
center("The app writes the listing. No cut of the sale.", M(40), 898, GRAY)
q = "What stays after the lights go off?"; f = B(50); w = d.textlength(q, font=f); assert w + 80 <= 1040, w
x0 = (W - w) / 2 - 40
d.rounded_rectangle((x0, 1258, x0 + w + 80, 1362), radius=26, fill=BLUE)
d.text(((W - w) / 2, 1282), q, font=f, fill=(255, 255, 255))
im.save(os.path.join(D, "endcard.png")); print("endcard", im.size)
