# Cuts the real app recording (Expo web build of apps/mobile, mock API, the Cat 950G listing photo uploaded through
# "Choose from Library", recording/recsell.js) into the four phone segments, at 30 fps, and writes
# source/app-seller.mp4 plus source/app-seller.json (segment start times in the output, for the headlines and taps).
# Usage: python3 apprec.py <frame dir with 0000.jpg.. and taps.json>
import os, sys, json, subprocess, tempfile
D = os.path.dirname(os.path.abspath(__file__)); RAW = sys.argv[1]
# (first source frame, last source frame, speed, headline index): source frames are 30 fps
SEGS = [(40, 190, 3.0, 1),     # Choose from Library, the loader photo lands, AI starts reading it
        (190, 430, 3.5, 2),    # AI fills title, category, condition; the form scrolls through what it wrote
        (830, 905, 1.5, 3),    # tap "Use price": $52,000 goes in
        (1114, 1171, 1.0, 4)]  # just after the "Publish listing" tap: "Your listing is live!" (starts after the boost prices leave)
taps = [t["f"] for t in json.load(open(os.path.join(RAW, "taps.json")))]
tmp = tempfile.mkdtemp(); n = 0; meta = {"segs": [], "taps": []}
for a, b, sp, h in SEGS:
    meta["segs"].append({"t": round(n / 30, 3), "head": h, "src": [a, b], "speed": sp})
    k = 0.0
    while a + k <= b:
        src = a + int(round(k))
        for t in taps:
            if src <= t < src + sp and t >= a: meta["taps"].append(round(n / 30, 3))
        os.symlink(os.path.join(RAW, "%04d.jpg" % src), os.path.join(tmp, "%04d.jpg" % n)); n += 1; k += sp
meta["dur"] = round(n / 30, 3)
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "30", "-i", os.path.join(tmp, "%04d.jpg"),
                "-vf", "scale=1178:2334,format=yuv420p", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
                os.path.join(D, "source/app-seller.mp4")], check=True)
json.dump(meta, open(os.path.join(D, "source/app-seller.json"), "w"), indent=1); print(meta)
