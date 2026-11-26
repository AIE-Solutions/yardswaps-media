#!/usr/bin/env python3
"""Seller still images in the Just listed card look (Alan, 2026-11-26, of the earlier Just listed card:
"These images are super nice"; then, next to the seven k2 seller stills: "This tractor looks different?").

    python3 brand/posts/seller_photos.py <words from listing Reel slugs>   first: fetch the real photos
    python3 brand/posts/make_seller_cards.py [slug ...]

The card is the one listings/just_listed.py drew until 2026-11-26: the real photo across the top with only
the blue label on it, then on the light panel a two-line headline in slate, one line in blue with the facts
beside it in grey, and the footer line. Here the label, headline and blue line carry the seller message
(free to list, no selling fee) instead of a price. One photo per card, the whole item in frame, no faces,
plates or phone numbers; the footer names the item shown.

Out: brand/posts/seller-cards/seller-card-<slug>.jpg (1080x1350).
"""
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONTS = os.path.join(ROOT, "listings", "fonts")
SRC = os.environ.get("SELLER_SRC", os.path.join(HERE, "seller-src"))
OUT = os.path.join(HERE, "seller-cards")
BG, SLATE, BLUE, GRAY = (246, 246, 248), (26, 51, 83), (37, 99, 235), (84, 84, 86)
W, H, PH, PAD = 1080, 1350, 1000, 56
LABEL = "LIST IT FREE ON YARDSWAPS"
BLUE_LINE, FACTS = "Free to list", "No selling fee · Local pickup"


def font(name, size, weight):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def photo(frag, i=0):
    f = glob.glob(os.path.join(SRC, f"*{frag}-{i}.jpg"))
    assert len(f) == 1, (frag, i, f)
    return Image.open(f[0]).convert("RGB")


def card(ph, line1, line2, shown, anchor=(0.5, 0.5)):
    """anchor: where the cover crop sits on the photo, (0..1 across, 0..1 down)."""
    img = Image.new("RGB", (W, H), BG)
    s = max(W / ph.width, PH / ph.height)
    ph = ph.resize((int(ph.width * s + 0.5), int(ph.height * s + 0.5)), Image.LANCZOS)
    left, top = int((ph.width - W) * anchor[0]), int((ph.height - PH) * anchor[1])
    img.paste(ph.crop((left, top, left + W, top + PH)), (0, 0))
    d = ImageDraw.Draw(img)
    lf = font("SpaceGrotesk.ttf", 30, b"Bold")
    tw = d.textlength(LABEL, font=lf)
    d.rounded_rectangle((PAD - 4, 44, PAD + tw + 40, 44 + 58), radius=29, fill=BLUE)
    d.text((PAD + 18, 44 + 12), LABEL, font=lf, fill=(255, 255, 255))
    tf = font("SpaceGrotesk.ttf", 50, b"Bold")
    y = PH + 40
    for line in (line1, line2):
        assert d.textlength(line, font=tf) <= W - 2 * PAD, line
        d.text((PAD, y), line, font=tf, fill=SLATE)
        y += 62
    y += 14
    pf = font("SpaceGrotesk.ttf", 44, b"Bold")
    d.text((PAD, y), BLUE_LINE, font=pf, fill=BLUE)
    rf = font("Inter.ttf", 32, b"Medium")
    d.text((PAD + d.textlength(BLUE_LINE, font=pf) + 24, y + 8), FACTS, font=rf, fill=GRAY)
    ff = font("Inter.ttf", 28, b"Medium")
    foot = f"Shown: {shown}. yardswaps.com"
    assert d.textlength(foot, font=ff) <= W - 2 * PAD, foot
    d.text((PAD, H - 64), foot, font=ff, fill=GRAY)
    return img


# slug, (listing fragment, photo index), headline line 1, line 2, item shown, crop anchor
L2 = "Snap a photo. AI writes the listing."
CARDS = [
    ("coffee-gear", ("q3nph", 0), "Coffee gear sitting idle?", L2, "La Spaziale S11 espresso machine", (0.5, 0.5)),
    ("yard-gear", ("behok", 0), "Upgraded your mower?", L2, "Big Dog walk-behind mower", (0.5, 0.7)),
    ("shop-tools", ("k5oda", 0), "Tools you don\u2019t use?", L2, "Mitutoyo micrometer set", (0.5, 0.5)),
    ("hvac-units", ("uemvl", 0), "HVAC left from a job?", L2, "Goodman condenser", (0.5, 0.22)),
    ("spare-engine", ("dsydq", 0), "Spare engine in the shop?", L2, "Komatsu HD785-7 engine", (0.5, 0.5)),
    ("walk-in-cooler", ("q3khm", 0), "Cooler sitting empty?", L2, "Floral walk-in display cooler", (0.5, 0.5)),
    ("kitchen-ovens", ("s8tqf", 0), "Replaced your oven?", L2, "TurboChef Eco oven", (0.5, 0.3)),
]

if __name__ == "__main__":
    names = sys.argv[1:]
    os.makedirs(OUT, exist_ok=True)
    for slug, (frag, i), l1, l2, shown, anchor in CARDS:
        if names and slug not in names:
            continue
        out = os.path.join(OUT, f"seller-card-{slug}.jpg")
        card(photo(frag, i), l1, l2, shown, anchor).save(out, "JPEG", quality=88, optimize=True)
        print(out)
