#!/usr/bin/env python3
"""Pick today's REAL listing photo for the daily seller Story.

Runs in GitHub Actions (story.yml). Writes stories/out/<date>-listing-<id>-bg.jpg, a small
stories/out/<date>-listing-<id>-bg.json ({"credit": "Title · $1,200"}) that render_story.js prints as a small "Shown:" line,
and KEY=VALUE lines for $GITHUB_OUTPUT (date, machine, slug, bg).

Alan, 2026-11-26: item pictures must be real ("looks like ai slop"). Until then this script took an AI-made
backdrop of a yard at sunset (a bank of ElevenLabs images, else a Runway render). Now the picture is a live
listing's own photo, and only one the daily listing review already approved for the Just listed card
(listings/queue.json, status approved or posted): that photo has passed the face check and the plate and
phone blur, and it sits in listings/photos/<id>.jpg. No approved photo, no Story that day; nothing is
generated.

Order: a listing never shown in this Story first (newest first), then the one shown longest ago. A listing
that is no longer live is left out. If the listings API cannot be reached the photo still goes out, but
without the "Shown:" line, because we could not confirm the listing is still for sale.

Env: BG_URL = use this https image instead (a real photo someone picked by hand); MACHINE names it in the log.
"""
import glob
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.yardswaps.com"
RAW = "https://raw.githubusercontent.com/AIE-Solutions/yardswaps-media/main/"
UA = "yardswaps-story/1.0 (https://github.com/AIE-Solutions/yardswaps-media)"
CREDIT_CHARS = 30   # the chip holds about this much of a title next to the price


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def load(path, default):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return default


def active_ids():
    """Ids of every live listing, or None when the API cannot be read."""
    got, total = [], None
    try:
        while total is None or len(got) < total:
            d = json.loads(fetch(f"{SITE}/api/listings?sort=newest&limit=100&offset={len(got)}"))
            page = d.get("listings") or []
            total = d.get("total", len(got) + len(page))
            if not page:
                break
            got += page
    except Exception as e:
        print(f"listings API not readable ({e}); no chip today")
        return None
    return {l["id"] for l in got if l.get("status", "active") == "active"}


def short_title(t, n=CREDIT_CHARS):
    t = re.sub(r"\s+", " ", (t or "").strip())
    t = re.split(r"\s[–—|/-]\s|,\s", t)[0] if len(t) > n else t
    if len(t) > n:
        t = t[:n + 1].rsplit(" ", 1)[0].rstrip(",;:-")
    return t


def pick(queue, posted, active):
    """The approved listing photo to show today, or None."""
    last = {}
    for p in posted:
        if p.get("status") == "posted" and str(p.get("machine", "")).startswith("listing-"):
            last[p["machine"][len("listing-"):]] = p.get("time") or p.get("date") or ""
    pool = [q for q in queue if q.get("status") in ("approved", "posted") and q.get("photo_file")
            and q.get("listing_id") and not q.get("kind")]
    if active is not None:
        pool = [q for q in pool if q["listing_id"] in active]
    pool.sort(key=lambda q: q.get("added") or "", reverse=True)        # newest first ...
    pool.sort(key=lambda q: last.get(q["listing_id"], ""))             # ... never shown first, then oldest shown
    return pool[0] if pool else None


def out(**kv):
    for k, v in kv.items():
        print(f"{k}={v}")
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f:
            for k, v in kv.items():
                f.write(f"{k}={v}\n")


def main():
    now = datetime.now(ZoneInfo("America/Chicago"))
    date = now.strftime("%Y-%m-%d")
    os.makedirs(os.path.join(ROOT, "stories", "out"), exist_ok=True)
    bg_url = (os.environ.get("BG_URL") or "").strip()
    if bg_url:
        if not bg_url.startswith("https://"):
            die("BG_URL must be https")
        slug = re.sub(r"[^a-z0-9]+", "-", (os.environ.get("MACHINE") or "manual").lower()).strip("-") or "manual"
        bg = f"stories/out/{date}-{slug}-bg.jpg"
        with open(os.path.join(ROOT, bg), "wb") as f:
            f.write(fetch(bg_url))
        return out(date=date, machine=slug, slug=slug, bg=bg)
    today = sorted(glob.glob(os.path.join(ROOT, "stories", "out", f"{date}-listing-*-bg.jpg")))
    if today:   # a second run today: the same photo, not another one
        bg = os.path.relpath(today[0], ROOT)
        slug = os.path.basename(bg)[len(date) + 1:-len("-bg.jpg")]
        print(f"reusing today's photo {bg}")
        return out(date=date, machine=slug, slug=slug, bg=bg)
    active = active_ids()
    q = pick(load("listings/queue.json", []), load("stories/posted.json", []), active)
    if not q:
        die("no approved real listing photo to show today; no Story (nothing is generated, Alan 2026-11-26)")
    slug = "listing-" + q["listing_id"]
    bg = f"stories/out/{date}-{slug}-bg.jpg"
    local = os.path.join(ROOT, q["photo_file"])
    data = open(local, "rb").read() if os.path.exists(local) else fetch(RAW + q["photo_file"])
    with open(os.path.join(ROOT, bg), "wb") as f:
        f.write(data)
    if active is not None:
        price = q.get("price")
        credit = short_title(q.get("title")) + (f" · ${price:,.0f}" if price and price > 0 else "")
        with open(os.path.join(ROOT, bg[:-4] + ".json"), "w", encoding="utf-8") as f:
            json.dump({"credit": credit, "listing_id": q["listing_id"], "title": q.get("title")}, f)
    print(f"Story photo: {q.get('title')} ({q['listing_id']}), {len(data)} bytes")
    out(date=date, machine=slug, slug=slug, bg=bg)


if __name__ == "__main__":
    main()
