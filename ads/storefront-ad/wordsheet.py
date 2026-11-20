# Words-vs-screen sheet (MOTION.md rule, Nov 15). Usage: wordsheet.py <final.mp4> <out.jpg> [captions]
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
V, OUT = sys.argv[1], sys.argv[2]; CAP = len(sys.argv) > 3; D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "../parts-ad/source/fonts/SpaceGrotesk_500Medium.ttf"), 22)
rows = [
 (2.0, "Your yard.", "Real photo: 2007 Freightliner M2 grapple truck parked in a gravel dealer yard, whole truck in frame, nothing moving"),
 (5.9, "On one page.", "Real photo: 2014 SkyTrak 6042 telehandler parked in the yard, whole machine in frame"),
 (9.6, "Every unit, one link.", "Real photo: 2019 Ford F-350 SuperCab service truck parked, whole truck in frame"),
 (14.0, "Your storefront on YardSwaps.", "Real app (main, Nov 20): Your Equipment Co. storefront, the same grapple truck, telehandler and F-350 at the top of the inventory"),
 (19.6, "30 days free. Then $49 a month.", "Real app: Choose a plan, Dealer card: $49/mo, First 30 days free for new dealers, Featured in YardSwaps social posts, Start free trial"),
 (23.6, "Open your storefront. / 30 days free, then $49 a month. Listing is free. / What's sitting in your yard right now?", "End card: wordmark, store badges, yardswaps.com"),
]
W, TH = 300, 534; cols = len(rows)
sheet = Image.new("RGB", (cols * (W + 20) + 20, TH + 220), "white"); d = ImageDraw.Draw(sheet)
def wrap(t, maxw):
    out, cur = [], ""
    for w in t.split():
        if d.textlength((cur + " " + w).strip(), font=F) <= maxw: cur = (cur + " " + w).strip()
        else: out.append(cur); cur = w
    return out + [cur]
for i, (t, line, screen) in enumerate(rows):
    fr = f"/tmp/ws_{i}.jpg"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", V, "-frames:v", "1", fr], check=True)
    im = Image.open(fr).resize((W, TH)); x = 20 + i * (W + 20); y = 20
    sheet.paste(im, (x, y)); yy = y + TH + 6
    for l in wrap(f"{t:.1f}s  {line}", W): d.text((x, yy), l, font=F, fill=(26, 51, 83)); yy += 26
    for l in wrap(screen, W): d.text((x, yy), l, font=F, fill=(84, 84, 86)); yy += 26
sheet.save(OUT, quality=88); print(OUT)
