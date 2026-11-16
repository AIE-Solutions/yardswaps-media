# Light end card: the brand-commercial-v2 card with the text swapped (wordmark, badges, url kept as they were)
import os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(D, "endcard-v2-base.png")).convert("RGB")
W, H = im.size; bg = im.getpixel((20, 20)); d = ImageDraw.Draw(im)
B = lambda s: ImageFont.truetype(os.path.join(D, "fonts/SpaceGrotesk_700Bold.ttf"), s)
M = lambda s: ImageFont.truetype(os.path.join(D, "fonts/SpaceGrotesk_500Medium.ttf"), s)
SLATE, GRAY, BLUE = (26, 51, 83), (84, 84, 86), (37, 99, 235)
# wipe headline + subline (y 800-960) and the question pill (y 1250-1370)
d.rectangle((0, 790, W, 965), fill=bg); d.rectangle((0, 1240, W, 1380), fill=bg)
def center(text, font, y, fill):
    w = d.textlength(text, font=font); d.text(((W - w) / 2, y), text, font=font, fill=fill)
center("Snap the part. List it free.", B(62), 820, SLATE)
center("The app writes the listing. No cut of the sale.", M(40), 898, GRAY)
q = "What's the oldest part still on your shelf?"; f = B(50); w = d.textlength(q, font=f)
x0 = (W - w) / 2 - 40
d.rounded_rectangle((x0, 1258, x0 + w + 80, 1362), radius=26, fill=BLUE)
d.text(((W - w) / 2, 1282), q, font=f, fill=(255, 255, 255))
im.save(os.path.join(D, "endcard.png")); print("endcard", im.size)
