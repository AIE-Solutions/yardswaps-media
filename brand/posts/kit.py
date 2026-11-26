#!/usr/bin/env python3
"""YardSwaps post kit: one designed look for every still post and Reel frame.

Alan, 2026-11-26: "we need to improve quality of post and imagery and branding ... whatever we are sending to the
socials looks like ai slop". Before this, each pipeline drew its own frame: a small photo on a blurred copy of
itself, an AI backdrop on the daily Story, small type, no logo until the end card.

The look (brand colours and fonts only, CLAUDE.md of the app repo):
- a REAL listing photo, big and sharp (never an AI or stock picture, never a blurred fill);
- the YardSwaps wordmark on a white tab, top left, on every frame;
- a bold Space Grotesk headline, one line on a blue highlight bar;
- a brand slate panel (#1A3353) under the photo for the words, so type is never on a busy picture;
- feed posts end in the brand bar (wordmark, "Buy and sell used equipment", blue stripes).

Pillow only, so every workflow can use it (the listings job has no browser).

    tip_post(photo, kicker, headline, body, tip, ...)      1080x1350 feed post, or 1080x1920 with tall=True
    listing_post(photo, title, price, facts, label)        1080x1350 feed post
    story(photo, headline, body, label, line, ...)         1080x1920 Story
    reel_frame(photos, title, price, facts, label)         1080x1920 base frame + where each photo goes
                                                            (listings/listing_reels.py animates the photos)

Headline lines are a list; a line starting with "*" gets the blue bar. Copy follows MESSAGING.md.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS = os.path.join(ROOT, "listings", "fonts")

LOOK = "k1"   # bump when the look changes; listing Reels re-make older clips that carry another value
W = 1080
FEED_H, TALL_H = 1350, 1920
WHITE, BLUE = (255, 255, 255), (37, 99, 235)
SLATE, DEEP = (26, 51, 83), (14, 34, 64)   # brand slate (--slate-brand) and its deep stop (--slate-deep)
PANEL, BOX = SLATE, DEEP   # the text panel, and what sits on it: the tip box, the feed bar, the top shade
SOFT, KICK = (220, 229, 244), (170, 196, 255)
HI = BLUE   # the highlight: the bar under a headline line, the tip label, the Reel pill
# Stories and Reels: nothing to read in the top 150 px or the bottom 340 px (the apps' own buttons sit there).
SAFE_TOP, SAFE_BOTTOM = 150, 340
BAR_H = 118


def font(name, size, weight):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def sg(size):
    return font("SpaceGrotesk.ttf", size, b"Bold")


def inter(size, weight=b"SemiBold"):
    return font("Inter.ttf", size, weight)


def tracked_width(d, text, f, tracking):
    return sum(d.textlength(c, font=f) for c in text) + tracking * f.size * max(len(text) - 1, 0)


def tracked(d, xy, text, f, fill, tracking):
    """Draw text with letter spacing (in em). Returns its width."""
    x, y = xy
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tracking * f.size
    return x - xy[0] - tracking * f.size


def wrap(d, text, f, width, max_lines=None):
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while d.textlength(lines[-1] + "…", font=f) > width and " " in lines[-1]:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1].rstrip(",;:-") + "…"
    return lines


# ---------- blocks: each is (height, draw(img, d, x, y)) so a column can be laid out from the bottom up ----------

def b_kicker(d, text, size=34):
    f = sg(size)

    def draw(img, d, x, y):
        tracked(d, (x, y), text.upper(), f, KICK, 0.14)
    return size + 6, draw


def b_headline(d, lines, width, max_size, upper=True):
    """The biggest size at which every line fits the column; "*" lines sit on the blue bar."""
    texts = [(ln[1:], True) if ln.startswith("*") else (ln, False) for ln in lines]
    if upper:
        texts = [(t.upper(), h) for t, h in texts]
    size = max_size
    while size > 56:
        f = sg(size)
        if all(d.textlength(t, font=f) + (0.3 * size if h else 0) <= width for t, h in texts):
            break
        size -= 2
    f = sg(size)
    lh = int(size * 1.1)

    def draw(img, d, x, y):
        for i, (t, hl) in enumerate(texts):
            ty = y + i * lh
            if hl:
                tw = d.textlength(t, font=f)
                px = int(0.15 * size)
                d.rounded_rectangle((x - px, ty + int(0.06 * size), x + tw + px, ty + int(1.08 * size)), 8, fill=HI)
            d.text((x, ty), t, font=f, fill=WHITE)
    return len(texts) * lh + int(size * 0.08), draw


def b_title(d, text, width, size, max_lines=2):
    """A listing title, sentence case. Long titles step down a size before they are ever cut short."""
    f = sg(size)
    lines = wrap(d, text, f, width, max_lines)
    while lines[-1].endswith("…") and size > 44:
        size -= 4
        f = sg(size)
        lines = wrap(d, text, f, width, max_lines + 1)
    lh = int(size * 1.14)

    def draw(img, d, x, y):
        for i, ln in enumerate(lines):
            d.text((x, y + i * lh), ln, font=f, fill=WHITE)
    return len(lines) * lh, draw


def b_text(d, text, width, size, fill=(238, 243, 251), weight=b"SemiBold"):
    f = inter(size, weight)
    lines = wrap(d, text, f, width)
    lh = int(size * 1.34)

    def draw(img, d, x, y):
        for i, ln in enumerate(lines):
            d.text((x, y + i * lh), ln, font=f, fill=fill)
    return len(lines) * lh, draw


def b_price(d, price, facts, width, size, facts_size):
    """Price, with the facts on the same line when they fit, else under it."""
    pf, ff = sg(size), inter(facts_size)
    pw = d.textlength(price, font=pf)
    beside = bool(facts) and pw + 34 + d.textlength(facts, font=ff) <= width
    h = int(size * 1.08) + (0 if beside or not facts else int(facts_size * 1.5))

    def draw(img, d, x, y):
        d.text((x, y - int(size * 0.1)), price, font=pf, fill=WHITE)
        if facts and beside:
            d.text((x + pw + 34, y + int(size * 0.84) - int(facts_size * 1.02)), facts, font=ff, fill=SOFT)
        elif facts:
            d.text((x, y + int(size * 1.06)), facts, font=ff, fill=SOFT)
    return h, draw


def b_tip(d, label, text, width, label_size, text_size):
    lf, tf = sg(label_size), inter(text_size)
    lw = tracked_width(d, label.upper(), lf, 0.1) + 44
    lh_label = label_size + 20
    lines = wrap(d, text, tf, width - 56)
    lh = int(text_size * 1.32)
    box_h = len(lines) * lh + 40
    box_w = min(width, max(d.textlength(ln, font=tf) for ln in lines) + 56)

    def draw(img, d, x, y):
        d.rounded_rectangle((x, y, x + lw, y + lh_label + 14), 12, fill=HI)
        tracked(d, (x + 22, y + 9), label.upper(), lf, WHITE, 0.1)
        top = y + lh_label
        over = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(over)
        od.rounded_rectangle((x, top, x + box_w, top + box_h), 18, fill=BOX + (235,), outline=(255, 255, 255, 46), width=2)
        od.rectangle((x, top, x + 30, top + 20), fill=BOX + (235,))   # square the corner under the label
        od.line((x, top, x, top + 20), fill=(255, 255, 255, 46), width=2)
        img.paste(Image.alpha_composite(img.convert("RGBA"), over).convert("RGB"))
        d2 = ImageDraw.Draw(img)
        for i, ln in enumerate(lines):
            d2.text((x + 28, top + 18 + i * lh), ln, font=tf, fill=WHITE)
    return lh_label + box_h, draw


def column(img, blocks, gaps, x, bottom):
    """Draw blocks stacked upward from `bottom`; returns the y of the column's top."""
    total = sum(h for h, _ in blocks) + sum(gaps[:len(blocks) - 1])
    y = top = bottom - total
    for i, (h, draw) in enumerate(blocks):
        draw(img, ImageDraw.Draw(img), x, y)
        y += h + (gaps[i] if i < len(blocks) - 1 else 0)
    return top


def column_top(blocks, gaps, bottom):
    return bottom - sum(h for h, _ in blocks) - sum(gaps[:len(blocks) - 1])


# ---------- pieces ----------

def cover(photo, w, h, pos=(0.5, 0.5)):
    s = max(w / photo.width, h / photo.height)
    im = photo.resize((max(w, round(photo.width * s)), max(h, round(photo.height * s))), Image.LANCZOS)
    left = round((im.width - w) * pos[0])
    top = round((im.height - h) * pos[1])
    return im.crop((left, top, left + w, top + h))


def melt(img, y0, y1, colour=None):
    """Fade the picture into the panel colour between y0 and y1."""
    colour = colour or PANEL
    h = y1 - y0
    ramp = Image.new("L", (1, h))
    ramp.putdata([int(255 * min(1.0, (i / h) / 0.72) ** 1.6) for i in range(h)])
    img.paste(Image.new("RGB", (img.width, h), colour), (0, y0), ramp.resize((img.width, h)))


def shade_top(img, h=320, strength=0.6):
    ramp = Image.new("L", (1, h))
    ramp.putdata([int(255 * strength * (1 - i / h)) for i in range(h)])
    img.paste(Image.new("RGB", (img.width, h), BOX), (0, 0), ramp.resize((img.width, h)))


def tab(img, x, y, hanging):
    """The wordmark on a white tab. hanging: square top, flush with the frame's top edge."""
    d = ImageDraw.Draw(img)
    f = sg(54)
    tw = tracked_width(d, "YardSwaps", f, -0.035)
    w, h = int(tw) + 68, 104 if hanging else 96
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x, y + 8, x + w, y + h + 8), 26, fill=(10, 24, 48, 80))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(14))).convert("RGB"))
    d = ImageDraw.Draw(img)
    if hanging:
        d.rounded_rectangle((x, y - 30, x + w, y + h), 26, fill=WHITE)
        tracked(d, (x + 34, y + 26), "YardSwaps", f, BLUE, -0.035)
    else:
        d.rounded_rectangle((x, y, x + w, y + h), 22, fill=WHITE)
        tracked(d, (x + 34, y + 17), "YardSwaps", f, BLUE, -0.035)
    return w, h


def pill(img, right, y, text):
    d = ImageDraw.Draw(img)
    f = sg(38)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle((right - tw - 60, y, right, y + 72), 36, fill=HI)
    d.text((right - tw - 30, y + 12), text, font=f, fill=WHITE)


def credit(img, right, y, label, text):
    """Small white chip naming the real listing in the photo."""
    d = ImageDraw.Draw(img)
    lf, tf = sg(20), inter(27, b"Bold")
    lw, tw = tracked_width(d, label.upper(), lf, 0.12), d.textlength(text, font=tf)
    w = int(max(lw, tw)) + 44
    d.rounded_rectangle((right - w, y, right, y + 84), 18, fill=WHITE)
    tracked(d, (right - 22 - lw, y + 11), label.upper(), lf, BLUE, 0.12)
    d.text((right - 22 - tw, y + 38), text, font=tf, fill=SLATE)


def bar(img, text="Buy and sell used equipment"):
    """Brand bar at the bottom of feed posts."""
    d = ImageDraw.Draw(img)
    y = img.height - BAR_H
    d.rectangle((0, y, img.width, img.height), fill=BOX)
    for i in range(4):   # blue stripes, leaning right, on the right edge
        x = img.width - 215 + i * 64
        d.polygon([(x + 55, y), (x + 85, y), (x + 30, img.height), (x, img.height)], fill=BLUE)
    f = sg(46)
    w = tracked(d, (64, y + 30), "YardSwaps", f, WHITE, -0.035)
    d.rectangle((64 + w + 26, y + 34, 64 + w + 29, y + BAR_H - 34), fill=BLUE)
    d.text((64 + w + 54, y + 40), text, font=inter(30), fill=SOFT)


def card(photo, w, h, radius=30):
    """The whole photo fitted inside w x h, rounded, as RGBA."""
    s = min(w / photo.width, h / photo.height)
    im = photo.resize((round(photo.width * s), round(photo.height * s)), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius, fill=255)
    im.putalpha(mask)
    return im


def drop_shadow(img, box, radius=30):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 22, x1, y1 + 22), radius, fill=(4, 12, 28, 150))
    return Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(30))).convert("RGB")


def _photo_top(img, photo, top_of_text, pos, under=70, fade=240):
    """Photo across the top, down to just under where the text starts, melting into the panel."""
    ph = top_of_text + under
    img.paste(cover(photo, img.width, ph, pos), (0, 0))
    melt(img, ph - fade, ph)


# ---------- posts ----------

def tip_post(photo, kicker, headline, body, tip, tip_label="PRO TIP", credit_text=None, pos=(0.5, 0.5), tall=False):
    H = TALL_H if tall else FEED_H
    pad = 56 if tall else 64
    img = Image.new("RGB", (W, H), PANEL)
    d = ImageDraw.Draw(img)
    width = W - 2 * pad
    blocks = [b_kicker(d, kicker), b_headline(d, headline, width, 150 if tall else 132),
              b_text(d, body, min(width, 940), 46 if tall else 37),
              b_tip(d, tip_label, tip, width, 32 if tall else 27, 38 if tall else 33)]
    gaps = [14, 20, 26] if not tall else [18, 26, 32]
    bottom = H - (SAFE_BOTTOM + 30 if tall else BAR_H + 40)
    _photo_top(img, photo, column_top(blocks, gaps, bottom), pos)
    if tall:
        shade_top(img)
    column(img, blocks, gaps, pad, bottom)
    tab(img, pad, SAFE_TOP if tall else 0, hanging=not tall)
    if credit_text:
        credit(img, W - (pad if tall else 40), SAFE_TOP + 6 if tall else 30, "On YardSwaps now", credit_text)
    if not tall:
        bar(img)
    return img


def text_post(kicker, headline, body, label, line):
    """Feed post with no photo (the "buyers are looking for" cards): the words carry it, same panel and bar."""
    img = Image.new("RGB", (W, FEED_H), PANEL)
    d = ImageDraw.Draw(img)
    pad, width = 64, W - 128
    blocks = [b_kicker(d, kicker), b_headline(d, headline, width, 150), b_text(d, body, min(width, 900), 44),
              b_tip(d, label, line, width, 28, 40)]
    gaps = [18, 26, 44]
    total = sum(h for h, _ in blocks) + sum(gaps)
    top, bottom = 150, FEED_H - BAR_H - 50
    column(img, blocks, gaps, pad, top + (bottom - top + total) // 2)
    tab(img, pad, 0, hanging=True)
    bar(img)
    return img


def story(photo, headline, body, label, line, credit_text=None, pos=(0.5, 0.5)):
    """Seller Story: headline, one line of body, and the link in the labelled box."""
    img = Image.new("RGB", (W, TALL_H), PANEL)
    d = ImageDraw.Draw(img)
    pad, width = 56, W - 112
    blocks = [b_headline(d, headline, width, 150), b_text(d, body, width, 46), b_tip(d, label, line, width, 32, 48)]
    gaps = [22, 32]
    bottom = TALL_H - SAFE_BOTTOM - 30
    _photo_top(img, photo, column_top(blocks, gaps, bottom), pos)
    shade_top(img)
    column(img, blocks, gaps, pad, bottom)
    tab(img, pad, SAFE_TOP, hanging=False)
    if credit_text:
        credit(img, W - pad, SAFE_TOP + 6, "On YardSwaps now", credit_text)
    return img


def listing_post(photo, title, price, facts="", label="Just listed", pos=(0.5, 0.5)):
    """Feed post for one real listing: the photo, its title, the price, the facts."""
    img = Image.new("RGB", (W, FEED_H), PANEL)
    d = ImageDraw.Draw(img)
    pad, width = 64, W - 128
    blocks = [b_kicker(d, label), b_title(d, title, width, 60), b_price(d, price, facts, width, 124, 36)]
    gaps = [14, 14]
    bottom = FEED_H - BAR_H - 36
    top = column_top(blocks, gaps, bottom)
    if photo.height / photo.width > (top + 20) / W * 1.12:
        # a tall photo: show all of it as a card instead of cropping half the machine away
        c = card(photo, W - 80, top - 34 - 40)
        x, y = (W - c.width) // 2, 40 + (top - 34 - 40 - c.height) // 2
        img = drop_shadow(img, (x, y, x + c.width, y + c.height))
        img.paste(c, (x, y), c)
        tab(img, pad, 0, hanging=True)
    else:
        _photo_top(img, photo, top, pos, under=40, fade=150)
        tab(img, pad, 0, hanging=True)
    column(img, blocks, gaps, pad, bottom)
    bar(img)
    return img


def reel_frame(photos, title, price, facts="", label="Just listed"):
    """Base frame of a listing Reel (everything but the photos) and each photo as a card with where it goes.

    Returns (base RGB image, [(card RGBA, x, y), ...]). The text never moves; listing_reels.py lets each
    photo card settle in and cross-fades to the next, so the item is whole in every frame. The header, the
    photo and the text sit together in the middle of the safe area, sized for the tallest photo."""
    img = Image.new("RGB", (W, TALL_H), PANEL)
    d = ImageDraw.Draw(img)
    pad, width = 56, W - 112
    blocks = [b_title(d, title, width, 58, 3), b_price(d, price, facts, width, 132, 40)]
    gaps = [16]
    text_h = sum(h for h, _ in blocks) + gaps[0]
    head_h, gap = 96, 34
    lo, hi = SAFE_TOP, TALL_H - SAFE_BOTTOM - 30
    box_h = hi - lo - head_h - text_h - 2 * gap
    cards = [card(p, W - 80, box_h) for p in photos]
    tallest = max(c.height for c in cards)
    y = lo + (hi - lo - (head_h + gap + tallest + gap + text_h)) // 2
    tab(img, pad, y, hanging=False)
    pill(img, W - pad, y + 12, label)
    y0 = y + head_h + gap
    column(img, blocks, gaps, pad, y0 + tallest + gap + text_h)
    return img, [(c, (W - c.width) // 2, y0 + (tallest - c.height) // 2) for c in cards]


def reel_still(photos, title, price, facts="", label="Just listed", i=0):
    """One finished frame (photo i in place), for previews and review sheets."""
    base, cards = reel_frame(photos, title, price, facts, label)
    c, x, y = cards[i]
    img = drop_shadow(base, (x, y, x + c.width, y + c.height))
    img.paste(c, (x, y), c)
    return img
