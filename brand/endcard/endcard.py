#!/usr/bin/env python3
"""Every YardSwaps video ends on the YardSwaps end card (Alan, 2026-11-25).

The card is the blue one the motion clips already end on: the YardSwaps wordmark, two lines,
the App Store and Google Play badges and the link (card.html, rendered by render.js into
endcard-<audience>-<ratio>.png). Two versions, by the clip's audience:
  seller  "Add a photo. AI fills in the rest." / "Free to list. No cut of the sale." / yardswaps.com
  dealer  "Open your storefront." / "30 days free, then the founding price." / yardswaps.com/s
          (storefront clips never say free to list, MESSAGING.md)
On screen for CARD_SECONDS (2 s; Alan: no more than about 2 s on Shorts).

    python3 brand/endcard/endcard.py fix [--dry]   check every clip in reels/library.json and
        youtube/queue.json; a clip that already ends on the right card for 1-2.6 s is only marked;
        any other clip gets its ending cut (a light or blue card, if any) and the card added for
        2 s, music faded under it. Marks each entry "endcard": "<audience>-v1".
    python3 brand/endcard/endcard.py add IN.mp4 OUT.mp4 [seller|dealer]   one file (ads, long videos)
    python3 brand/endcard/endcard.py check FILE.mp4 ...                    print the card length found

The Reels, TikTok and Shorts posters only post entries marked "endcard", so a clip without the
card never goes out. listings/listing_reels.py runs fix after every build (listings workflow,
9:10 am Central), which also marks clips other pipelines add. Needs ffmpeg, Pillow and NumPy.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LIBRARY = os.path.join(ROOT, "reels", "library.json")
QUEUE = os.path.join(ROOT, "youtube", "queue.json")
VERSION = "v1"
CARD_SECONDS = 2.0
KEEP_MIN, KEEP_MAX = 1.0, 3.1          # an existing blue card this long stays as it is (the motion clips' 3 s)
RATIOS = {"9x16": 9 / 16, "4x5": 4 / 5, "1x1": 1.0, "16x9": 16 / 9}
SCAN_FPS = 10


def audience_of(entry):
    return "dealer" if (entry or {}).get("audience") == "dealer" else "seller"


def card_png(audience, w, h):
    ratio = min(RATIOS, key=lambda r: abs(RATIOS[r] - w / h))
    return os.path.join(HERE, f"endcard-{audience}-{ratio}.png")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height",
                          "-show_entries", "format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in j["streams"])
    return v["width"], v["height"], float(j["format"]["duration"]), has_audio


def _frames(path):
    import numpy as np
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={SCAN_FPS},scale=54:96",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, 96, 54, 3).astype(int)


def tail(path, with_dip=False):
    """(kind, seconds) of the card at the end: kind is "blue", "light" or None."""
    a = _frames(path)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    blue = ((b > 170) & (r < 110) & (g > 60) & (g < 150)).mean(axis=(1, 2))
    # a light card (older cuts) only counts while the picture holds still, so a light UI scene isn't cut
    still = abs(a - a[-1]).mean(axis=(1, 2, 3)) < 4
    light = ((r > 228) & (g > 228) & (b > 228)).mean(axis=(1, 2)) * still
    for kind, frac in (("blue", blue), ("light", light)):
        i = len(frac)
        while i > 0 and frac[i - 1] > 0.55:
            i -= 1
        if len(frac) - i >= 3:
            if with_dip:      # the dip or flash into the old card (up to 0.5 s) goes too
                ref, j = a[-1].mean(), i
                while j > 0 and i - j < 5 and a[j - 1].mean() < 0.85 * ref:
                    j -= 1
                if j < i and (j == 0 or a[j - 1].mean() >= 0.85 * ref):
                    i = j
            return kind, round((len(frac) - i) / SCAN_FPS, 2)
    return None, 0.0


def add(src, dst, audience="seller", seconds=CARD_SECONDS):
    """Write dst = src without any card at its end, then the YardSwaps card for `seconds`.
    A seller clip that already ends on the blue card, only too long, keeps its own card (with its
    question) cut to `seconds`."""
    w, h, dur, has_audio = probe(src)
    kind, card = tail(src)
    if kind == "blue" and audience == "seller":
        return trim(src, dst, dur - card + seconds, has_audio)
    kind, card = tail(src, with_dip=True)
    cut = max(0.5, dur - card) if kind else dur
    total = cut + seconds
    png = card_png(audience, w, h)
    fd, tmp = tempfile.mkstemp(suffix=".mp4", dir=os.path.dirname(os.path.abspath(dst)))
    os.close(fd)
    f = [f"[0:v]trim=0:{cut:.3f},setpts=PTS-STARTPTS,fps=30,scale={w}:{h},setsar=1[a]",
         f"[1:v]scale={w}:{h},fps=30,setsar=1,trim=0:{seconds},setpts=PTS-STARTPTS[b]",
         "[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]"]
    args = ["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-t", f"{seconds}", "-i", png]
    if has_audio:
        # the clip's own sound keeps going under the card where it has any, then fades out
        f.append(f"[0:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,apad=whole_dur={total:.3f},"
                 f"afade=t=out:st={max(0, total - 0.9):.3f}:d=0.9[aout]")
    args += ["-filter_complex", ";".join(f), "-map", "[v]"]
    if has_audio:
        args += ["-map", "[aout]", "-c:a", "aac", "-b:a", "128k"]
    args += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30",
             "-movflags", "+faststart", "-t", f"{total:.3f}", tmp]
    subprocess.run(args, check=True)
    os.replace(tmp, dst)
    return round(total, 2)


def trim(src, dst, total, has_audio):
    fd, tmp = tempfile.mkstemp(suffix=".mp4", dir=os.path.dirname(os.path.abspath(dst)))
    os.close(fd)
    args = ["ffmpeg", "-v", "error", "-y", "-i", src, "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p"]
    if has_audio:
        args += ["-af", f"afade=t=out:st={max(0, total - 0.9):.3f}:d=0.9", "-c:a", "aac", "-b:a", "128k"]
    subprocess.run(args + ["-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, dst)
    return round(total, 2)


def ok_as_is(path, audience, mark):
    """True when the clip already ends on the right card at the right length."""
    if mark == f"{audience}-{VERSION}":
        return True
    kind, card = tail(path)
    # a dealer clip's blue card from the motion pipeline says "Free to list", so dealers always get theirs
    return kind == "blue" and audience == "seller" and KEEP_MIN <= card <= KEEP_MAX


def fix(dry=False):
    changed = []
    lib = json.load(open(LIBRARY))
    rows = [(e, "library") for e in lib["videos"]]
    queue = json.load(open(QUEUE)) if os.path.exists(QUEUE) else None
    by_file = {e.get("file"): e for e in lib["videos"]}
    for r in (queue or {}).get("shorts", []):
        if r.get("file") and r["file"] not in by_file:
            rows.append((r, "queue"))
    for e, where in rows:
        path = os.path.join(ROOT, e["file"])
        aud = audience_of(e)
        if not os.path.exists(path):
            continue
        if ok_as_is(path, aud, e.get("endcard")):
            if e.get("endcard") != f"{aud}-{VERSION}":
                e["endcard"] = f"{aud}-{VERSION}"
                changed.append((e["file"], "marked"))
            continue
        kind, card = tail(path)
        if dry:
            print(f"would fix {e['file']} ({aud}; ends on {kind or 'no card'} {card}s)")
            continue
        n = add(path, path, aud)
        e["endcard"] = f"{aud}-{VERSION}"
        changed.append((e["file"], f"card added ({aud}; was {kind or 'no card'} {card}s), now {n}s"))
    for r in (queue or {}).get("shorts", []):     # queue rows that point at library clips share the mark
        if r.get("file") in by_file and by_file[r["file"]].get("endcard"):
            if r.get("endcard") != by_file[r["file"]]["endcard"]:
                r["endcard"] = by_file[r["file"]]["endcard"]
                changed.append((r["file"], "queue row marked"))
    if not dry and changed:
        with open(LIBRARY, "w") as fh:
            json.dump(lib, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        if queue is not None:
            with open(QUEUE, "w") as fh:
                json.dump(queue, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
    for c in changed:
        print(" ", *c)
    print(f"end card: {len(changed)} change(s)")
    return changed


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fix":
        fix(dry="--dry" in sys.argv)
    elif cmd == "add" and len(sys.argv) >= 4:
        print(add(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "seller"))
    elif cmd == "check":
        for p in sys.argv[2:]:
            print(p, *tail(p))
    else:
        print(__doc__)
        sys.exit(2)
