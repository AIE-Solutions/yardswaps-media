#!/usr/bin/env python3
"""YardSwaps storefront Meta ads, v2: hook in the first 2 s, Justin Case voiceover,
captions synced to each line, branded frame, real app recordings, founding offer card.

usage: make_ad.py <ad-id> <aspect 9x16|4x5> <narration dir> <out.mp4>
Frames are drawn with PIL and piped to ffmpeg; audio = voice lines + music bed ducked.
"""
import json, os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = "/home/user/yardswaps-media"
LIB = f"{MEDIA}/reels/library"
PHOTOS = f"{MEDIA}/broll/in/brand-kit/site-listings"
MUSIC = f"{MEDIA}/music/v2/yardswaps-music-clean-120bpm.mp3"
FPS = 30

# brand tokens (CLAUDE.md :root)
BG = (246, 246, 248); SLATE = (26, 51, 83); BLUE = (37, 99, 235); BLUE_D = (28, 72, 158)
DEEP = (14, 34, 64); TEXT2 = (84, 84, 86); WHITE = (255, 255, 255)

def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, name), size)
SG = "SpaceGrotesk_700Bold.ttf"; IS = "Inter_600SemiBold.ttf"; IM = "Inter_500Medium.ttf"

# ---------- ad definitions ----------
SEG = {  # (source reel slug, start s, end s): phone-only stretches, no headline cards
    "storefront": ("whole-lot-one-link", 5.2, 9.8),
    "socials": ("socials-on-storefront", 5.6, 8.4),
    "import": ("import-from-your-website", 5.1, 10.4),
    "stats": ("storefront-stats", 5.2, 10.4),
    "demand": ("see-what-buyers-want-v2", 5.1, 7.72),
}
GRID_A = ["fleet-2007-freightliner-business-class-m2-106-grapple-tr.jpg", "forklifts-2014-sky-trak-6042-telehandler.jpg",
          "hvac-goodman-condenser-air-handler-hvac-split-system.jpg", "pressure-hotsy-hot-water-pressure-washer-cart.jpg",
          "machining-kennedy-brown-wrinkle-tool-chest-and-roller-cabine.jpg", "trailers-2001-american-spray-technologies-spray-tek-150-1g.jpg"]
GRID_B = ["fleet-2019-hino-268-box-truck-168k-miles.jpg", "landscaping-2019-atmax-mowermax-bm-boom-mower-high-flow-4wd.jpg",
          "warehouse-floor-scrubber.jpg", "machining-mitutoya-outside-micrometer-set-large.jpg"]

ADS = {
  "b1-tour": [
    dict(kind="grid", photos=GRID_A, title=["Every unit you sell.", "One storefront."], vo="tour-1"),
    dict(kind="app", seg="storefront", title="Your storefront", vo="tour-2"),
    dict(kind="app", seg="socials", title="Your socials", vo="tour-3"),
    dict(kind="app", seg="import", title="Import from your website", vo="tour-4"),
    dict(kind="app", seg="stats", title="Stats on every unit", vo="tour-5"),
    dict(kind="app", seg="demand", title="Buyer demand near you", vo="tour-6"),
    dict(kind="end", vo="offer"),
  ],
  "b2-import": [
    dict(kind="grid", photos=GRID_B, title=["Already on your", "own website?"], vo="imp-1"),
    dict(kind="app", seg="import", title="Import from your website", vo="imp-2", extra="imp-3"),
    dict(kind="end", vo="offer"),
  ],
  "b3-stats": [
    dict(kind="single", photo="pressure-hotsy-hot-water-pressure-washer-cart.jpg", title=["Which units do", "buyers look at?"], vo="sta-1"),
    dict(kind="app", seg="stats", title="Stats on every unit", vo="sta-2", extra="sta-3"),
    dict(kind="end", vo="offer"),
  ],
  "b4-demand": [
    dict(kind="single", photo="forklifts-2014-sky-trak-6042-telehandler.jpg", title=["What are buyers", "near you searching?"], vo="dem-1"),
    dict(kind="app", seg="demand", title="Buyer demand near you", vo="dem-2", extra="dem-3"),
    dict(kind="end", vo="offer"),
  ],
}
LINES = {}
def load_lines(ndir):
    for row in open(os.path.join(ndir, "lines.tsv")):
        f, _v, _m, _l, text = row.rstrip("\n").split("\t", 4)
        LINES[f[len("meta-"):-4]] = (os.path.join(ndir, f), text)

def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())

# ---------- layout ----------
class L:
    def __init__(self, aspect):
        self.W, self.H = (1080, 1920) if aspect == "9x16" else (1080, 1350)
        tall = aspect == "9x16"
        self.tall = tall
        self.chip_y = 250 if tall else 54          # Reels: keep the top 14% clear
        self.title_y = 330 if tall else 112
        self.title_px = 74 if tall else 58
        self.cap_y = 430 if tall else 186
        self.cap_px = 40 if tall else 32
        self.phone_y = 610 if tall else 300
        self.phone_scale = 1.12 if tall else 0.98
        self.hook_px = 92 if tall else 72
        self.hook_y = 320 if tall else 96

# ---------- drawing helpers ----------
def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def wrap_bal(draw, text, fnt, maxw):
    """Wrap, then narrow the width so the last line isn't a lone word."""
    lines = wrap(draw, text, fnt, maxw); n = len(lines); best = lines
    w = maxw
    while n > 1 and w > maxw * 0.55:
        w -= 20; t = wrap(draw, text, fnt, w)
        if len(t) != n: break
        best = t
    return best

CAP_SUBS = {"over thirty, ninety or a hundred and eighty days": "over 30, 90 or 180 days", "thirty days": "30 days"}

def chunks_for(text, draw, fnt, maxw):
    """Split a voice line into caption chunks of at most 2 wrapped lines."""
    for a, b in CAP_SUBS.items(): text = text.replace(a, b)
    parts, out = [], []
    for sent in text.replace("? ", "?|").replace(". ", ".|").split("|"):
        parts.append(sent.strip())
    for p in parts:
        ls = wrap(draw, p, fnt, maxw)
        if len(ls) <= 2: out.append(p); continue
        # split long sentence at commas, else by words
        bits = [b.strip() for b in p.split(",")]
        cur = ""
        for b in bits:
            t = (cur + ", " + b) if cur else b
            if len(wrap(draw, t, fnt, maxw)) <= 2: cur = t
            else:
                if cur: out.append(cur + ",")
                cur = b
        if cur: out.append(cur)
    final = []
    for c in [c for c in out if c]:
        if len(wrap(draw, c, fnt, maxw)) <= 2: final.append(c); continue
        # no comma to split at: break by words, filling up to 2 lines each
        cur = ""
        for w in c.split():
            t = (cur + " " + w).strip()
            if len(wrap(draw, t, fnt, maxw)) <= 2: cur = t
            else: final.append(cur); cur = w
        if cur: final.append(cur)
    # avoid a 1-2 word tail chunk: move words back from the previous chunk
    if len(final) > 1 and len(final[-1].split()) <= 4:
        prev = final[-2].split(); tail = final[-1].split()
        while len(tail) < 5 and len(prev) > 3:
            tail.insert(0, prev.pop())
        final[-2], final[-1] = " ".join(prev), " ".join(tail)
    return final

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def text_center(d, y, text, fnt, fill, W):
    w = d.textlength(text, font=fnt); d.text(((W - w) / 2, y), text, font=fnt, fill=fill)

def pill(d, cx, y, text, fnt, fg, bg, padx=26, pady=12):
    w = d.textlength(text, font=fnt); bb = fnt.getbbox("Ag"); h = bb[3] - bb[1]
    x0 = cx - w / 2 - padx; d.rounded_rectangle([x0, y, x0 + w + 2 * padx, y + h + 2 * pady], radius=999, fill=bg)
    d.text((cx - w / 2, y + pady - bb[1]), text, font=fnt, fill=fg)
    return y + h + 2 * pady

def contain(img, w, h, bg=WHITE):
    im = img.copy(); im.thumbnail((w, h), Image.LANCZOS)
    c = Image.new("RGB", (w, h), bg); c.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return c

def cover(img, w, h):
    r = max(w / img.width, h / img.height); im = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2; return im.crop((x, y, x + w, y + h))

def shadow_card(base, card, x, y, radius=28, alpha=255):
    mask = Image.new("L", card.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=radius, fill=alpha)
    sh = Image.new("L", (card.width + 60, card.height + 60), 0)
    ImageDraw.Draw(sh).rounded_rectangle([30, 38, card.width + 30, card.height + 38], radius=radius, fill=int(40 * alpha / 255))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    base.paste(Image.new("RGB", sh.size, SLATE), (x - 30, y - 30), sh)
    base.paste(card, (x, y), mask)

def chip(d, lay, alpha=1.0):
    f = font(IS, 30 if lay.tall else 26)
    pill(d, lay.W / 2, lay.chip_y, "YardSwaps storefront", f, WHITE, BLUE)

# ---------- source video frames ----------
def read_segment(slug, t0, t1, crop=(196, 456, 884, 1500)):
    """Return list of phone-crop frames (PIL) from the source reel."""
    x0, y0, x1, y1 = crop; w, h = x1 - x0, y1 - y0
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", f"{LIB}/yardswaps-{slug}-9x16.mp4",
           "-vf", f"crop={w}:{h}:{x0}:{y0},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.check_output(cmd); n = len(raw) // (w * h * 3)
    arr = np.frombuffer(raw, np.uint8).reshape(n, h, w, 3)
    return [Image.fromarray(a) for a in arr]

# ---------- scenes ----------
def scene_frames(sc, lay, nframes, cap_chunks):
    W, H = lay.W, lay.H
    capf = font(IS, lay.cap_px)
    def draw_caption(d, i):
        if not cap_chunks: return
        t = i / FPS; cur = cap_chunks[-1][1]
        for (st, txt) in cap_chunks:
            if t >= st: cur = txt
        lines = wrap_bal(d, cur, capf, W - 160)
        y = lay.cap_y
        for ln in lines[:2]:
            text_center(d, y, ln, capf, TEXT2, W); y += int(lay.cap_px * 1.3)

    if sc["kind"] in ("grid", "single"):
        if sc["kind"] == "grid":
            photos = [Image.open(os.path.join(PHOTOS, p)).convert("RGB") for p in sc["photos"]]
            cols = 2; rows = math.ceil(len(photos) / cols)
            top = (lay.hook_y + 2 * int(lay.hook_px * 1.1) + 150) if lay.tall else (lay.hook_y + 2 * int(lay.hook_px * 1.1) + 120)
            bottom = H - (190 if lay.tall else 40)
            gap = 22; tw = (W - 2 * 70 - gap) // cols; th = min(tw * 3 // 4, (bottom - top - gap * (rows - 1)) // rows)
            tiles = [contain(p, tw, th, WHITE) for p in photos]
        else:
            ph = Image.open(os.path.join(PHOTOS, sc["photo"])).convert("RGB")
            bgimg = cover(ph, W, H).filter(ImageFilter.GaussianBlur(28))
            bgimg = Image.blend(bgimg, Image.new("RGB", (W, H), BG), 0.55)
        hookf = font(SG, lay.hook_px)
        for i in range(nframes):
            if sc["kind"] == "grid":
                fr = Image.new("RGB", (W, H), BG)
                gx0 = (W - (cols * tw + (cols - 1) * gap)) // 2
                for k, tile in enumerate(tiles):
                    a = ease((i - 2 - k * 3) / 7)
                    if a <= 0: continue
                    s = 0.86 + 0.14 * a
                    tt = tile.resize((int(tw * s), int(th * s)), Image.LANCZOS)
                    cx = gx0 + (k % cols) * (tw + gap) + tw // 2; cy = top + (k // cols) * (th + gap) + th // 2
                    shadow_card(fr, tt, cx - tt.width // 2, cy - tt.height // 2 + int((1 - a) * 30), radius=22, alpha=int(255 * a))
            else:
                fr = bgimg.copy()
                z = 1.0 + 0.06 * (i / max(1, nframes))  # slow push on the real item
                pw, phh = int((W - 120) * z), int((H * (0.56 if lay.tall else 0.58)) * z)
                card = contain(ph, pw, phh, WHITE)
                ty = (lay.hook_y + 2 * int(lay.hook_px * 1.1) + (150 if lay.tall else 120))
                shadow_card(fr, card, (W - pw) // 2, ty, radius=28)
            d = ImageDraw.Draw(fr); chip(d, lay)
            a = ease(i / 8); y = lay.hook_y + 40 + int((1 - a) * 30)
            for j, ln in enumerate(sc["title"]):
                text_center(d, y + j * int(lay.hook_px * 1.1), ln, hookf, SLATE if j == 0 else BLUE, W)
            # offer sticker under the hook from the first second
            if i >= 10:
                sf = font(IS, 34 if lay.tall else 28)
                pill(d, W / 2, y + 2 * int(lay.hook_px * 1.1) + 16, "Storefront free for 30 days", sf, WHITE, SLATE)
            yield fr
        return

    if sc["kind"] == "app":
        slug, t0, t1 = SEG[sc["seg"]]
        src = read_segment(slug, t0, t1)
        # stretch the clip to the voice if needed (max 1.35x slower), then hold the last frame
        span = len(src); rate = min(1.0, max(span / max(1, nframes), 1 / 1.35))
        tf = font(SG, lay.title_px)
        for i in range(nframes):
            k = min(span - 1, int(i * rate))
            ph = src[k]
            pw, phh = int(ph.width * lay.phone_scale), int(ph.height * lay.phone_scale)
            ph = ph.resize((pw, phh), Image.LANCZOS)
            fr = Image.new("RGB", (W, H), BG)
            a = ease(i / 7)
            fr.paste(ph, ((W - pw) // 2, lay.phone_y + int((1 - a) * 40)))
            d = ImageDraw.Draw(fr); chip(d, lay)
            text_center(d, lay.title_y, sc["title"], tf, SLATE, W)
            draw_caption(d, i)
            yield fr
        return

    if sc["kind"] == "end":
        T = lay.tall
        big = font(SG, 136 if T else 112); h1 = font(SG, 76 if T else 62)
        sub = font(IS, 48 if T else 40); small = font(IM, 38 if T else 32); urlf = font(IS, 42 if T else 36)
        grad = Image.new("RGB", (W, H)); gd = ImageDraw.Draw(grad)
        for y in range(H):
            t = y / H; c = tuple(int(BLUE[j] * (1 - t) + BLUE_D[j] * t) for j in range(3)); gd.line([(0, y), (W, y)], fill=c)
        SOFT = (220, 230, 252)
        items = [("YardSwaps", big, WHITE, 0, 170 if T else 140), ("Storefront: 30 days free", h1, WHITE, 1, 128 if T else 104),
                 ("Then $29 a month for your first", sub, WHITE, 2, 64 if T else 54), ("3 paid months, then $49.", sub, WHITE, 2, 110 if T else 90),
                 ("First 100 storefronts. Open before Dec 1.", small, SOFT, 3, 54 if T else 46),
                 ("Cancel before day 30 and pay nothing.", small, SOFT, 3, 100 if T else 80)]
        block = sum(it[4] for it in items) + 80
        # Reels: keep text between the top 14% and the bottom 35%; Feeds (4:5) use the whole frame
        lo, hi = (270, int(H * 0.65)) if T else (0, H)
        base_y = lo + (hi - lo - block) // 2
        for i in range(nframes):
            fr = grad.copy(); y = base_y
            for (txt, f, col, step, g) in items:
                a = ease((i - step * 5) / 9)
                if a > 0:
                    yy = y + int((1 - a) * 24)
                    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
                    text_center(ld, yy, txt, f, col + (int(255 * a),), W); fr.paste(layer, (0, 0), layer)
                y += g
            if i > 24:
                d = ImageDraw.Draw(fr)
                pill(d, W / 2, y, "yardswaps.com/dealers", urlf, BLUE, WHITE, padx=34, pady=16)
            yield fr
        return

# ---------- build ----------
def build(ad, aspect, ndir, out):
    load_lines(ndir); lay = L(aspect); scenes = ADS[ad]
    tmpd = Image.new("RGB", (10, 10)); dd = ImageDraw.Draw(tmpd); capf = font(IS, lay.cap_px)
    plan, t = [], 0.0
    for sc in scenes:
        vo = [sc["vo"]] + ([sc["extra"]] if sc.get("extra") else [])
        lead = 0.25 if sc["kind"] != "grid" and sc["kind"] != "single" else 0.15
        voice, cur = [], lead
        caps = []
        for v in vo:
            path, text = LINES[v]; dv = dur(path)
            voice.append((t + cur, path))
            if sc["kind"] == "app":
                chs = chunks_for(text, dd, capf, lay.W - 160); tot = sum(len(c) for c in chs); st = cur
                for c in chs:
                    caps.append((st, c)); st += dv * len(c) / tot
            cur += dv + 0.25
        length = cur + (0.35 if sc["kind"] != "end" else 1.2)
        plan.append((sc, int(round(length * FPS)), caps, voice)); t += length
    total = t
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{lay.W}x{lay.H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out + ".video.mp4"], stdin=subprocess.PIPE)
    for sc, n, caps, _ in plan:
        for fr in scene_frames(sc, lay, n, caps):
            ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()
    # audio: voice lines at their starts, music bed under them, ducked, loudness to -14 LUFS
    voices = [v for _, _, _, vs in plan for v in vs]
    inputs = ["-i", out + ".video.mp4", "-stream_loop", "-1", "-i", MUSIC]
    filt = []
    for j, (st, p) in enumerate(voices):
        inputs += ["-i", p]; filt.append(f"[{j+2}:a]adelay={int(st*1000)}|{int(st*1000)},aresample=48000[v{j}]")
    mixv = "".join(f"[v{j}]" for j in range(len(voices)))
    filt.append(f"{mixv}amix=inputs={len(voices)}:normalize=0,apad,atrim=0:{total:.3f}[vo]")
    filt.append(f"[1:a]atrim=0:{total:.3f},aresample=48000,volume=0.22,afade=t=out:st={total-1.0:.3f}:d=1.0[bed]")
    filt.append("[vo]asplit[vo1][vo2];[bed][vo1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck]")
    filt.append("[duck][vo2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[a]",
                           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", out])
    os.remove(out + ".video.mp4")
    print(out, f"{total:.2f}s")

if __name__ == "__main__":
    build(*sys.argv[1:5])
