# Words-vs-screen sheet: the frame at the start, middle and end of every line, with the line printed under it.
# Usage: python3 wordsheet.py <mp4> <out.jpg>
import sys, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); V, OUT = sys.argv[1], sys.argv[2]
DUR = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",V],capture_output=True,text=True).stdout)
m = json.load(open(os.path.join(D, "source/app-seller.json"))); P0 = DUR - m["dur"] - 2.6  # phone start, from the real file
caps = ["Equipment sitting idle?", "Cranes.", "Rollers.", "Racking.", "Packaging machines."]
heads = ["Snap a photo.", "AI writes the listing.", "Set your price.", "Listed free."]
F1 = 1 / 30; a1, a2 = 1.5 - F1, 1.0 - F1  # each looped-still shot comes out one frame short
spans = [(0, a1, caps[0])] + [(a1 + i * a2, a1 + (i + 1) * a2, caps[i + 1]) for i in range(4)]
st = [s["t"] for s in m["segs"]] + [m["dur"]]
spans += [(P0 + st[i], P0 + st[i + 1], heads[i]) for i in range(4)]
spans += [(P0 + m["dur"], P0 + m["dur"] + 2.6, "End card: List it free. AI writes the listing from your photos. No selling fee.")]
F = ImageFont.truetype(os.path.join(D, "../parts-ad/source/fonts/SpaceGrotesk_500Medium.ttf"), 18)
TW, TH = 240, 427; S = Image.new("RGB", (3 * TW + 260, len(spans) * (TH + 6)), "white"); d = ImageDraw.Draw(S)
for r, (a, b, text) in enumerate(spans):
    for c, t in enumerate((a + 0.08, (a + b) / 2, min(b, DUR) - 0.1)):
        f = f"/tmp/ws_{r}_{c}.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", V, "-frames:v", "1", "-vf", f"scale={TW}:-2", f], check=True)
        im = Image.open(f).convert("RGB"); S.paste(im.crop((0, 0, TW, min(TH, im.height))), (c * TW, r * (TH + 6)))
        d.text((c * TW + 4, r * (TH + 6) + 4), f"{t:.2f}s", fill="red", font=F)
    y = r * (TH + 6) + 20; words = text.split(); line = ""
    for w in words:
        if d.textlength(line + " " + w, font=F) > 245: d.text((3 * TW + 10, y), line.strip(), fill="black", font=F); y += 24; line = ""
        line += " " + w
    d.text((3 * TW + 10, y), line.strip(), fill="black", font=F)
S.save(OUT, quality=80); print(OUT, S.size)
