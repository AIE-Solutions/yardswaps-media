"""Phone walkthrough built from a live recording of the real app (rig: local app, mocked API).
Same walkthrough format: opener with the real photo, headline over a phone, blue end card, music low.
The phone screen is the recording itself at real speed; only dead waits are trimmed.
Usage: live.py <clip.json> <out.mp4> [stills dir]"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
REPO = "/home/user/yardswaps-media"
sys.path.insert(0, os.path.join(REPO, "brand/posts"))
import kit
C = json.load(open(sys.argv[1])); OUT = sys.argv[2]; STILLS = sys.argv[3] if len(sys.argv) > 3 else None
W, H, FPS = 1080, 1920, 30
SLATE, BLUE, WHITE = kit.SLATE, kit.BLUE, kit.WHITE
GROUND = (244, 243, 246)
RAW = C["raw"]; TAPS = json.load(open(os.path.join(RAW, "taps.json")))
photo = Image.open(C["photo"]).convert("RGB")
HOOK, ASK = C["hook"], C["ask"]
T_OPEN, T_X = C.get("opener", 2.1), 0.3

def smooth(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def rounded(size, r):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255); return m

def opener(t):
    k = 1.0 + 0.03 * (t / (T_OPEN + T_X))
    big = photo.resize((int(H * photo.width / photo.height), H))
    x0 = (big.width - W) // 2
    bg = big.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(38))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (236, 239, 245)), 0.38)
    pw, ph = 900, 1200
    if photo.width / photo.height > pw / ph:
        ph = round(pw * photo.height / photo.width)
    else:
        pw = round(ph * photo.width / photo.height)
    px, py = (W - pw) // 2, 300 + (1200 - ph) // 2
    sw, sh_ = photo.width / k, photo.height / k
    box = ((photo.width - sw) / 2, (photo.height - sh_) / 2, (photo.width + sw) / 2, (photo.height + sh_) / 2)
    ph_img = photo.resize((pw, ph), Image.LANCZOS, box=box)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([px, py + 18, px + pw, py + ph + 18], 34, fill=90)
    bg.paste((20, 34, 60), (0, 0), sh.filter(ImageFilter.GaussianBlur(30)))
    bg.paste(ph_img, (px, py), rounded((pw, ph), 34))
    d = ImageDraw.Draw(bg)
    f = kit.sg(54)
    w = max(d.textlength(s, font=f) for s in HOOK)
    bx, by, bw, bh = (W - 900) // 2 - 26, min(168, py - 132) if ph >= 1100 else py - 215, int(w) + 76, 170
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([bx, by + 10, bx + bw, by + bh + 10], 30, fill=70)
    bg.paste((20, 34, 60), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], 30, fill=WHITE)
    d.text((bx + 38, by + 22), HOOK[0], font=f, fill=SLATE)
    d.text((bx + 38, by + 22 + 64), HOOK[1], font=f, fill=BLUE)
    f2 = kit.sg(44)
    lw = max(d.textlength(s, font=f2) for s in ASK)
    qw, qh = int(lw) + 84, 54 * len(ASK) + 44
    qx, qy = (W - qw) // 2, py + ph - qh + 54
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([qx, qy + 10, qx + qw, qy + qh + 10], 28, fill=80)
    bg.paste((20, 34, 60), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([qx, qy, qx + qw, qy + qh], 28, fill=BLUE)
    for i, s in enumerate(ASK):
        d.text(((W - d.textlength(s, font=f2)) / 2, qy + 20 + i * 54), s, font=f2, fill=WHITE)
    return bg

# Phone frame: the status bar and bezel of the sell-flow phone template, with the recording in its app area.
TPL = Image.open(C["template"]).convert("RGB")
CROP = (96, 70, 984, 1868)                  # bezel 136..943 x 110..1818 plus its soft shadow
APP = (154, 273, 926, 1801)                 # app viewport inside the template (393 x 778 CSS px)
PH_H = C.get("phone_h", 1503); S = PH_H / (1818 - 110)
PH_TOP = C.get("phone_top", 306)
CAP_Y = C.get("cap_y", 146)
def _mask():
    from scipy import ndimage
    a = np.asarray(TPL).astype(int)
    dark = a.max(axis=2) < 45
    lab, _ = ndimage.label(dark)
    sizes = ndimage.sum(dark, lab, range(1, lab.max() + 1))
    bez = lab == (int(np.argmax(sizes)) + 1)
    inside = ndimage.binary_fill_holes(bez) & ~bez
    m = np.zeros_like(inside); m[APP[1]:APP[3], :] = inside[APP[1]:APP[3], :]
    return Image.fromarray((m * 255).astype("uint8"), "L")
cw, ch = round((CROP[2] - CROP[0]) * S), round((CROP[3] - CROP[1]) * S)
OX = (W - cw) // 2; OY = PH_TOP - round((110 - CROP[1]) * S)
tpl_s = TPL.crop(CROP).resize((cw, ch), Image.LANCZOS)
mask_s = _mask().crop(CROP).resize((cw, ch), Image.LANCZOS)
ax0, ay0 = round((APP[0] - CROP[0]) * S), round((APP[1] - CROP[1]) * S)
aw, ah = round((APP[2] - APP[0]) * S) + 1, round((APP[3] - APP[1]) * S) + 1
base = Image.new("RGB", (W, H), GROUND); base.paste(tpl_s, (OX, OY))

def fit(d, s, size, maxw=980):
    f = kit.sg(size)
    while d.textlength(s, font=f) > maxw:
        size -= 2; f = kit.sg(size)
    return f

def scene(frame, cap, tap=None, a_tap=0.0, press=0.0):
    im = base.copy()
    lay = tpl_s.copy(); lay.paste(frame.resize((aw, ah), Image.LANCZOS), (ax0, ay0))
    im.paste(Image.composite(lay, tpl_s, mask_s), (OX, OY))
    d = ImageDraw.Draw(im)
    for i, (s, col) in enumerate(zip(cap, (SLATE, BLUE))):
        f = fit(d, s, 56)
        d.text(((W - d.textlength(s, font=f)) / 2, CAP_Y + i * 68), s, font=f, fill=col)
    if tap and a_tap > 0.01:
        cx = OX + ax0 + tap[0] / 393 * aw; cy = OY + ay0 + tap[1] / 778 * ah
        r = int(34 - 8 * press)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(ov)
        d2.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(37, 99, 235, int(175 * a_tap)), outline=(255, 255, 255, int(235 * a_tap)), width=4)
        im.paste(ov, (0, 0), ov)
    return im

def src(i):
    if isinstance(i, str):
        return Image.open(i).convert("RGB")
    return Image.open(os.path.join(RAW, f"{i:04d}.jpg")).convert("RGB")

# timeline: list of (source frame or image path, caption index)
def auto_segments():
    """Keep every moving frame at real speed; trim still stretches; captions follow the take's marks."""
    import glob
    M = json.load(open(os.path.join(RAW, "marks.json")))
    n = len(glob.glob(os.path.join(RAW, "[0-9]*.jpg")))
    prev = None; mv = []
    for i in range(n):
        a = np.asarray(Image.open(os.path.join(RAW, f"{i:04d}.jpg")).convert("L").resize((131, 259))).astype(int)
        mv.append(False if prev is None else bool((abs(a - prev) > 12).sum() > 0)); prev = a
    # close 1-3 frame gaps inside a movement
    for i in range(1, n - 1):
        if not mv[i] and any(mv[max(0, i - 3):i]) and any(mv[i + 1:i + 4]): mv[i] = True
    taps = [t["f"] for t in TAPS]
    keep = [False] * n; i = 0
    while i < n:
        j = i
        while j + 1 < n and mv[j + 1] == mv[i]: j += 1
        if mv[i]:
            for k in range(i, j + 1): keep[k] = True
        else:
            cap = 16
            if i <= M["filled"] + 8 and j >= M["filled"]: cap = 30          # let the filled fields be read
            if i <= M["photo_in"] + 6 and j > M["photo_in"]: cap = 24
            for k in range(max(i, j - cap + 1), j + 1): keep[k] = True
            for t in taps:
                if i <= t <= j:
                    for k in range(max(i, t - (22 if t == taps[0] else 10)), min(j, t + 6) + 1): keep[k] = True
        i = j + 1
    def cap_of(f):
        if f < M["photo_in"]: return 0
        if f < M["filled"] - 6: return 1
        if f < M["price"] - 10: return 2
        if f <= M["priced"] + 22: return 3
        if f <= M["specs"]: return 4
        return 5
    out = []; x = 0.0
    f = 0
    while f < n:
        if keep[f]:
            fast = mv[f] and M["specs"] < f < taps[-1] - 12        # the long scroll to Publish runs at 1.5x
            out.append((f, cap_of(f)))
            if fast and len(out) % 2 == 0 and f + 1 < n and keep[f + 1]: f += 1
        f += 1
    out += [(n - 1, 5)] * 8
    return out
seq = []
if "segments" not in C:
    seq = auto_segments(); C["segments"] = []
for seg in C["segments"]:
    a, b = seg["frames"]; step = seg.get("step", 1.0)
    x = float(a)
    while x <= b + 1e-6:
        seq.append((int(round(x)), seg["cap"])); x += step
    for _ in range(seg.get("hold", 0)):
        seq.append((b, seg["cap"]))
if C.get("final"):
    n = C["final"]["frames"]
    for k in range(n):
        seq.append((C["final"]["image"], C["final"]["cap"]))
CAPS = C["caps"]
n_open = round(T_OPEN * FPS); n_x = round(T_X * FPS)
END_S = 2.9
ENDDIR = C["end_frames"]            # transparent frames from endrender.js (the earlier walkthroughs' ending)
last_scene = None
total = n_open + len(seq) + round(END_S * FPS)
dur = total / FPS
vol = C.get("volume", 0.35)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", os.path.join(REPO, "music/v2", C["music"]), "-filter_complex",
                        f"[1:a]atrim=0:{dur},volume={vol},afade=t=in:d=0.3,afade=t=out:st={dur-0.8}:d=0.8[a]", "-map", "0:v", "-map", "[a]",
                        "-c:a", "aac", "-b:a", "128k", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", "-t", f"{dur}", OUT], stdin=subprocess.PIPE)
def tap_state(sf):
    if isinstance(sf, str):
        return None, 0, 0
    for tp in TAPS:
        dt = sf - tp["f"]
        if -8 <= dt <= 5:
            a = smooth((dt + 8) / 4) * (1 - smooth((dt - 2) / 3))
            return (tp["x"], tp["y"]), a, smooth((dt + 1) / 2)
    return None, 0, 0
cache = {}
prev_final = None
for j in range(total):
    if j < n_open:
        out = opener(j / FPS)
    elif j < n_open + len(seq):
        k = j - n_open
        sf, ci = seq[k]
        fr = cache.get(sf)
        if fr is None:
            cache.clear(); fr = cache[sf] = src(sf)
        if isinstance(sf, str) and prev_final is not None:
            kk = k - first_final
            if kk < 5:
                fr = Image.blend(prev_final, fr, smooth((kk + 1) / 5))
        tap, a, pr = tap_state(sf)
        out = scene(fr, CAPS[ci], tap, a, pr)
        if not isinstance(sf, str):
            prev_final = fr; first_final = k + 1
        last_scene = out
        if k < n_x:
            out = Image.blend(opener(j / FPS), out, smooth((k + 1) / n_x))
    else:
        e = Image.open(os.path.join(ENDDIR, f"{min(j - n_open - len(seq), 86):03d}.png")).convert("RGBA")
        out = last_scene.convert("RGBA"); out.alpha_composite(e); out = out.convert("RGB")
    if STILLS and (j % 15 == 0):
        out.resize((270, 480), Image.LANCZOS).save(os.path.join(STILLS, f"s{j:04d}.jpg"), quality=82)
    if STILLS and j in C.get("stills", []):
        out.save(os.path.join(STILLS, f"full-{j:04d}.png"))
    enc.stdin.write(out.tobytes())
enc.stdin.close(); enc.wait()
print(OUT, total, "frames", round(dur, 2), "s; app", round(len(seq) / FPS, 2), "s")
