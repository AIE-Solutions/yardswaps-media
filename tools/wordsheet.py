#!/usr/bin/env python3
"""Words-vs-screen sheet for any clip (MOTION.md rule: every on-screen line next to the frame it plays over).

Usage:
    python3 tools/wordsheet.py <clip.mp4> <out.jpg> [--every 2.0] [--json out.json]

Takes a frame every --every seconds (plus the last second, so the end card is always on the sheet), reads the words on
each frame with tesseract, and lays the frames out with their time and the words read. The words column is a machine
read: a person (or agent) still looks at every frame and writes what the screen shows in the audit note. Nothing here
calls a paid service.
"""
import argparse, json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT = os.path.join(ROOT, "ads/parts-ad/source/fonts/SpaceGrotesk_500Medium.ttf")


def duration(v):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def grab(v, t, path):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", v, "-frames:v", "1", path], check=True)
    return Image.open(path).convert("RGB")


def read_words(im):
    try:
        import pytesseract
    except ImportError:
        return ""
    g = ImageOps.grayscale(im)
    txt = pytesseract.image_to_string(g, config="--psm 11")
    words = [w for w in txt.split() if sum(c.isalnum() for c in w) >= 2]
    return " ".join(words)[:220]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip"); ap.add_argument("out")
    ap.add_argument("--every", type=float, default=2.0)
    ap.add_argument("--json")
    a = ap.parse_args()
    dur = duration(a.clip)
    times, t = [], 0.6
    while t < dur - 0.8:
        times.append(round(t, 1)); t += a.every
    times.append(round(max(dur - 0.4, 0), 1))
    W, TH, cols = 216, 384, 6
    font = ImageFont.truetype(FONT, 15)
    rows_n = (len(times) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W + 14) + 14, rows_n * (TH + 132) + 44), "white")
    d = ImageDraw.Draw(sheet)
    d.text((14, 12), f"{os.path.basename(a.clip)}  ({dur:.1f} s)", font=font, fill=(26, 51, 83))

    def wrap(s, maxw):
        out, cur = [], ""
        for w in s.split():
            if d.textlength((cur + " " + w).strip(), font=font) <= maxw:
                cur = (cur + " " + w).strip()
            else:
                out.append(cur); cur = w
        return out + [cur]

    rec = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, t in enumerate(times):
            im = grab(a.clip, t, os.path.join(tmp, f"f{i}.png"))
            words = read_words(im)
            rec.append({"t": t, "words": words})
            x = 14 + (i % cols) * (W + 14); y = 40 + (i // cols) * (TH + 132)
            sheet.paste(im.resize((W, TH)), (x, y))
            yy = y + TH + 4
            d.text((x, yy), f"{t:.1f} s", font=font, fill=(37, 99, 235)); yy += 18
            for ln in wrap(words or "(no words)", W)[:6]:
                d.text((x, yy), ln, font=font, fill=(84, 84, 86)); yy += 18
    sheet.save(a.out, quality=72, optimize=True)
    if a.json:
        json.dump({"clip": a.clip, "seconds": round(dur, 1), "frames": rec}, open(a.json, "w"), indent=1)
    print(a.out)


if __name__ == "__main__":
    sys.exit(main())
