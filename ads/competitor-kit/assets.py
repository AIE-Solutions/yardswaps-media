# Still assets for the competitor-style ads: shot captions, walkthrough phone + captions, end cards.
# Vertical 1080x1920 and wide 1920x1080. Usage: python3 assets.py <spec.json> <outdir>
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

K = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(K, "../brand-commercial-v2/source/fonts/SpaceGrotesk_700Bold.ttf")
V2END = os.path.join(K, "../brand-commercial-v2/source/endcard.png")  # source of the wordmark + official store badges
BLUE, SLATE, GRAY, BG = (37, 99, 235, 255), (26, 51, 83, 255), (84, 84, 86, 255), (246, 246, 248)
spec = json.load(open(sys.argv[1])); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
f = lambda s: ImageFont.truetype(FONT, s)


def shot_caption(text, W, H, X, BOTTOM, size, LH, maxw, grad=True):
    F = f(size); ls = text.split("|")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if grad:  # soft dark gradient behind the words for legibility
        g = Image.new("L", (1, H), 0)
        for y in range(H):
            t = (y - (BOTTOM - LH * len(ls) - 260)) / (H - (BOTTOM - LH * len(ls) - 260))
            g.putpixel((0, y), 0 if t < 0 else min(150, int(150 * t ** 1.4)))
        img = Image.composite(Image.new("RGBA", (W, H), (8, 14, 24, 255)), img, g.resize((W, H)))
    d = ImageDraw.Draw(img)
    assert all(d.textlength(l, font=F) <= maxw for l in ls), (text, [d.textlength(l, font=F) for l in ls])
    top = BOTTOM - LH * len(ls)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for i, l in enumerate(ls): sd.text((X, top + i * LH), l, font=F, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(img)
    d.rounded_rectangle((X, top - 40, X + 84, top - 28), radius=6, fill=BLUE)
    for i, l in enumerate(ls): d.text((X, top + i * LH), l, font=F, fill=(255, 255, 255, 255))
    return img


def phone(W, H, SW, SH, X0, Y0, BZ, R_IN, R_OUT, name):
    ow, oh = SW + 2 * BZ, SH + 2 * BZ
    bz = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(bz)
    d.rounded_rectangle((X0 - BZ, Y0 - BZ, X0 - BZ + ow, Y0 - BZ + oh), radius=R_OUT, fill=(18, 20, 24, 255))
    d.rounded_rectangle((X0 - BZ + 3, Y0 - BZ + 3, X0 - BZ + ow - 3, Y0 - BZ + oh - 3), radius=R_OUT - 3, outline=(60, 64, 72, 255), width=2)
    hole = Image.new("L", (W, H), 0); ImageDraw.Draw(hole).rounded_rectangle((X0, Y0, X0 + SW, Y0 + SH), radius=R_IN, fill=255)
    bz.putalpha(Image.composite(Image.new("L", (W, H), 0), bz.getchannel("A"), hole)); bz.save(f"{OUT}/bezel-{name}.png")
    bg = Image.new("RGB", (W, H), BG); sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle((X0 - BZ + 10, Y0 - BZ + 40, X0 - BZ + ow - 10, Y0 - BZ + oh + 30), radius=R_OUT, fill=70)
    Image.composite(Image.new("RGB", (W, H), SLATE[:3]), bg, sh.filter(ImageFilter.GaussianBlur(40))).save(f"{OUT}/appbg-{name}.png")


def walk_caps(name, W, H, size, pos):
    F = f(size)
    for k, (l1, l2) in enumerate(spec["walk_caps"], 1):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for i, (t, c) in enumerate([(l1, SLATE), (l2, BLUE)]):
            x, y = pos(d.textlength(t, font=F), i); d.text((x, y), t, font=F, fill=c)
        im.save(f"{OUT}/w{k}-{name}.png")


# end card pieces cut from the v2 card so the wordmark and badges stay the official artwork
v2 = Image.open(V2END).convert("RGB")
WM = v2.crop((180, 585, 900, 745)); BADGES = v2.crop((190, 975, 890, 1090))


def endcard(W, H, name):
    e = spec["end"]; im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    wide = W > H
    s = 0.92 if wide else 1.0
    wm = WM.resize((int(WM.width * s), int(WM.height * s)), Image.LANCZOS)
    bd = BADGES.resize((int(BADGES.width * s), int(BADGES.height * s)), Image.LANCZOS)
    F1, F2, F3, FQ = f(int(66 * s)), f(int(46 * s)), f(int(46 * s)), f(int(56 * s))
    y = int((H * 0.5) - (560 * s)) if not wide else 90
    im.paste(wm, ((W - wm.width) // 2, y)); y += wm.height + int(60 * s)
    for t, F, c, gap in [(e["line1"], F1, SLATE, 18), (e["line2"], F2, GRAY, 40)]:
        while d.textlength(t, font=F) > W - 100: F = f(F.size - 2)  # shrink a long line to fit
        w = d.textlength(t, font=F); d.text(((W - w) / 2, y), t, font=F, fill=c); y += F.size + int(gap * s)
    im.paste(bd, ((W - bd.width) // 2, y)); y += bd.height + int(44 * s)
    w = d.textlength("yardswaps.com", font=F3); d.text(((W - w) / 2, y), "yardswaps.com", font=F3, fill=BLUE); y += F3.size + int(60 * s)
    q = e["q"]; w = d.textlength(q, font=FQ); pad = int(38 * s)
    d.rounded_rectangle(((W - w) / 2 - pad, y, (W + w) / 2 + pad, y + FQ.size + 2 * int(24 * s)), radius=int(26 * s), fill=BLUE)
    d.text(((W - w) / 2, y + int(20 * s)), q, font=FQ, fill=(255, 255, 255))
    assert y + FQ.size + 60 < H, ("end card overflows", name)
    # centre the block vertically
    bot = y + FQ.size + 2 * int(24 * s); top = int((H * 0.5) - (560 * s)) if not wide else 90
    shift = (H - (bot - top)) // 2 - top
    out = Image.new("RGB", (W, H), BG); out.paste(im.crop((0, 0, W, H)), (0, shift)) if shift >= 0 else out.paste(im.crop((0, -shift, W, H)), (0, 0))
    if shift > 0: ImageDraw.Draw(out).rectangle((0, 0, W, shift), fill=BG)
    out.save(f"{OUT}/end-{name}.png")


for i, s in enumerate(spec["shots"]):
    if not s.get("cap"): continue
    shot_caption(s["cap"], 1080, 1920, 84, 1560, 88, 100, 912).save(f"{OUT}/t{i}-v.png")
    # wide: words on the right of the vertical panel, on the dimmed backdrop
    shot_caption(s["cap"], 1920, 1080, 960, 640, 84, 96, 900, grad=False).save(f"{OUT}/t{i}-w.png")
phone(1080, 1920, 744, 1473, 168, 330, 22, 86, 106, "v")
walk_caps("v", 1080, 1920, 66, lambda w, i: ((1080 - w) / 2, 92 + i * 84))
phone(1920, 1080, 456, 904, 360, 88, 14, 54, 66, "w")
walk_caps("w", 1920, 1080, 76, lambda w, i: (960, 400 + i * 96))
endcard(1080, 1920, "v"); endcard(1920, 1080, "w")
print("assets ok", OUT)
