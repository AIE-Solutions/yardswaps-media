#!/usr/bin/env python3
"""Build v3 of the "Too big to ship? List it free." seller ad (9:16, 4:5, 1:1).

v3 (Alan, Nov 24): the phone shows the SAME booster pump the ad just featured. The sell flow is
recorded in the real app (Expo web, local) with that listing's own photo, see rec/.

Inputs (all in this folder):
  clips/<slug>.mp4   Runway image-to-video clips made from the REAL listing photos
                     (camera moves only; the item is not redrawn). Missing clip ->
                     the real photo src/<photo>.jpg with a slow push (1.00-1.035).
  APPDIR/NNNN.jpg    real app recording, 30 fps frames (rec/rec_booster.js), 1179x2334
  audio/vo.mp3       ElevenLabs v4 voice (Justin Case), audio/music.mp3 bed
Usage: build.py [9x16|4x5|1x1 ...]
"""
import os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(ROOT, "listings", "fonts")
LOGO = os.path.join(ROOT, "broll", "in", "brand-kit", "logo", "yardswaps-logo-512.png")
WORDMARK = os.path.join(ROOT, "broll", "in", "brand-kit", "wordmark", "yardswaps-wordmark-on-light.png")
APPDIR = os.environ.get("APPDIR", "/mnt/project-files/yardswaps-campaign/assets/ads/big-items-v3/rec/raw/booster")

FPS = 30
SLATE = (26, 51, 83)
BLUE = (37, 99, 235)
PAGE = (243, 243, 245)
INK = (32, 32, 32)
WHITE = (255, 255, 255)

SIZES = {"9x16": (1080, 1920), "4x5": (1080, 1350), "1x1": (1080, 1080)}

# (start, end, kind, source, caption, clip_in)   times in seconds of the final cut
VO_OFFSET = 0.30
TIMELINE = [
    (0.00, 2.10, "item", "semi", "Too big to ship?", 0.0),
    (2.10, 3.25, "item", "semi", "Semi truck", 2.1),
    (3.25, 4.40, "item", "booster", "Booster pump", 0.0),
    (4.40, 5.45, "item", "rockbucket", "Rock bucket", 0.0),
    (5.45, 6.70, "item", "cooling", "Cooling system", 0.0),
    (6.70, 7.75, "item", "vplow", "V-plow", 0.0),
    (7.75, 9.70, "app", None, "List it free.", (30, 112)),
    (9.70, 12.60, "app", None, "Snap photos.\nThe AI writes the listing.", (112, 330)),
    (12.60, 16.10, "end", None, None, 0.0),
]
PHOTO = {"semi": "pete05-4", "booster": "booster-1", "rockbucket": "rockbucket-0",
         "cooling": "cooling-1", "vplow": "vplow-0", "ripper": "ripper140-0"}
DURATION = TIMELINE[-1][1]


def font(name, size, var=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


def read_frames(path, t0, n, scale_w=None):
    vf = f"fps={FPS}" + (f",scale={scale_w}:-2" if scale_w else "")
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    w, h = map(int, probe.split(","))
    if scale_w:
        h = int(round(h * scale_w / w / 2) * 2); w = scale_w
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", path, "-frames:v", str(n),
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    arr = np.frombuffer(raw, np.uint8)
    k = len(arr) // (w * h * 3)
    frames = [Image.fromarray(arr[i * w * h * 3:(i + 1) * w * h * 3].reshape(h, w, 3)) for i in range(k)]
    while len(frames) < n:            # hold the last frame if the clip is short
        frames.append(frames[-1])
    return frames


def photo_frames(slug, n):
    im = Image.open(os.path.join(HERE, "src", PHOTO[slug] + ".jpg")).convert("RGB")
    im.thumbnail((960, 1280))
    out = []
    for i in range(n):
        z = 1.0 + 0.035 * i / max(1, n - 1)
        w, h = im.size
        cw, ch = w / z, h / z
        box = ((w - cw) / 2, (h - ch) / 2, (w + cw) / 2, (h + ch) / 2)
        out.append(im.resize((w, h), Image.LANCZOS, box=box))
    return out


def fit(im, W, H):
    s = min(W / im.width, H / im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def cover(im, W, H):
    s = max(W / im.width, H / im.height)
    r = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.BILINEAR)
    x, y = (r.width - W) // 2, (r.height - H) // 2
    return r.crop((x, y, x + W, y + H))


def wordmark_pill(W):
    wm = Image.open(WORDMARK).convert("RGBA")
    h = int(W * 0.058)
    wm = wm.resize((int(wm.width * h / wm.height), h), Image.LANCZOS)
    pad = int(h * 0.45)
    pill = Image.new("RGBA", (wm.width + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    d.rounded_rectangle((0, 0, pill.width - 1, pill.height - 1), radius=pill.height // 2, fill=(255, 255, 255, 240))
    pill.alpha_composite(wm, (pad, pad))
    return pill


def wrap_lines(text):
    return text.split("\n")


def caption_layer(W, H, text, bottom):
    """Space Grotesk lines lower-left with a blue bar (house style)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lines = wrap_lines(text)
    size = int(W * (0.085 if len(lines) == 1 else 0.066))
    f = font("SpaceGrotesk.ttf", size, "Bold")
    d = ImageDraw.Draw(layer)
    lh = int(size * 1.12)
    x = int(W * 0.075)
    y0 = bottom - lh * len(lines)
    # soft dark band for contrast
    band = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(band)
    top = max(0, y0 - int(size * 1.4))
    for yy in range(top, H):
        a = min(170, int(170 * (yy - top) / max(1, (y0 - top))))
        bd.line([(0, yy), (W, yy)], fill=a)
    shade = Image.new("RGBA", (W, H), (8, 16, 28, 255))
    shade.putalpha(band)
    layer.alpha_composite(shade)
    d = ImageDraw.Draw(layer)
    bar_w = max(8, int(W * 0.011))
    d.rectangle((x - bar_w - int(W * 0.025), y0 + int(size * 0.12), x - int(W * 0.025), y0 + lh * len(lines) - int(size * 0.12)), fill=BLUE + (255,))
    for i, ln in enumerate(lines):
        d.text((x, y0 + i * lh), ln, font=f, fill=WHITE + (255,))
    return layer


def item_frame(fr, W, H, cap, pill):
    bg = cover(fr, W // 8, H // 8).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    bg = Image.blend(bg, Image.new("RGB", (W, H), (20, 26, 34)), 0.35)
    top = int(H * 0.085) if H > W * 1.5 else int(H * 0.0)
    area_h = int(H * 0.78) if H > W * 1.5 else H
    f = fit(fr, W, area_h)
    canvas = bg.convert("RGBA")
    canvas.paste(f, ((W - f.width) // 2, top + (area_h - f.height) // 2))
    canvas.alpha_composite(cap)
    canvas.alpha_composite(pill, (int(W * 0.05), int(W * 0.05)))
    return canvas.convert("RGB")


def app_frames(rng, n):
    """Raw recording frames rng[0]..rng[1] spread over n output frames (light time-warp)."""
    last = len([x for x in os.listdir(APPDIR) if x.endswith(".jpg")]) - 1
    a, b = rng
    idx = [min(last, int(round(a + (b - a) * i / max(1, n - 1)))) for i in range(n)]
    return [Image.open(os.path.join(APPDIR, f"{k:04d}.jpg")).convert("RGB") for k in idx]


def ease(t):
    t = min(1.0, max(0.0, t))
    return 0.5 - math.cos(math.pi * t) / 2


def phone(screen, inner_w):
    """Real app screen inside a plain phone body (status bar drawn, as in the motion kit's frame.html)."""
    sw = inner_w
    sh = int(round(screen.height * sw / screen.width))
    bar = int(sw * 0.118)
    bez = int(sw * 0.026)
    ow, oh = sw + 2 * bez, sh + bar + 2 * bez
    r_out = int(ow * 0.145)
    body = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, ow - 1, oh - 1), radius=r_out, fill=(18, 18, 20, 255), outline=(58, 58, 62, 255), width=max(2, bez // 6))
    scr = Image.new("RGB", (sw, sh + bar), (255, 255, 255))
    scr.paste(screen.resize((sw, sh), Image.LANCZOS), (0, bar))
    sd = ImageDraw.Draw(scr)
    t = font("Inter.ttf", int(bar * 0.33), "SemiBold")
    sd.text((int(sw * 0.12), int(bar * 0.30)), "9:41", font=t, fill=(17, 17, 17))
    iw, ih = int(sw * 0.30), int(bar * 0.62)
    sd.rounded_rectangle(((sw - iw) // 2, int(bar * 0.18), (sw + iw) // 2, int(bar * 0.18) + ih), radius=ih // 2, fill=(0, 0, 0))
    x = int(sw * 0.80); yb = int(bar * 0.62); u = max(2, int(bar * 0.05))
    for i in range(4):
        hh = int(bar * (0.10 + 0.06 * i))
        sd.rounded_rectangle((x + i * u * 2, yb - hh, x + i * u * 2 + u + 1, yb), radius=1, fill=(17, 17, 17))
    bx = x + 9 * u
    sd.rounded_rectangle((bx, yb - int(bar * 0.26), bx + int(bar * 0.48), yb), radius=u, outline=(17, 17, 17), width=max(2, u // 2))
    sd.rectangle((bx + u, yb - int(bar * 0.26) + u, bx + int(bar * 0.48) - u, yb - u), fill=(17, 17, 17))
    hw = int(sw * 0.33)
    sd.rounded_rectangle(((sw - hw) // 2, sh + bar - int(bar * 0.16), (sw + hw) // 2, sh + bar - int(bar * 0.10)), radius=4, fill=(17, 17, 17))
    m = Image.new("L", scr.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, scr.width - 1, scr.height - 1), radius=r_out - bez, fill=255)
    body.paste(scr, (bez, bez), m)
    return body


PHONE_CACHE = {}


def app_frame(fr, W, H, text, pill, zoom=1.0):
    canvas = Image.new("RGB", (W, H), PAGE).convert("RGBA")
    lines = wrap_lines(text)
    size = int(W * (0.085 if len(lines) == 1 else 0.062))
    f = font("SpaceGrotesk.ttf", size, "Bold")
    d = ImageDraw.Draw(canvas)
    lh = int(size * 1.12)
    head_top = int(H * 0.07) if H > W * 1.5 else int(H * 0.05)
    x = int(W * 0.075)
    for i, ln in enumerate(lines):
        d.text((x, head_top + i * lh), ln, font=f, fill=SLATE if i == 0 else BLUE)
    rule_y = head_top + lh * len(lines) + int(size * 0.25)
    d.rectangle((x, rule_y, x + int(W * 0.12), rule_y + max(6, int(W * 0.007))), fill=BLUE)
    area_top = rule_y + int(H * 0.035)
    area_h = H - area_top - int(H * 0.03)
    # phone sized to the space left: height-limited on every ratio
    ratio = (fr.height / fr.width)
    # 9:16 fits the whole phone; on 4:5 and 1:1 the phone keeps a readable size and runs off the bottom edge
    inner_w = int(W * 0.62) if H > W * 1.5 else int(W * 0.70)
    ph = phone(fr, inner_w)
    if zoom > 1.001:
        # camera push on the phone: scale around the photo strip (upper left of the screen), clipped to the area
        zw, zh = int(ph.width * zoom), int(ph.height * zoom)
        big = ph.resize((zw, zh), Image.LANCZOS)
        fx, fy = 0.24, 0.17                      # focus: the cover photo in the sell form
        px = (W - ph.width) // 2 + int(ph.width * fx) - int(zw * fx)
        py = area_top + int(ph.height * fy) - int(zh * fy)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(big, (px, py), big)
        clip = Image.new("L", (W, H), 0)
        ImageDraw.Draw(clip).rectangle((0, area_top - int(H * 0.012), W, H), fill=255)
        layer.putalpha(Image.fromarray(np.minimum(np.array(layer.getchannel("A")), np.array(clip))))
        canvas.alpha_composite(layer)
    else:
        canvas.alpha_composite(ph, ((W - ph.width) // 2, area_top))
    return canvas.convert("RGB")


def end_card(W, H):
    c = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(c)
    x = int(W * 0.075)
    tall = H > W * 1.5
    size = int(W * (0.115 if tall else 0.1))
    f = font("SpaceGrotesk.ttf", size, "Bold")
    lh = int(size * 1.05)
    y = int(H * (0.26 if tall else 0.14))
    for i, ln in enumerate(["Too big to ship?", "List it free."]):
        d.text((x, y + i * lh), ln, font=f, fill=SLATE if i == 0 else BLUE)
    y += lh * 2 + int(size * 0.35)
    d.rectangle((x, y, x + int(W * 0.24), y + max(8, int(W * 0.009))), fill=BLUE)
    y += int(size * 0.75)
    small = font("Inter.ttf", int(W * 0.041), "SemiBold")
    for ln in ["The AI writes the listing from your photos.", "No selling fee. Local pickup."]:
        d.text((x, y), ln, font=small, fill=INK)
        y += int(W * 0.066)
    # logo + wordmark + url
    icon_h = int(W * 0.13)
    logo = Image.open(LOGO).convert("RGBA").resize((icon_h, icon_h), Image.LANCZOS)
    m = Image.new("L", logo.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, icon_h - 1, icon_h - 1), radius=int(icon_h * 0.22), fill=255)
    logo.putalpha(Image.fromarray(np.minimum(np.array(logo.getchannel("A")), np.array(m))))
    wm = Image.open(WORDMARK).convert("RGBA")
    wh = int(icon_h * 0.5)
    wm = wm.resize((int(wm.width * wh / wm.height), wh), Image.LANCZOS)
    by = int(H * (0.78 if tall else 0.74))
    c.paste(logo, (x, by), logo)
    c.paste(wm, (x + icon_h + int(W * 0.035), by + (icon_h - wh) // 2), wm)
    url = font("Inter.ttf", int(W * 0.042), "SemiBold")
    d.text((x, by + icon_h + int(W * 0.04)), "yardswaps.com", font=url, fill=SLATE)
    return c


def build(ratio):
    W, H = SIZES[ratio]
    pill = wordmark_pill(W)
    out = os.path.join(HERE, "out", f"yardswaps-too-big-to-ship-v3-{ratio}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    silent = out.replace(".mp4", "-silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    endc = end_card(W, H)
    total = 0
    for (a, b, kind, slug, cap, cin) in TIMELINE:
        n = int(round(b * FPS)) - int(round(a * FPS))
        if kind == "item":
            clip = os.path.join(HERE, "clips", slug + ".mp4")
            frames = read_frames(clip, cin, n) if os.path.exists(clip) else photo_frames(slug, n)
            bottom = int(H * 0.955) if H > W * 1.5 else int(H * 0.92)
            capl = caption_layer(W, H, cap, bottom)
            for fr in frames[:n]:
                ff.stdin.write(item_frame(fr, W, H, capl, pill).tobytes())
        elif kind == "app":
            frames = app_frames(cin, n)
            first = (a == 7.75)
            for i, fr in enumerate(frames[:n]):
                # "List it free.": hold close on the booster photo going in, then ease back out to the whole phone
                z = 1.0 + 1.0 * (1 - ease((i - n * 0.55) / (n * 0.45))) if first else 1.0
                ff.stdin.write(app_frame(fr, W, H, cap, pill, z).tobytes())
        else:
            for i in range(n):
                ff.stdin.write(endc.tobytes())
        total += n
    ff.stdin.close(); ff.wait()
    vo = os.path.join(HERE, "audio", "vo.mp3")
    mu = os.path.join(HERE, "audio", "music.mp3")
    fc = (f"[1:a]adelay={int(VO_OFFSET*1000)}|{int(VO_OFFSET*1000)},volume=1.0[v];"
          f"[2:a]atrim=0:{DURATION},afade=t=out:st={DURATION-1.2}:d=1.2,volume=0.22[m];"
          f"[v][m]amix=inputs=2:duration=longest:normalize=0,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", vo, "-i", mu, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-t", str(DURATION), "-movflags", "+faststart", out], check=True)
    os.remove(silent)
    print(out, total / FPS)


if __name__ == "__main__":
    for r in (sys.argv[1:] or ["9x16", "4x5", "1x1"]):
        build(r)
