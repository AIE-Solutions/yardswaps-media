#!/usr/bin/env python3
"""Backgrounds for HeyCatch, in the post kit look (white and blue).

Alan, 2026-11-26: "Heychat allows to setup own images". HeyCatch (app.heycatch.ai, Videos, Post settings,
"Background images and videos") takes our own pictures and lays its caption over them. Until now it drew on
stock pictures, old app screens and trending memes. These plates are what it gets instead: one real listing
photo each, shown whole on white, the item named on the one blue tag, the wordmark once. No headline, because
HeyCatch writes its own line on top; nothing to read in the top 200 px or the bottom 340 px.

  python3 brand/heycatch/make_plates.py SRC_DIR     # SRC_DIR holds the listing photos named in PLATES

Each entry: file name, the end of the source photo's name (listing id tail and photo index), the tag.
"""
import glob
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "posts"))
import kit  # noqa: E402

W, H = 1080, 1920
SAFE_TOP, SAFE_END = 200, 1440   # the tag and the photo sit centred between these, as one group
BOX_H = 1080                     # the tallest a photo is shown
TAG_SIZE, TAG_GAP = 44, 34       # the tag sits this far above the photo, on the photo's left edge
WM_BASE = 1530

PLATES = [
    ("forklift", "xqapl-0", "Toyota electric forklift"),
    ("espresso-machine", "q3nph-0", "La Spaziale espresso machine"),
    ("spare-engine", "dsydq-0", "Komatsu HD785-7 engine"),
    ("pallet-racking", "no15x-0", "Pallet racking, full lot"),
    ("walk-in-cooler", "q3khm-0", "Walk-in display cooler"),
    ("generator", "gyurk-1", "Westinghouse generator"),
    ("mini-excavator", "fbt0s-0", "John Deere 50G"),
    ("hvac-condenser", "uemvl-0", "Goodman condenser"),
    ("tool-cabinet", "navll-0", "Kennedy tool cabinet"),
    ("micrometer-set", "k5oda-0", "Mitutoyo micrometer set"),
    ("rapid-cook-oven", "s8tqf-0", "TurboChef oven"),
    ("convection-oven", "1z3jc-0", "Cadco convection oven"),
    ("walk-behind-mower", "behok-0", "Big Dog walk-behind mower"),
    ("leaf-vacuum", "tp04q-0", "Billy Goat leaf vacuum"),
    ("boom-mower", "hmgpw-0", "Atmax boom mower"),
    ("sweeper-scrubber", "sf6pt-0", "Tennant M20 sweeper"),
    ("blasting-trailer", "5c2iy-0", "Dustless blasting trailer"),
    ("air-scrubbers", "mrxlz-1", "HEPA air scrubbers"),
    ("dehumidifiers", "wr62p-0", "Commercial dehumidifiers"),
    ("condensing-unit", "90evj-0", "FresKool condensing unit"),
    ("ice-maker", "3uv4m-0", "Osion ice maker"),
    ("coffee-grinder", "vnu8r-0", "Bunn coffee grinder"),
    ("tires-and-wheels", "owtin-0", "Michelin tires and wheels"),
    ("hydraulic-cylinder", "c6m5i-0", "Kubota cylinder and thumb"),
    ("chop-saw", "evuy3-0", "Ryobi chop saw"),
]


def plate(photo, tag):
    img = Image.new("RGB", (W, H), kit.WHITE)
    card = kit.card(photo, W - 2 * kit.M, BOX_H, radius=28)
    tag_h = round(kit.TAG_H * TAG_SIZE / kit.SIZE_TAG)
    x = (W - card.width) // 2
    top = SAFE_TOP + (SAFE_END - SAFE_TOP - tag_h - TAG_GAP - card.height) // 2
    kit.tag(img, tag, x=x, top=top, size=TAG_SIZE, width=card.width)
    img.paste(card, (x, top + tag_h + TAG_GAP), card)
    kit.wordmark_row(img, WM_BASE)
    return img


def main(src):
    out = os.path.join(HERE, "plates")
    os.makedirs(out, exist_ok=True)
    for name, frag, tag in PLATES:
        f = glob.glob(os.path.join(src, f"*{frag}.jpg"))
        assert len(f) == 1, (frag, f)
        plate(Image.open(f[0]).convert("RGB"), tag).save(
            os.path.join(out, f"yardswaps-hc-{name}.jpg"), quality=88, optimize=True)
        print(name)


if __name__ == "__main__":
    main(sys.argv[1])
