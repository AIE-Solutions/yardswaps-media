# Words-vs-screen sheet (MOTION.md rule, Nov 15). Usage: wordsheet.py <final.mp4> <out.jpg> [captions]
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
V, OUT = sys.argv[1], sys.argv[2]; CAP = len(sys.argv) > 3; D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "../parts-ad/source/fonts/SpaceGrotesk_500Medium.ttf"), 22)
rows = [
 (2.0, "Parked for the night." if CAP else "(no text)", "Graded real photo: Peterbilt 379, whole truck in frame, dusk, nothing moving"),
 (6.3, "Waiting on its next machine." if CAP else "(no text)", "Graded real photo: Komatsu engine on a stand in a parts warehouse, whole engine in frame"),
 (10.6, "Every size in the box." if CAP else "(no text)", "Graded real photo: open micrometer case, whole case in frame"),
 (14.8, "Lights off? List it free. / The app writes the listing. No cut of the sale. / What stays after the lights go off?", "End card: wordmark, store badges, yardswaps.com"),
]
W, TH = 300, 534; cols = 4
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
