# Words-vs-screen sheet: every on-screen line next to the frame it plays over (MOTION.md rule, Nov 15). Usage: wordsheet.py <final.mp4> <out.jpg>
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
V, OUT = sys.argv[1], sys.argv[2]; D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "fonts/SpaceGrotesk_500Medium.ttf"), 22)
rows = [  # (time, line as written, what is on screen)
 (1.6, "The pallet nobody touched all year.", "Real photo: pallet of wrapped Eaton hydraulic cylinders, part labels on; whole pallet in frame"),
 (4.7, "The mic set still in its case.", "Real photo: open wooden micrometer case on a bench, whole case in frame"),
 (7.6, "The sprayer parked all season.", "Real photo: spray trailer parked by a wall, whole trailer in frame"),
 (9.1, "Surplus pallet? Snap it, labels up. (app)", "Real app: New listing with the same cylinders photo just taken"),
 (10.6, "AI fills it. Title. Category. (app)", "Real app: title 'Loader Hydraulic Cylinder Lot, Surplus...' and category filled by AI"),
 (12.2, "AI wrote it. Condition, count. (app)", "Real app: condition New (Surplus), count 8, description filled"),
 (13.6, "Tap once. Price set. (app)", "Real app: price 1250 typed, suggested range shown"),
 (15.5, "Published. Listed free. (app)", "Real app: 'Your listing is live!' modal"),
 (16.9, "One photo. No typing. Listed free. (app)", "Real app: live modal, the cylinders photo card 'On the pallet'"),
 (20.0, "Snap the part. List it free. / What's the oldest part still on your shelf?", "End card: wordmark, store badges, yardswaps.com"),
]
W, TH = 300, 534; cols = 5; rws = (len(rows) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (W + 20) + 20, rws * (TH + 200) + 20), "white"); d = ImageDraw.Draw(sheet)
def wrap(t, maxw):
    out, cur = [], ""
    for w in t.split():
        if d.textlength((cur + " " + w).strip(), font=F) <= maxw: cur = (cur + " " + w).strip()
        else: out.append(cur); cur = w
    return out + [cur]
for i, (t, line, screen) in enumerate(rows):
    fr = f"/tmp/ws_{i}.jpg"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", V, "-frames:v", "1", fr], check=True)
    im = Image.open(fr).resize((W, TH)); x = 20 + (i % cols) * (W + 20); y = 20 + (i // cols) * (TH + 200)
    sheet.paste(im, (x, y)); yy = y + TH + 6
    for l in wrap(f"{t:.1f}s  {line}", W): d.text((x, yy), l, font=F, fill=(26, 51, 83)); yy += 26
    for l in wrap(screen, W): d.text((x, yy), l, font=F, fill=(84, 84, 86)); yy += 26
sheet.save(OUT, quality=88); print(OUT)
