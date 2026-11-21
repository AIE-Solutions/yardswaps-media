# Words-vs-screen sheet: every on-screen line next to the frame it plays over (MOTION.md rule, Nov 15). Usage: wordsheet.py <final.mp4> <out.jpg>
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
V, OUT = sys.argv[1], sys.argv[2]; D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "fonts/SpaceGrotesk_500Medium.ttf"), 22)
rows = [  # (time, line as written, what is on screen)
 (0.5, "Equipment sitting idle?", "Phone camera screen: the real listing photo of a Hotsy hot-water pressure washer, whole machine in the viewfinder, soft focus"),
 (1.5, "Equipment sitting idle? / Snap one photo.", "Focus tap on the machine, the photo sharpens"),
 (2.45, "Snap one photo.", "Shutter: flash, the thumbnail fills with the photo"),
 (3.5, "(no words)", "Pull back: the camera screen is the screen of the phone"),
 (5.3, "AI fills it. Title. Category. (app)", "Real app: title 'Hot Water Pressure Washer, 3,000 psi, Elec...' and category Pressure Washers filled by AI"),
 (6.6, "AI wrote it. Condition, PSI. (app)", "Real app: condition and PSI filled, description written"),
 (7.9, "Tap once. Price set. (app)", "Real app: suggested price $1,600-$2,800, Use price tapped"),
 (9.3, "Published. Listed free. (app)", "Real app: 'Your listing is live!' modal"),
 (11.0, "One photo. No typing. Listed free. (app)", "Real app: live modal, the same photo as a card"),
 (13.5, "Equipment sitting idle? List it free. / Snap a photo. The AI writes the listing. / What's sitting idle in your yard?", "End card: wordmark, store badges, yardswaps.com"),
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
