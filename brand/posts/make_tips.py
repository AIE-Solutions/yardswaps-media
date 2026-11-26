#!/usr/bin/env python3
"""Render the designed tip posts in tips.json (feed 4:5 and Story 9:16) with the post kit.

    python3 brand/posts/make_tips.py            # every tip
    python3 brand/posts/make_tips.py tip-cold-start

Each tip sits on a real photo from a live listing. The "On YardSwaps now" chip names that listing and its
price only when the listings API says it is still live today; otherwise the post goes out without the chip.
Run it again on the day a tip is posted, so the chip is never stale.
"""
import json
import os
import sys
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

API = os.environ.get("LISTINGS_API", "https://www.yardswaps.com/api/listings")


def live_listings():
    out, offset = {}, 0
    try:
        while True:
            req = urllib.request.Request(f"{API}?limit=100&offset={offset}", headers={"User-Agent": "yardswaps-media"})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            got = d.get("listings") or []
            for l in got:
                if l.get("status", "active") == "active":
                    out[l["id"]] = l
            offset += len(got)
            if not got or offset >= (d.get("total") or 0):
                return out
    except Exception as e:  # no network: render without the chip rather than claim a listing is live
        print(f"listings API not reachable ({e}); rendering without the listing chip")
        return {}


def main():
    want = set(sys.argv[1:])
    tips = json.load(open(os.path.join(HERE, "tips.json")))["tips"]
    live = live_listings()
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for t in tips:
        if want and t["slug"] not in want:
            continue
        photo = Image.open(os.path.join(HERE, "photos", t["slug"] + ".jpg")).convert("RGB")
        l = live.get(t.get("listing_id"))
        chip = None
        if l and t.get("credit") and l.get("price"):
            chip = f"{t['credit']} · ${l['price']:,.0f}"
        for tall, name in ((False, "4x5"), (True, "9x16")):
            img = kit.tip_post(photo, t["kicker"], t["headline"], t["body"], t["tip"],
                               tip_label=t.get("tip_label", "PRO TIP"), credit_text=chip,
                               pos=tuple(t.get("pos", (0.5, 0.5))), tall=tall)
            out = os.path.join(HERE, "out", f"{t['slug']}-{name}.jpg")
            img.save(out, "JPEG", quality=90, optimize=True)
        print(f"{t['slug']}: {'chip ' + chip if chip else 'no chip (listing not live)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
