# Phone stage for the app part: 1080x1920 light-gray background with a slate headline above a big phone
# (the recording at 740x1466 with rounded corners), plus the alpha mask the build applies to the recording.
import os, sys
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(D, "../parts-ad/source")
B = lambda s: ImageFont.truetype(os.path.join(S, "fonts/SpaceGrotesk_700Bold.ttf"), s)
W, H = 1080, 1920; PW, PH, PX, PY, RAD = 740, 1466, 170, 330, 64
BG, SLATE, BLUE = (246, 246, 248), (26, 51, 83), (37, 99, 235)
def stage(key, lines):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    f = B(64); y = 118
    for i, l in enumerate(lines):
        w = d.textlength(l, font=f); assert w <= 960, (l, w)
        d.text(((W - w) / 2, y + i * 76), l, font=f, fill=SLATE if i == 0 else BLUE)
    d.rounded_rectangle((PX - 14, PY - 14, PX + PW + 14, PY + PH + 14), radius=RAD + 14, fill=SLATE)
    im.save(os.path.join(D, f"stage-{key}.png"))
stage("store", ["Your storefront", "on YardSwaps."])
stage("plans", ["30 days free.", "Then $49 a month."])
m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), radius=RAD, fill=255)
m.save(os.path.join(D, "phone-mask.png")); print("stages", PW, PH, PX, PY)
