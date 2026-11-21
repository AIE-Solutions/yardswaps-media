# Words-vs-screen sheet for the viral-format ad. Usage: wordsheet-viral.py <final.mp4> <out.jpg>
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
V, OUT = sys.argv[1], sys.argv[2]; D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "../parts-ad/source/fonts/SpaceGrotesk_500Medium.ttf"), 20)
rows = [
 (0.6, "Your whole yard. (+ logo pill top-left, 'AI-generated scene')", "AI-generated scene (Runway Gen-4, our prompt): dealer yard, parked machines, slow push"),
 (1.9, "One page. (+ logo pill, AI label)", "AI-generated scene: wheel loader, forklift, generator, slow push"),
 (2.9, "Every unit. (+ logo pill)", "Real listing photo animated by Runway (grapple truck, idle), whole truck in frame"),
 (3.9, "Your hours. (+ logo pill)", "Real listing photo animated by Runway (telehandler, idle)"),
 (4.9, "Your links. (+ logo pill)", "Real listing photo animated by Runway (F-350 service truck, idle)"),
 (7.5, "Your storefront on YardSwaps.", "Real app (main, Nov 20): demo storefront, city-neutral, scrolls to the real units and prices"),
 (10.8, "Open your storefront. / 30 days free, then $49 a month. / What's sitting in your yard right now?", "End card: wordmark, store badges, yardswaps.com"),
]
W, TH = 240, 427; cols = len(rows)
sheet = Image.new("RGB", (cols * (W + 16) + 16, TH + 250), "white"); d = ImageDraw.Draw(sheet)
def wrap(t, maxw):
    out, cur = [], ""
    for w in t.split():
        if d.textlength((cur + " " + w).strip(), font=F) <= maxw: cur = (cur + " " + w).strip()
        else: out.append(cur); cur = w
    return out + [cur]
for i, (t, line, screen) in enumerate(rows):
    fr = f"/tmp/wsv_{i}.jpg"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", V, "-frames:v", "1", fr], check=True)
    im = Image.open(fr); im = im.resize((W, round(W * im.height / im.width))); x = 16 + i * (W + 16); y = 16
    sheet.paste(im, (x, y)); yy = y + TH + 6
    for l in wrap(f"{t:.1f}s  {line}", W): d.text((x, yy), l, font=F, fill=(26, 51, 83)); yy += 24
    for l in wrap(screen, W): d.text((x, yy), l, font=F, fill=(84, 84, 86)); yy += 24
sheet.save(OUT, quality=88); print(OUT)
