#!/usr/bin/env python3
"""YardSwaps post kit: one designed look for every still post and Reel frame.

Alan, 2026-11-26: "we need to improve quality of post and imagery and branding ... whatever we are sending to the
socials looks like ai slop". Three outside critics rated the first pass (k1: white wordmark tab, blue highlight
bar, tip box, striped footer) "fix", and a second hard critic reviewed this one. This is k2.

The look (brand colours and fonts only, CLAUDE.md of the app repo):
- the PHOTO is the hero: a real listing photo across the top, the whole item, with nothing drawn over it
  (never an AI or stock picture, never a blurred fill, no melt, no shadow);
- a WHITE ground under it (Alan, 11-26: "The white and blue is much cleaner than the blue in blue"), which is
  also how the app looks;
- ONE blue tag per frame holding the one fact that matters (the price, the hours, the offer);
- a slate (#1A3353) Space Grotesk Bold uppercase title on one line, one line of facts in Inter, the wordmark
  once ("Yard" slate, "Swaps" blue, as in the app);
- one margin (64 px) and one type scale: hook 140, headline 104, title 86, facts 50, second line 40, small 36,
  wordmark 46, tag 118;
- on 9:16 every word sits between y 269 and y 1248, the part the apps do not cover;
- no pills, stripes, check marks, icons, emoji, gradients or "POV:". Never the blue tag on slate or navy.

Pillow only, so every workflow can use it (the listings job has no browser).

    listing_post(photo, title, price, facts, facts2)       1080x1350 feed post
    reel_shots(photos, title, price, facts_lines)          1080x1920 frames, one per shot (hard cuts)
    tip_post(photo, tag, headline, body, credit_text)      1080x1350 feed post, or 1080x1920 with tall=True
    text_post(headline, tag, body, url)                    1080x1350 feed post with no photo
    story(photo, tag, headline, body, url)                 1080x1920 Story

Copy follows MESSAGING.md.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS = os.path.join(ROOT, "listings", "fonts")

LOOK = "k2"   # bump when the look changes; listing Reels re-make older clips that carry another value
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


def tracked(d, xy, text, f, fill, tracking, anchor=None):
    """Draw text with letter spacing (in em). Returns its width. anchor="ls" puts y on the baseline."""
    x, y = xy
    for c in text:
        d.text((x, y), c, font=f, fill=fill, anchor=anchor)
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


# ---------- k2: the spec band ----------

INK, GREY, LIGHT = SLATE, (74, 85, 104), (238, 242, 248)   # type, facts, and a panel with no photo
M = 64                    # the one margin
PHOTO_H = 720             # the photo fills 0..720 (a 3:2 photo is shown whole)
TAG_TOP, TAG_H = 748, 162  # the blue tag sits on the white, clear of the photo
TITLE_BASE = 1011         # baseline of the title's first line
TEXT_TOP, TEXT_BOTTOM = 269, 1248   # 9:16: the area the apps do not cover
SIZE_HOOK, SIZE_HEAD, SIZE_TITLE, SIZE_FACTS, SIZE_SECOND, SIZE_SMALL, SIZE_WM, SIZE_TAG = 140, 104, 86, 50, 40, 36, 46, 118

STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
          "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
          "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
          "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
          "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
          "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
          "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
          "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
          "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
          "WI": "Wisconsin", "WY": "Wyoming", "DC": "D.C."}


def spell_state(place):
    """"Finger, TN" -> "Finger, Tennessee": a two-letter state next to a short town reads as a typo."""
    if place and "," in place:
        town, st = place.rsplit(",", 1)
        return f"{town.strip()}, {STATES.get(st.strip().upper(), st.strip())}"
    return STATES.get((place or "").strip().upper(), place or "")


def fit_photo(photo, w, h, tol=0.06, pos=(0.5, 0.5)):
    """The photo for a w x h slot. Filled edge to edge when that trims no more than `tol` off a side (a 4:3
    phone photo loses a sliver of sky and ground); otherwise the WHOLE photo, standing on the bottom edge on the
    light panel, so no part of the item is ever cut away."""
    s = max(w / photo.width, h / photo.height)
    trim = max(photo.width * s - w, photo.height * s - h) / 2 / max(photo.width * s, photo.height * s)
    if trim <= tol:
        return cover(photo, w, h, pos)
    out = Image.new("RGB", (w, h), LIGHT)
    s = min(w / photo.width, h / photo.height)
    im = photo.resize((max(1, round(photo.width * s)), max(1, round(photo.height * s))), Image.LANCZOS)
    out.paste(im, ((w - im.width) // 2, h - im.height))
    return out


def _fit_size(d, text, make, size, width, floor, tracking=0.0):
    while size > floor and tracked_width(d, text, make(size), tracking) > width:
        size -= 2
    return size


def tag(img, text, x=M, top=TAG_TOP, size=SIZE_TAG, width=None):
    """The one blue tag: the key fact in Space Grotesk Bold. Returns its right edge."""
    d = ImageDraw.Draw(img)
    text = text.upper()
    width = width or img.width - 2 * M
    size = _fit_size(d, text, sg, size, width - 60, 60, -0.02)
    f = sg(size)
    h = round(TAG_H * size / SIZE_TAG)
    tw = tracked_width(d, text, f, -0.02)
    d.rounded_rectangle((x, top, x + tw + 60, top + h), 10, fill=BLUE)
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    base = top + (h + cap) // 2 - round(size * 0.012)
    tracked(d, (x + 30, base), text, f, WHITE, -0.02, anchor="ls")
    return x + tw + 60


TITLE_TRACK = 0.0   # capitals are set open; a negative value made letters touch (critic, 11-26)
_DANGLING = {"WITH", "AND", "ON", "OF", "FOR", "THE", "A", "AN", "IN", "AT", "TO", "PLUS", "&", "+", "OR", "BY"}


def _two_lines(d, text, width, at):
    """`text` on at most two balanced lines at size `at`, and whether words had to be dropped to do it."""
    f, lines, cur, dropped = sg(at), [], "", False
    for w in text.split():
        trial = (cur + " " + w).strip()
        if tracked_width(d, trial, f, TITLE_TRACK) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) > 2:
        dropped = True
        # never an ellipsis: keep whole words, and do not end on "with", "and", "of"...
        words = " ".join(lines[:2]).split()
        while len(words) > 2 and words[-1].strip(",;:").upper() in _DANGLING:
            words.pop()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if tracked_width(d, trial, f, TITLE_TRACK) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        lines = [ln.rstrip(",;:-") for ln in lines[:2]]
    if len(lines) == 2:
        # balance the two lines, so the second is never a lone word
        words, best = " ".join(lines).split(), None
        for k in range(1, len(words)):
            a, b = " ".join(words[:k]), " ".join(words[k:])
            wa, wb = tracked_width(d, a, f, TITLE_TRACK), tracked_width(d, b, f, TITLE_TRACK)
            if wa <= width and wb <= width and (best is None or max(wa, wb) < best[0]):
                best = (max(wa, wb), [a, b])
        if best:
            lines = best[1]
    return lines, dropped




def title_lines(d, text, width, size=SIZE_TITLE, floor=64):
    """An uppercase title in fixed sizes, never a size in between: one line at the title size, else one line at
    `floor`, else two lines at `floor`. Only a title too long for that is set two lines at 56 px, before any
    word is dropped; never an ellipsis."""
    text = " ".join(text.upper().split())
    for s in (size, floor):
        if tracked_width(d, text, sg(s), TITLE_TRACK) <= width:
            return s, [text]
    lines, dropped = _two_lines(d, text, width, floor)
    if not dropped:
        return floor, lines
    return 56, _two_lines(d, text, width, 56)[0]


def wordmark_row(img, base, right_text="yardswaps.com"):
    """The wordmark once, bottom left, and one small line on the right (the link or the listing shown)."""
    d = ImageDraw.Draw(img)
    w = tracked(d, (M, base), "Yard", sg(SIZE_WM), INK, -0.02, anchor="ls") + SIZE_WM * -0.02
    w += tracked(d, (M + w, base), "Swaps", sg(SIZE_WM), BLUE, -0.02, anchor="ls")
    if right_text:
        size = _fit_size(d, right_text, lambda z: inter(z, b"Medium"), SIZE_SMALL, img.width - 2 * M - w - 40, 26)
        d.text((img.width - M, base), right_text, font=inter(size, b"Medium"), fill=GREY, anchor="rs")


def band(img, tag_text, title, facts="", second="", body="", wm_base=1205, right_text="yardswaps.com",
         top=TAG_TOP, title_base=TITLE_BASE):
    """Tag, title, facts (and a quieter second line, or a wrapped body line) on the white ground. Positions are fixed,
    so every post lines up with every other. Returns the baseline of the last line of text."""
    d = ImageDraw.Draw(img)
    width = img.width - 2 * M
    tag(img, tag_text, top=top)
    size, lines = title_lines(d, title, width)
    two = len(lines) > 1
    first = title_base - 19 if two else title_base
    y = first
    for i, ln in enumerate(lines):
        y = first + i * round(size * 1.0)
        tracked(d, (M, y), ln, sg(size), INK, TITLE_TRACK, anchor="ls")
    if two and wm_base < 1250:
        second = ""          # the tall frame has room for one facts line under a two-line title
    if facts:
        y += 70 if two else 78
        fs = _fit_size(d, facts, inter, SIZE_FACTS, width, 38)
        d.text((M, y), facts, font=inter(fs), fill=GREY, anchor="ls")
    if second:
        y += 62
        ss = _fit_size(d, second, lambda z: inter(z, b"Medium"), SIZE_SECOND, width, 30)
        d.text((M, y), second, font=inter(ss, b"Medium"), fill=GREY, anchor="ls")
    if body:
        f = inter(SIZE_SECOND, b"Medium")
        for j, ln in enumerate(wrap(d, body, f, min(width, 900), 2)):
            y += 66 if j == 0 else 50
            d.text((M, y), ln, font=f, fill=GREY, anchor="ls")
    wordmark_row(img, wm_base, right_text)
    return y


# ---------- posts ----------

def listing_post(photo, title, price, facts="", label=None, pos=(0.5, 0.5), facts2=""):
    """Feed post for one real listing: the photo, the price in the tag, the title, the facts. (`label` is from
    k1 and no longer drawn: the caption says "Just listed".)"""
    img = Image.new("RGB", (W, FEED_H), WHITE)
    img.paste(fit_photo(photo, W, PHOTO_H, pos=pos), (0, 0))
    band(img, price, title, facts, facts2, wm_base=1283)
    return img


def _dhash(img):
    """A 64-bit difference hash: two photos of the same view land within a few bits of each other."""
    g = img.convert("L").resize((9, 8), Image.LANCZOS)
    px = list(g.getdata())
    return [px[r * 9 + c] > px[r * 9 + c + 1] for r in range(8) for c in range(8)]


def distinct(photos, near=12):
    """The photos with near-duplicates dropped (same view twice reads as a mistake once they sit in one frame).
    Order is kept; the first photo always stays."""
    kept, hashes = [], []
    for p in photos:
        h = _dhash(p)
        if all(sum(a != b for a, b in zip(h, k)) > near for k in hashes):
            kept.append(p)
            hashes.append(h)
    return kept or photos[:1]


MAST_BASE = 269 + 46              # the upright layout: the wordmark as a masthead at the top of the safe area
UP_TAG = MAST_BASE + 30           # then the same tag, title and facts, 403 px higher than in the stacked layout
UP_OFF = UP_TAG - TAG_TOP
UP_GAP = 40                       # from the last line of text down to the photo


def _upright(p):
    """Upright or square: too tall for the 3:2 slot of the stacked layout."""
    return p.width < p.height * 1.2


def _tall_slot(img, p, top):
    """The upright layout's photo: flush with the text's left edge, from under the text to the foot of the
    frame. An upright phone photo fills the column (a sliver trimmed at most); anything else is shown whole,
    as wide as fits, on the white. Never a pale bar beside a photo."""
    w, h = W - 2 * M, TALL_H - top
    s = w / p.width
    if p.height * s <= h:
        img.paste(p.resize((w, max(1, round(p.height * s))), Image.LANCZOS), (M, top))
        return
    trim = (p.height * s - h) / 2 / (p.height * s)
    if trim <= 0.06:
        img.paste(cover(p, w, h), (M, top))
        return
    s = h / p.height
    img.paste(p.resize((max(1, round(p.width * s)), h), Image.LANCZOS), (M, top))


def reel_layout(photos):
    """("stack" | "upright", the photos it uses). Stack: two or more wide photos, the listing's first photo
    wide. Upright: the first photo is upright (most phone photos), or there is one wide photo and upright ones."""
    photos = distinct(photos)
    wide = [p for p in photos if not _upright(p)]
    if photos and not _upright(photos[0]) and (len(wide) > 1 or len(wide) == len(photos)):
        return "stack", wide
    return "upright", photos


def reel_shots(photos, title, price, facts_lines):
    """The frames of a listing Reel, one per shot, joined with hard cuts by listings/listing_reels.py.

    Stack (wide photos): the whole item on top (photo i), the white band (the price in the tag and the title on
    every shot, a facts line that changes with the shot), and another wide photo of the same listing below as a
    detail (it sits under the apps' buttons, so nothing there has to be read). One wide photo: the foot stays
    white. Upright (the first photo is upright or square): the wordmark as a masthead at the top of the safe
    area, the same tag, title and facts under it, and one photo a shot standing large under the text, flush
    with its left edge. The link is on the end card, not on the frame. Photos that show the same view are
    shown once."""
    kind, photos = reel_layout(photos)
    k = len(photos)
    lines = [ln for ln in facts_lines if ln] or [""]
    out, top = [], None
    for i, p in enumerate(photos):
        img = Image.new("RGB", (W, TALL_H), WHITE)
        if kind == "stack":
            img.paste(fit_photo(p, W, PHOTO_H), (0, 0))
            if k > 1:
                img.paste(cover(photos[(i + 1) % k], W, TALL_H - 1240), (0, 1240))
            band(img, price, title, lines[i % len(lines)], right_text="")
        else:
            y = band(img, price, title, lines[i % len(lines)], wm_base=MAST_BASE, top=UP_TAG,
                     title_base=TITLE_BASE + UP_OFF, right_text="")
            top = top or y + UP_GAP      # the same for every shot of the clip
            _tall_slot(img, p, top)
        out.append(img)
    return out


def reel_still(photos, title, price, facts_lines, i=0):
    """One finished frame (shot i), for previews and review sheets."""
    return reel_shots(photos, title, price, facts_lines)[i]


def tip_post(photo, tag_text, headline, body, credit_text=None, pos=(0.5, 0.5), tall=False):
    """A tip: the photo PROVES the tip (the meter, the plate, the wear), the tag holds the fact in the photo,
    the headline is one plain instruction and the body one line that says the same thing."""
    img = Image.new("RGB", (W, TALL_H if tall else FEED_H), WHITE)
    img.paste(cover(photo, W, PHOTO_H, pos), (0, 0))
    if tall:
        ImageDraw.Draw(img).rectangle((0, 1240, W, TALL_H), fill=LIGHT)
    band(img, tag_text, headline, body=body, wm_base=1205 if tall else 1283, right_text=credit_text or "yardswaps.com")
    return img


def text_post(headline, tag_text, body, url="yardswaps.com"):
    """Feed post with no photo (the "buyers are looking for" cards): the headline, the key words in the blue
    tag under it, one line, the wordmark. The block sits in the middle of the frame."""
    img = Image.new("RGB", (W, FEED_H), WHITE)
    d = ImageDraw.Draw(img)
    width = W - 2 * M
    lines = [ln.lstrip("*").upper() for ln in headline]
    size = SIZE_HEAD
    while size > 72 and max(tracked_width(d, ln, sg(size), -0.025) for ln in lines) > width:
        size -= 2
    f = sg(size)
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    bf = inter(44, b"Medium")
    body_lines = wrap(d, body, bf, min(width, 900), 3)
    total = cap + (len(lines) - 1) * round(size * 0.98) + 44 + TAG_H + 78 + (len(body_lines) - 1) * 58
    y = (FEED_H - 120 - total) // 2 + cap
    for ln in lines:
        tracked(d, (M, y), ln, f, INK, -0.025, anchor="ls")
        y += round(size * 0.98)
    y += 44 - round(size * 0.98)
    tag(img, tag_text, top=y)
    y += TAG_H + 78
    for ln in body_lines:
        d.text((M, y), ln, font=bf, fill=GREY, anchor="ls")
        y += 58
    wordmark_row(img, 1283, url)
    return img


STORY_OFF = 200   # a Story sits 200 px lower: Instagram's own header covers the light strip, not the photo


def story(photo, tag_text, headline, body, url="yardswaps.com", pos=(0.5, 0.5), credit_text=None):
    """Seller Story: a light strip, the real photo, then the tag, a one-line headline, the body and the link on
    white, and the light panel. stories/render_story.js draws the same thing in HTML for the daily job."""
    o = STORY_OFF
    img = Image.new("RGB", (W, TALL_H), LIGHT)
    img.paste(fit_photo(photo, W, PHOTO_H, pos=pos), (0, o))
    d = ImageDraw.Draw(img)
    d.rectangle((0, o + PHOTO_H, W, o + 1240), fill=WHITE)
    band(img, tag_text, headline, body=body, wm_base=1205 + o, right_text=url, top=TAG_TOP + o, title_base=TITLE_BASE + o)
    if credit_text:
        d.text((M, o + 1306), "Shown: " + credit_text, font=inter(32, b"Medium"), fill=GREY, anchor="ls")
    return img
