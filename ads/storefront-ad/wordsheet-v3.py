# Words-vs-screen sheet for the v3 ad. Usage: [WS_TIMES=1,4,8,12] wordsheet-v3.py <final.mp4> <out.jpg>
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
V, OUT = sys.argv[1], sys.argv[2]; D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype(os.path.join(D, "../parts-ad/source/fonts/SpaceGrotesk_500Medium.ttf"), 22)
T = [float(x) for x in os.environ.get("WS_TIMES", "1,4,8,12").split(",")]
rows = [
 (T[0], "Your yard. (+ YardSwaps wordmark, 'AI-generated scene')", "AI-generated scene (Runway Gen-4 from our own prompt): a dealer yard with a row of parked machines, nothing moving but the camera"),
 (T[1], "On one page. (+ wordmark, AI label)", "AI-generated scene: a wheel loader, generator and forklift parked in a yard, slow dolly"),
 (T[2], "Your storefront on YardSwaps.", "Real app (main, Nov 20): Your Equipment Co. storefront, the grapple truck, telehandler and F-350 at the top of the inventory"),
 (T[3], "Open your storefront. / 30 days free, then $49 a month. / What's sitting in your yard right now?", "End card: wordmark, store badges, yardswaps.com"),
]
W, TH = 300, 534; cols = len(rows)
sheet = Image.new("RGB", (cols * (W + 20) + 20, TH + 240), "white"); d = ImageDraw.Draw(sheet)
def wrap(t, maxw):
    out, cur = [], ""
    for w in t.split():
        if d.textlength((cur + " " + w).strip(), font=F) <= maxw: cur = (cur + " " + w).strip()
        else: out.append(cur); cur = w
    return out + [cur]
for i, (t, line, screen) in enumerate(rows):
    fr = f"/tmp/ws3_{i}.jpg"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", V, "-frames:v", "1", fr], check=True)
    im = Image.open(fr); im = im.resize((W, round(W * im.height / im.width))); x = 20 + i * (W + 20); y = 20
    sheet.paste(im, (x, y)); yy = y + TH + 6
    for l in wrap(f"{t:.1f}s  {line}", W): d.text((x, yy), l, font=F, fill=(26, 51, 83)); yy += 26
    for l in wrap(screen, W): d.text((x, yy), l, font=F, fill=(84, 84, 86)); yy += 26
sheet.save(OUT, quality=88); print(OUT)
