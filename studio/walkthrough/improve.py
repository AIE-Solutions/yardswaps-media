"""Light refinement of an earlier phone walkthrough, on its own footage.
Same words, same phone screens, same music and end card. Three changes:
  1. opener: the real listing photo large and whole instead of a narrow strip;
  2. the photo-in-phone moment becomes a camera shot (shutter, flash);
  3. the phone is larger through the app section.
Usage: improve.py <original.mp4> <photo.jpg> <out.mp4> [still frames dir]"""
import sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "/home/user/yardswaps-media/brand/posts")
import kit

SRC, PHOTO, OUT = sys.argv[1:4]
STILLS = sys.argv[4] if len(sys.argv) > 4 else None
W, H, FPS = 1080, 1920, 30
CUT = 392                 # headline band above stays as it is; the phone below is enlarged
ZOOM = 1.28
SNAP_F = 153              # original frame where the photo fills the phone (5.10 s)
T_OPEN_END, T_CAM = 3.1, 3.5      # opener, then dissolve to the phone camera
T_PRESS, T_FLASH = 4.35, 4.5
T_ZOUT0, T_ZOUT1 = 11.9, 12.5     # ease back to the original size before the side photo card comes in
SLATE, BLUE, WHITE = kit.SLATE, kit.BLUE, kit.WHITE
HOOK = ("POV: the condenser you pulled", "on the last changeout.")
ASK = ("How many pulled", "units are behind your", "shop?")


def smooth(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def zoomed(frame, s):
    if s <= 1.001:
        return frame
    z = frame.transform((W, H), Image.AFFINE, (1 / s, 0, 540 - 540 / s, 0, 1 / s, CUT - CUT / s), resample=Image.BICUBIC)
    z = z.filter(ImageFilter.UnsharpMask(radius=1.4, percent=45, threshold=2))
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for i, y in enumerate(range(CUT - 8, CUT + 4)):
        d.line([(0, y), (W, y)], fill=int(255 * (i + 1) / 12))
    d.rectangle([0, CUT + 4, W, H], fill=255)
    return Image.composite(z, frame, m)


def zp(x, y, s=ZOOM):
    return 540 + (x - 540) * s, CUT + (y - CUT) * s


def rounded(size, r):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255); return m


photo = Image.open(PHOTO).convert("RGB")


def opener(t):
    k = 1.0 + 0.03 * (t / T_CAM)
    bg = photo.resize((W, int(W * photo.height / photo.width)))
    bg = bg.resize((int(bg.width * H / bg.height) + 2, H)).crop((0, 0, W, H)) if bg.height < H else bg.crop((0, 0, W, H))
    big = photo.resize((int(H * photo.width / photo.height), H))
    x0 = (big.width - W) // 2
    bg = big.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(38))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (236, 239, 245)), 0.38)
    pw, ph = 900, 1200
    px, py = (W - pw) // 2, 300
    src_w = photo.width / k; src_h = photo.height / k
    box = ((photo.width - src_w) / 2, (photo.height - src_h) / 2, (photo.width + src_w) / 2, (photo.height + src_h) / 2)
    ph_img = photo.resize((pw, ph), Image.LANCZOS, box=box)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([px, py + 18, px + pw, py + ph + 18], 34, fill=90)
    bg.paste((20, 34, 60), (0, 0), sh.filter(ImageFilter.GaussianBlur(30)))
    bg.paste(ph_img, (px, py), rounded((pw, ph), 34))
    d = ImageDraw.Draw(bg)
    f = kit.sg(54)
    w = max(d.textlength(s, font=f) for s in HOOK)
    bx, by, bw, bh = px - 26, 168, int(w) + 76, 170
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


# Phone screen (original coordinates), measured on the settled frame.
SCR = (311, 540, 769, 1453)      # the photo area under the status bar


def camera(base, t):
    """base = enlarged still of the photo-in-phone frame. Adds the camera controls, the press and the flash."""
    im = base.copy()
    x0, y0 = zp(SCR[0], SCR[1]); x1, y1 = zp(SCR[2], SCR[3])
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    ui = smooth((t - T_CAM) / 0.25) * (1 - smooth((t - (T_FLASH + 0.25)) / 0.3))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    # bottom shade inside the screen, shutter, focus corners
    shade_h = int(190 * ZOOM)
    for i in range(shade_h):
        d.line([(x0, y1 - shade_h + i), (x1, y1 - shade_h + i)], fill=(0, 0, 0, int(120 * i / shade_h)))
    cx, cy = (x0 + x1) // 2, y1 - int(88 * ZOOM)
    R = int(40 * ZOOM)
    press = smooth((t - T_PRESS) / 0.12) * (1 - smooth((t - T_FLASH) / 0.15))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, 255), width=int(5 * ZOOM))
    r = int((31 - 6 * press) * ZOOM)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))
    L, wd = int(34 * ZOOM), int(4 * ZOOM)
    fx0, fy0, fx1, fy1 = x0 + int(40 * ZOOM), y0 + int(120 * ZOOM), x1 - int(40 * ZOOM), y1 - int(250 * ZOOM)
    for (ax, ay, sx, sy) in ((fx0, fy0, 1, 1), (fx1, fy0, -1, 1), (fx0, fy1, 1, -1), (fx1, fy1, -1, -1)):
        d.line([(ax, ay), (ax + sx * L, ay)], fill=(255, 255, 255, 235), width=wd)
        d.line([(ax, ay), (ax, ay + sy * L)], fill=(255, 255, 255, 235), width=wd)
    a = ov.getchannel("A").point(lambda v: int(v * ui)); ov.putalpha(a)
    # keep everything inside the phone screen (rounded at the bottom)
    msk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(msk).rounded_rectangle([x0, y0 - 80, x1, y1], int(52 * ZOOM), fill=255)
    ImageDraw.Draw(msk).rectangle([0, 0, W, y0 - 1], fill=0)
    ov.putalpha(Image.composite(ov.getchannel("A"), Image.new("L", (W, H), 0), msk))
    im.paste(ov, (0, 0), ov)
    fl = max(0.0, 1 - (t - T_FLASH) / 0.28) if t >= T_FLASH else 0.0
    if fl > 0:
        white = Image.new("RGB", (W, H), WHITE)
        im = Image.composite(white, im, msk.point(lambda v: int(v * 0.92 * fl)))
    return im


def frames():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield Image.frombytes("RGB", (W, H), b)


def main():
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:a", "copy", "-c:v", "libx264", "-crf", "17",
                            "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
    held = []
    snap = None
    cam_from = int(round(T_OPEN_END * FPS))
    for i, fr in enumerate(frames()):
        t = i / FPS
        if i < SNAP_F:
            held.append(None)
            if i == 0:
                pass
            continue_original = False
        if i == SNAP_F:
            snap = zoomed(fr, ZOOM)
            # everything before this frame is rebuilt: opener, dissolve, camera
            for j in range(SNAP_F):
                tj = j / FPS
                if tj < T_OPEN_END:
                    out = opener(tj)
                elif tj < T_CAM:
                    out = Image.blend(opener(tj), camera(snap, tj), smooth((tj - T_OPEN_END) / (T_CAM - T_OPEN_END)))
                else:
                    out = camera(snap, tj)
                if STILLS and j in (30, 99, 115, 132, 136, 140):
                    out.save(os.path.join(STILLS, f"new-{j:03d}.png"))
                enc.stdin.write(out.tobytes())
        if i >= SNAP_F:
            s = ZOOM + (1.0 - ZOOM) * smooth((t - T_ZOUT0) / (T_ZOUT1 - T_ZOUT0))
            out = zoomed(fr, s)
            if STILLS and i in (153, 160, 200, 260, 330, 365, 372, 380, 400):
                out.save(os.path.join(STILLS, f"new-{i:03d}.png"))
            enc.stdin.write(out.tobytes())
    enc.stdin.close(); enc.wait()


main()
