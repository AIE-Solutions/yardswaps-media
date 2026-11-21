"""render.py <frames_dir> <photo.jpg> <fonts_dir> <out.mp4>
"Snap it" camera-POV ad, 9:16 or 1:1 (env RATIO=1x1). No generated imagery: the viewfinder shows the real listing photo,
the app part is the real sell-flow recording of that same photo (frames_dir, extracted from
motion/silent/yardswaps-pressure-washer-replaced-9x16.mp4 from 4.0 s at 30 fps).

0.00-2.90  full-screen phone camera: handheld drift (zoom 1.035, under the 1.04 cap), soft focus,
           focus tap 0.9 s, shutter 2.3 s (black blink, flash, thumbnail)
2.90-3.90  pull back: the camera screen shrinks into the phone of the recording
3.90-4.20  hold, 4.20-4.50 the camera screen dissolves into the app (recording t=5.8 s on)
4.50-      the recording plays to t=13.9 s (AI fills, price, published)
"""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

FR, PHOTO, FONTS, OUT = sys.argv[1:5]
import os
RATIO = os.environ.get("RATIO", "9x16")
FPS = 30
T_TAP, T_SHUT, T_Z0, T_Z1, T_DIS, T_APP = 0.9, 2.3, 2.9, 3.9, 4.2, 4.5
SRC_T0 = 5.8                            # recording time shown at T_DIS
SRC_END = 13.9
BLUE = (37, 99, 235); AMBER = (255, 190, 24)

B = lambda s: ImageFont.truetype(f"{FONTS}/SpaceGrotesk_700Bold.ttf", s)
M = lambda s: ImageFont.truetype(f"{FONTS}/SpaceGrotesk_500Medium.ttf", s)

def frame_at(t):  # recording frame for recording time t (frames start at 4.0 s)
    k = int(round((t - 4.0) * FPS)) + 1
    return Image.open(f"{FR}/{k:04d}.png").convert("RGB")

def detect_screen(img):
    """Phone screen rect in the recording: dark bezel box, then the white screen inside it."""
    a = np.asarray(img.convert("L")).astype(int); dark = a < 40
    cols = np.where(dark.sum(0) > a.shape[0] * 0.25)[0]; rows = np.where(dark.sum(1) > 40)[0]
    l, r = cols.min(), cols.max(); ym = (rows.min() + rows.max()) // 2
    il = l
    while a[ym, il] < 200: il += 1
    ir = r
    while a[ym, ir] < 200: ir -= 1
    xm = il + (ir - il) // 6
    col = a[:, xm]; t = np.where(col < 40)[0].min(); b = np.where(col < 40)[0].max()
    it = t
    while col[it] < 200: it += 1
    ib = b
    while col[ib] < 200: ib -= 1
    return il, it, ir - il + 1, ib - it + 1

SRC_T0 = 5.8                            # recording time shown at T_DIS
SRC_END = 13.9
static_bg = frame_at(SRC_T0)
W, H = static_bg.size
SX, SY, SW, SH = detect_screen(static_bg)
k_ = SW / 462; SR = 58 * k_                     # radius and island measured on the 9:16 recording (screen 462 wide)
ISL = (SX + 159 * k_, SY + 14 * k_, SX + 304 * k_, SY + 55 * k_)
CW = 1080; CH = round(CW * SH / SW)
VF_Y, VF_H = 470, 1440
SHUT_Y = 1990
if RATIO == "9x16":
    Z0 = CW / SW; C0 = (SX + SW / 2, SY + SH / 2)
    CAP = dict(x=72, bar=300, y1=330, y2=428, size=80, g0=330, g1=420, gmax=760)
else:   # square: the whole viewfinder fits the frame height, phone bezel at the sides
    Z0 = H * CW / (VF_H * SW); C0 = (SX + SW / 2, SY + (VF_Y + VF_H / 2) * SW / CW)
    CAP = dict(x=170, bar=56, y1=78, y2=152, size=60, g0=40, g1=300, gmax=420)
print(RATIO, "screen", SX, SY, SW, SH, "Z0", round(Z0, 3), flush=True)
# clean plate: no caption residue in the static frame
_a = np.asarray(static_bg).copy()
if RATIO == "9x16": _a[:392] = np.median(_a[:392, :120], axis=1, keepdims=True).astype(np.uint8)
else: _a[:, :SX - 40] = np.median(_a[:, :60], axis=1, keepdims=True).astype(np.uint8)
static_bg = Image.fromarray(_a)

photo = ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB")
photo = photo.resize((1080 * 2, 1440 * 2), Image.LANCZOS)   # exactly 3:4, supersampled

def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def ease_io(x): x = min(1, max(0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)

def shake(t):
    """Handheld drift: sum of slow sines, calmer after the focus tap, nearly still after the shutter."""
    amp = 1.0 if t < T_TAP else (0.55 if t < T_SHUT else 0.25)
    dx = 9 * math.sin(2.1 * t + 0.4) + 4 * math.sin(5.3 * t + 1.7)
    dy = 7 * math.sin(1.7 * t + 2.2) + 3 * math.sin(6.1 * t + 0.3)
    rot = 0.30 * math.sin(1.3 * t + 0.9) + 0.08 * math.sin(4.7 * t)
    return dx * amp, dy * amp, rot * amp

def viewfinder(t):
    s = 1.035
    dx, dy, rot = shake(t)
    big = photo.rotate(rot, resample=Image.BICUBIC, center=(1080 + dx * 2, 1440 + dy * 2))
    cw, ch = 1080 * 2 / s, 1440 * 2 / s
    cx, cy = 1080 - dx * 2, 1440 - dy * 2
    vf = big.crop((round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2))).resize((1080, 1440), Image.LANCZOS)
    # focus: soft before the tap, sharp 0.3 s after it
    blur = 5.0 * (1 - ease((t - T_TAP - 0.05) / 0.3)) if t < T_TAP + 0.4 else 0
    if blur > 0.2: vf = vf.filter(ImageFilter.GaussianBlur(blur))
    expo = 0.94 + 0.06 * ease((t - T_TAP) / 0.35)
    vf = Image.fromarray(np.clip(np.asarray(vf, dtype=np.float32) * expo, 0, 255).astype(np.uint8))
    return vf

THUMB = photo.resize((96, 128), Image.LANCZOS).crop((0, 16, 96, 112))

def canvas(t):
    c = Image.new("RGB", (CW, CH), (0, 0, 0))
    vf = viewfinder(min(t, T_Z0 + 0.3))
    c.paste(vf, (0, VF_Y))
    d = ImageDraw.Draw(c, "RGBA")
    # status bar (only seen once the screen is pulled back into the phone)
    d.text((112, 52), "9:41", font=B(44), fill=(255, 255, 255))
    for i, h in enumerate((14, 20, 26, 32)): d.rounded_rectangle((842 + i * 14, 92 - h, 852 + i * 14, 92), 3, fill=(255, 255, 255))
    d.rounded_rectangle((920, 62, 972, 92), 8, outline=(255, 255, 255), width=3); d.rectangle((925, 67, 960, 87), fill=(255, 255, 255))
    # top controls: flash and live off, generic camera glyphs
    d.ellipse((70, 300, 150, 380), outline=(255, 255, 255, 220), width=4)
    d.polygon([(116, 316), (96, 344), (110, 344), (102, 366), (126, 334), (112, 334)], fill=(255, 255, 255, 230))
    d.ellipse((930, 300, 1010, 380), outline=(255, 255, 255, 220), width=4); d.ellipse((958, 328, 982, 352), fill=(255, 255, 255, 230))
    # zoom chip inside the viewfinder
    d.ellipse((498, VF_Y + VF_H - 120, 582, VF_Y + VF_H - 36), fill=(0, 0, 0, 120))
    tw = d.textlength("1x", font=B(36)); d.text((540 - tw / 2, VF_Y + VF_H - 101), "1x", font=B(36), fill=AMBER)
    # focus square
    if T_TAP <= t < T_SHUT:
        k = t - T_TAP; sc = 1.45 - 0.45 * ease(k / 0.22); a = 255 if k < 0.9 else int(255 * max(0.35, 1 - (k - 0.9) / 0.4))
        fx, fy, r = 380, VF_Y + 690, 92 * sc
        d.rectangle((fx - r, fy - r, fx + r, fy + r), outline=AMBER + (a,), width=4)
        for (x0, y0, x1, y1) in ((fx, fy - r, fx, fy - r + 16), (fx, fy + r - 16, fx, fy + r), (fx - r, fy, fx - r + 16, fy), (fx + r - 16, fy, fx + r, fy)):
            d.line((x0, y0, x1, y1), fill=AMBER + (a,), width=4)
    # touch ripples (focus tap, shutter tap)
    for tt, (px, py) in ((T_TAP, (380, VF_Y + 690)), (T_SHUT - 0.05, (540, SHUT_Y))):
        k = t - tt
        if 0 <= k < 0.45:
            rr = 40 + 90 * ease(k / 0.45); a = int(150 * (1 - k / 0.45))
            d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(255, 255, 255, a // 2), outline=(255, 255, 255, a), width=3)
    # shutter button
    k = t - T_SHUT; press = 1 - 0.14 * math.sin(math.pi * min(1, max(0, k / 0.18))) if 0 <= k < 0.18 else 1
    d.ellipse((540 - 96, SHUT_Y - 96, 540 + 96, SHUT_Y + 96), outline=(255, 255, 255), width=8)
    ri = 78 * press; d.ellipse((540 - ri, SHUT_Y - ri, 540 + ri, SHUT_Y + ri), fill=(255, 255, 255))
    # last-photo thumbnail
    d.rounded_rectangle((150, SHUT_Y - 50, 250, SHUT_Y + 50), 14, fill=(40, 40, 40))
    if t >= T_SHUT + 0.08:
        p = ease((t - T_SHUT - 0.08) / 0.25); sz = int(96 * (0.55 + 0.45 * p))
        th = THUMB.resize((sz, sz)); m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sz - 1, sz - 1), 12, fill=255)
        c.paste(th, (200 - sz // 2, SHUT_Y - sz // 2), m)
    # flip-camera glyph
    d.ellipse((830, SHUT_Y - 50, 930, SHUT_Y + 50), fill=(60, 60, 60))
    d.arc((852, SHUT_Y - 28, 908, SHUT_Y + 28), 200, 340, fill=(255, 255, 255), width=5)
    d.arc((852, SHUT_Y - 28, 908, SHUT_Y + 28), 20, 160, fill=(255, 255, 255), width=5)
    d.rounded_rectangle((CW // 2 - 140, CH - 40, CW // 2 + 140, CH - 28), 6, fill=(255, 255, 255))
    # shutter: 2 black frames, then a short flash over the captured frame
    if 0 <= k < 0.07: c.paste((0, 0, 0), (0, VF_Y, CW, VF_Y + VF_H))
    elif 0.07 <= k < 0.3:
        fl = Image.new("RGB", (CW, VF_H), (255, 255, 255)); a = 0.55 * (1 - (k - 0.07) / 0.23)
        c.paste(Image.blend(c.crop((0, VF_Y, CW, VF_Y + VF_H)), fl, a), (0, VF_Y))
    return c

def screen_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), max(1, round(r)), fill=255); return m

def captions(img, t):
    """Opener captions, house style: white Space Grotesk, blue bar, top gradient, on the full-screen camera only."""
    if t >= T_Z0 + 0.35: return img
    a = 1.0 if t < T_Z0 else 1 - (t - T_Z0) / 0.35
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    g = np.zeros((H, 1), np.uint8); ys = np.arange(H)
    g[:, 0] = np.clip(215 * (1 - np.clip((ys - CAP["g0"]) / CAP["g1"], 0, 1)) ** 1.3, 0, 215) * (ys < CAP["gmax"])
    grad = Image.fromarray(g, "L").resize((W, H))
    lay = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), lay, grad)
    d = ImageDraw.Draw(lay)
    x = CAP["x"]
    d.rounded_rectangle((x, CAP["bar"], x + 84, CAP["bar"] + 12), 6, fill=BLUE + (255,))
    d.text((x, CAP["y1"]), "Equipment sitting idle?", font=B(CAP["size"]), fill=(255, 255, 255, 255))
    if t >= T_TAP + 0.1:
        p = ease((t - T_TAP - 0.1) / 0.3)
        d.text((x, CAP["y2"] + 18 * (1 - p)), "Snap one photo.", font=B(CAP["size"]), fill=(140, 180, 255, int(255 * p)))
    lay.putalpha(Image.fromarray((np.asarray(lay.getchannel("A"), np.float32) * a).astype(np.uint8)))
    return Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")

def compose(t, bg):
    """World = recording frame with the camera canvas in the phone screen; camera pulls back from Z0 to 1."""
    p = ease_io((t - T_Z0) / (T_Z1 - T_Z0))
    z = Z0 * (1 - p) + 1.0 * p
    # keep the zoom anchored at the screen centre until the end, where it lands on the full frame
    cx = C0[0] * (1 - p) + (W / 2) * p
    cy = C0[1] * (1 - p) + (H / 2) * p
    wx0, wy0 = cx - W / (2 * z), cy - H / (2 * z)
    if z > 1.001:
        out = bg.transform((W, H), Image.AFFINE, (1 / z, 0, wx0, 0, 1 / z, wy0), resample=Image.BICUBIC)
    else:
        out = bg.copy()
    cv = canvas(t)
    a_cv = 1.0 if t < T_DIS else max(0.0, 1 - (t - T_DIS) / (T_APP - T_DIS))
    if a_cv > 0:
        sw, sh = SW * z, SH * z; ox, oy = (SX - wx0) * z, (SY - wy0) * z
        # paste the part of the canvas that is on screen
        scale = sw / CW
        x0, y0 = max(0, -ox / scale), max(0, -oy / scale)
        x1, y1 = min(CW, (W - ox) / scale), min(CH, (H - oy) / scale)
        sub = cv.crop((round(x0), round(y0), round(x1), round(y1)))
        pw, ph = max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale))
        sub = sub.resize((pw, ph), Image.LANCZOS)
        m = screen_mask(round(sw), round(sh), SR * z).crop((round(x0 * scale), round(y0 * scale), round(x0 * scale) + pw, round(y0 * scale) + ph))
        if a_cv < 1: m = m.point(lambda v: int(v * a_cv))
        px, py = round(ox + x0 * scale), round(oy + y0 * scale)
        out.paste(sub, (px, py), m)
        d = ImageDraw.Draw(out)
        ix0, iy0, ix1, iy1 = [(v - o) * z for v, o in zip(ISL, (wx0, wy0, wx0, wy0))]
        if iy1 > 0 and a_cv >= 1: d.rounded_rectangle((ix0, iy0, ix1, iy1), 21 * z, fill=(8, 8, 10))
    return captions(out, t)

ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                       "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
n_total = int(round((T_APP + (SRC_END - (SRC_T0 + T_APP - T_DIS))) * FPS))
for i in range(n_total):
    t = i / FPS
    if t < T_DIS: img = compose(t, static_bg)
    elif t < T_APP: img = compose(t, frame_at(SRC_T0 + (t - T_DIS)))
    else: img = frame_at(SRC_T0 + (t - T_DIS))
    ff.stdin.write(img.tobytes())
    if i % 30 == 0: print("t", round(t, 2), flush=True)
ff.stdin.close(); ff.wait()
print("done", OUT, n_total / FPS)
