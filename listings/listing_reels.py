#!/usr/bin/env python3
"""Turn live listings into 12-second 9:16 Reels, so the posters have real, never-repeated machines.

Alan, 2026-11-21: "We keep reusing the same machines for our social media posts." The library had about
74 different machines for 9 Reels a day on each platform; with the 14-day machine rule (rotation/README.md)
that runs dry in about four days. The ~115 live listings are the deeper pool, new listings first.

Runs in the listings workflow right after prep (9:10 am Central). Each run:

1. Sync: a library clip whose listing is no longer active (sold, paused, deleted) or whose seller
   switched off "Feature my listings in YardSwaps social posts" gets "hold": true, so it never posts again.
   Reel reviews from listings/reel-queue.json are applied: approved clears the hold, rejected removes the
   clip file and its library entry.
2. Build up to REELS_PER_RUN new Reels from live listings in rotation order (rotation.rank_listings:
   not shown anywhere in 14 days, newest first, one per seller, categories interleaved), skipping
   listings that already have a clip.

Each Reel shows only the listing's own photos (up to 3) in the post kit look (brand/posts/kit.py, k2): the
WHOLE item across the top with nothing drawn over it, the price in the one blue tag, the short title and a line
of facts on white, and another photo of the same listing underneath. Shots are joined with hard cuts and every
shot changes the top photo, the detail and the facts line. Same checks as the Just listed card: no photo with a
face, every word with a digit blurred (plates, phones, street numbers), no title with contact details. Then the
2-second YardSwaps end card every video ends on (brand/endcard: wordmark, "Add a photo. AI fills in the rest.",
store badges, yardswaps.com). After the build, brand/endcard/endcard.py fix checks every clip in the library and the
Shorts queue and adds the card where one is missing (posters only post clips it has marked). No seller name, no description, no location.
Music: one of the licensed beds in music/v2, low.

Review gate (listings/README.md "Review rules"): a clip whose only photo is the one the daily review
already approved on the listing's card goes straight in. Any other clip goes in with "hold": true and a
"pending" row in listings/reel-queue.json, with a contact sheet of every frame it uses in
listings/reel-previews/<id>.jpg, until the review task approves it.

Env: DRY_RUN=1 renders into /tmp and changes nothing; REELS_PER_RUN (default 6); PER_SELLER (default 1, clips per seller per run); LISTINGS_JSON = read the
listings from this file instead of the API (tests).
"""
import datetime as dt
import json
import os
import random
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "listings"))
sys.path.insert(0, os.path.join(ROOT, "rotation"))
sys.path.insert(0, os.path.join(ROOT, "brand", "endcard"))
sys.path.insert(0, os.path.join(ROOT, "brand", "posts"))
import endcard  # noqa: E402
import kit  # noqa: E402
import just_listed as jl  # noqa: E402
import rotation as rot  # noqa: E402

LIBRARY = os.path.join(ROOT, "reels", "library.json")
CLIPS = os.path.join(ROOT, "reels", "library")
REEL_QUEUE = os.path.join(ROOT, "listings", "reel-queue.json")
PREVIEWS = os.path.join(ROOT, "listings", "reel-previews")
MUSIC = os.path.join(ROOT, "music", "v2")

REELS_PER_RUN = int(os.environ.get("REELS_PER_RUN") or 6)
PER_SELLER = int(os.environ.get("PER_SELLER") or 1)   # clips per seller per run; a backfill run raises it
W, H, FPS = 1080, 1920, 30
PHOTO_SECONDS = 3.4
END_SECONDS = 2.0
MAX_PHOTOS = 3

WHITE, BLUE, SLATE = (255, 255, 255), (37, 99, 235), (26, 51, 83)

QUESTIONS = [
    "What would you put this to work on first?",
    "What do you check first on a used one like this?",
    "What's sitting in your yard that a buyer like this is looking for?",
    "Used or new: which way do you go on a machine like this?",
    "What's the one machine your crew can't do without?",
    "What did you replace last year that's still sitting around?",
]


def slugify(t, n=34):
    s = re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")
    return s[:n].rstrip("-") or "listing"


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")


def load_library():
    with open(LIBRARY, encoding="utf-8") as f:
        return json.load(f)


# ---------- frames ----------
# The look comes from brand/posts/kit.py (Alan, 2026-11-26: "whatever we are sending to the socials looks like
# ai slop", then "The white and blue is much cleaner than the blue in blue"). No fades and no slow zoom: each
# shot is a still, and the cut to the next one is hard.


def end_card():
    """The YardSwaps end card (brand/endcard), the same one every video ends on."""
    from PIL import Image
    return Image.open(endcard.card_png("seller", W, H)).convert("RGB").resize((W, H))


def render(l, photos_rgb, question, out_mp4, sheet_jpg):
    """Encode the Reel; returns its length in seconds. `question` stays in the caption, not on the frame."""
    from PIL import Image
    photos = [Image.fromarray(p) for p in photos_rgb]
    shots = kit.reel_shots(photos, jl.spec_title(l), jl.price_text(l.get("price")), jl.facts_lines(l))
    k = len(shots)
    n = int(PHOTO_SECONDS * FPS)
    total = k * PHOTO_SECONDS + END_SECONDS
    tracks = sorted(f for f in os.listdir(MUSIC) if f.endswith(".mp3")) if os.path.isdir(MUSIC) else []
    args = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
            "-r", str(FPS), "-i", "-"]
    if tracks:
        args += ["-i", os.path.join(MUSIC, random.Random(l["id"]).choice(tracks)),
                 "-filter_complex", f"[1:a]atrim=0:{total},volume=0.35,afade=t=out:st={total - 1.2}:d=1.2[a]",
                 "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "128k"]
    args += ["-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-movflags", "+faststart", "-t", f"{total}", out_mp4]
    enc = subprocess.Popen(args, stdin=subprocess.PIPE)

    for img in shots:
        frame = img.tobytes()
        for _ in range(n):
            enc.stdin.write(frame)
    stills = list(shots)
    end = end_card()
    endb = end.tobytes()
    for _ in range(int(END_SECONDS * FPS)):
        enc.stdin.write(endb)
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {l['id']}")
    # contact sheet for the review: every photo frame + the end card
    thumbs = [t.resize((270, 480)) for t in stills + [end]]
    sheet = Image.new("RGB", (270 * len(thumbs) + 10 * (len(thumbs) - 1), 480), (255, 255, 255))
    for i, t in enumerate(thumbs):
        sheet.paste(t, (i * 280, 0))
    sheet.save(sheet_jpg, "JPEG", quality=82)
    return round(total, 1)


# ---------- photos ----------

def clean_photos(cv2, np, l, card_photo=None, skip=()):
    """(photos_rgb, urls) that pass the face check, with digit words blurred. `skip`: photo URLs a review
    rejected, never used again for this listing."""
    out, urls = [], []
    if card_photo and os.path.exists(os.path.join(ROOT, card_photo)):
        img = cv2.imread(os.path.join(ROOT, card_photo))
        return [cv2.cvtColor(img, cv2.COLOR_BGR2RGB)], ["card"]
    for u in (l.get("photoUrls") or [])[:jl.PHOTOS_TRIED + 1 + len(skip)]:
        if len(out) >= MAX_PHOTOS:
            break
        if u in skip:
            continue
        url = u if u.startswith("http") else jl.SITE + u
        try:
            raw = jl.fetch(url)
        except Exception as e:
            print(f"  {l['id']}: photo fetch failed {u}: {e}")
            continue
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if img is None or min(img.shape[:2]) < 400:
            continue
        if jl.faces_in(img):
            print(f"  {l['id']}: face in {u}, skipped")
            continue
        img2, _, _ = jl.blur_digit_text(img)
        out.append(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
        urls.append(u)
    return out, urls


# ---------- rebuilds ----------

PHOTO_NUM = re.compile(r"\bphotos? (\d)\b", re.I)


def bad_photos(r):
    """Photo URLs a rejected review row names ("photo 2 is a close-up ..."), or None when the reason is about
    the listing as a whole (a watermark on every photo, a title mismatch, no number at all)."""
    reason = r.get("reason") or ""
    photos = [u for u in (r.get("photos") or []) if u != "card"]
    nums = {int(n) for n in PHOTO_NUM.findall(reason)}
    if not nums or not photos or any(n < 1 or n > len(photos) for n in nums):
        return None
    if re.search(r"\b(photos|every photo|all photos|watermark|title|not equipment|duplicate)\b", reason, re.I):
        return None
    return {photos[n - 1] for n in nums}


def rebuild_skips(rq):
    """listing_id -> photo URLs to leave out, for listings whose clip was rejected over one or two photos.

    Alan, 2026-11-26: Reels must show real items. Most rejected listing Reels failed on a single photo (a
    close-up, a person's boots, a readable truck door) while the listing's other photos were fine, so the
    clip is made again from the rest and goes back to the review. Every rejection of the same listing adds
    its photos to the list; a listing whose latest rejection is about the whole listing never comes back."""
    skips = {}
    for r in rq:
        lid = r.get("listing_id")
        if r.get("status") != "rejected" or not lid:
            continue
        bad = bad_photos(r)
        if bad is None:
            skips[lid] = None
        elif skips.get(lid, set()) is not None:
            skips[lid] = skips.get(lid, set()) | bad
    return {k: v for k, v in skips.items() if v}


# ---------- restyle ----------

def same_photos(cv2, np, l, r, card_photo):
    """The photos a clip was approved with (its review row, else the approved card photo), checked again."""
    urls = [u for u in ((r or {}).get("photos") or []) if u != "card"]
    if not urls:
        return clean_photos(cv2, np, l, card_photo) if card_photo else ([], [])
    out = []
    for u in urls[:MAX_PHOTOS]:
        try:
            raw = jl.fetch(u if u.startswith("http") else jl.SITE + u)
        except Exception as e:
            print(f"  {l['id']}: photo fetch failed {u}: {e}")
            return [], []          # not the set the review saw: leave the clip as it is
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if img is None or jl.faces_in(img):
            return [], []
        out.append(cv2.cvtColor(jl.blur_digit_text(img)[0], cv2.COLOR_BGR2RGB))
    return out, urls


def restyle(vids, active, rq, queue, dry, limit):
    """Give older listing Reels the current look (kit.LOOK) from the SAME photos their review approved.

    Alan, 2026-11-26: the old frames (a small photo on a blurred copy of itself) "look like ai slop". The
    photos do not change, so a clip keeps its review status and its hold. The old file stays in the repo;
    the entry points at the new one. Returns how many it re-made."""
    todo = [v for v in vids if v.get("listing_id") in active and v.get("cut") == "listing"
            and v.get("look") != kit.LOOK]
    if not todo or limit <= 0:
        return 0
    import cv2
    import numpy as np
    latest = {r["listing_id"]: r for r in rq if r.get("listing_id")}
    cards = {q["listing_id"]: q.get("photo_file") for q in queue
             if q.get("status") in ("approved", "posted") and q.get("photo_file")}
    done = 0
    for v in todo:
        if done >= limit:
            break
        l = active[v["listing_id"]]
        photos, _ = same_photos(cv2, np, l, latest.get(l["id"]), cards.get(l["id"]))
        if not photos:
            print(f"  restyle skip {v['slug']}: its approved photos are not available")
            v["look"] = "kept"      # do not try again every run
            continue
        rel = f"reels/library/yardswaps-{v['slug']}-9x16-{kit.LOOK}.mp4"
        out = os.path.join(tempfile.gettempdir(), os.path.basename(rel)) if dry else os.path.join(ROOT, rel)
        sheet = os.path.join(tempfile.gettempdir() if dry else PREVIEWS, f"{l['id']}.jpg")
        v["seconds"] = render(l, photos, v.get("question", ""), out, sheet)
        v["file"], v["look"] = rel, kit.LOOK
        v.pop("endcard_checked", None)
        done += 1
        print(f"  restyled {v['slug']} ({v['seconds']}s, {len(photos)} photo(s)) -> {out}")
    return done


# ---------- main ----------

def body_for(l):
    title = jl.nice_title(l["title"])
    lead = "Just listed on YardSwaps" if jl.is_new(l) else "For sale on YardSwaps"
    return (f"{lead}: {title}. {jl.price_text(l.get('price'))}.\n\n"
            "See the photos and message the seller in the free YardSwaps app.\n\n"
            "Equipment sitting idle? List it free. Snap a photo and the AI writes the listing. No selling fee.")


def tags_for(l):
    cat = jl.CATEGORY_TAGS.get(l.get("category"), ["#Equipment", "#ForSale"])
    return " ".join([t.lower() for t in cat] + ["#usedequipment", "#yardswaps"])


def fetch_all():
    """Every live listing: the API returns at most 100 a page, so page with offset until total
    (before Nov 26 only the newest 100 of 146 were ever seen)."""
    got, total, off = [], None, 0
    while True:
        d = json.loads(jl.fetch(f"{jl.API}?sort=newest&limit=100&offset={off}"))
        page = d.get("listings", d) if isinstance(d, dict) else d
        total = d.get("total") if isinstance(d, dict) else None
        got += [l for l in page if l["id"] not in {g["id"] for g in got}]
        off += 100
        if not page or total is None or off >= total or off > 2000:
            break
    return {"listings": got, "total": total}


def main():
    dry = os.environ.get("DRY_RUN") == "1"
    if os.environ.get("LISTINGS_JSON"):
        data = json.load(open(os.environ["LISTINGS_JSON"]))
    else:
        data = fetch_all()
    got = data.get("listings", data) if isinstance(data, dict) else data
    active = {l["id"]: l for l in got if l.get("status", "active") == "active"}
    complete = isinstance(data, dict) and data.get("total") is not None and len(got) >= data["total"]
    feature = jl.feature_list()
    opted_out = set(feature.get("optedOut") or [])
    lib = load_library()
    vids = lib["videos"]
    rq = jl.load(REEL_QUEUE, [])
    queue = jl.load(jl.QUEUE, [])
    changed = False

    # 1. sync
    review = {r["listing_id"]: r for r in rq}
    for v in list(vids):
        lid = v.get("listing_id")
        if not lid:
            continue
        r = review.get(lid)
        if r and r.get("status") == "rejected":
            print(f"review rejected {v['slug']}: {r.get('reason', '')}; removing the clip")
            vids.remove(v)
            if not dry and os.path.exists(os.path.join(ROOT, v["file"])):
                os.remove(os.path.join(ROOT, v["file"]))
            changed = True
            continue
        if r and r.get("status") == "approved" and v.get("hold") and v.get("hold_reason", "").startswith("awaiting"):
            v.pop("hold", None)
            v.pop("hold_reason", None)
            changed = True
        gone = complete and lid not in active
        off = (active.get(lid) or {}).get("sellerId") in opted_out
        if (gone or off) and not v.get("hold"):
            v["hold"] = True
            v["hold_reason"] = "listing no longer active" if gone else "seller turned off social features"
            print(f"hold {v['slug']}: {v['hold_reason']}")
            changed = True

    # 2. build
    have = {v.get("listing_id") for v in vids if v.get("listing_id") and not v.get("studio")}
    skips = rebuild_skips(rq)
    latest = {r["listing_id"]: r for r in rq if r.get("listing_id")}
    rejected = {lid for lid, r in latest.items() if r.get("status") == "rejected" and lid not in skips}
    card_ok = {q["listing_id"]: q for q in queue if q.get("status") in ("approved", "posted") and q.get("photo_file")}
    hist = rot.uses(vids)
    # filter before ranking: a seller's slot must go to a listing that can still get a clip, not to
    # one that already has one (Nov 26: per_seller=1 after the clip filter left 3 of 146 buildable)
    todo = [l for l in active.values() if l["id"] not in have and l["id"] not in rejected and jl.safe_title(l)]
    order = rot.rank_listings(todo, hist, opted_out, per_seller=PER_SELLER)
    if PER_SELLER > 1:   # several per seller: take them seller by seller in turn so one dealer's lot is spread out
        by_seller = {}
        for l in order:
            by_seller.setdefault(l.get("sellerId"), []).append(l)
        order = []
        while any(by_seller.values()):
            for q in by_seller.values():
                if q:
                    order.append(q.pop(0))
    print(f"{len(active)} active listings, {len(order)} without a clip and free under the 14-day rule")
    built = 0
    if order:
        import cv2
        import numpy as np
        os.makedirs(CLIPS, exist_ok=True)
        os.makedirs(PREVIEWS, exist_ok=True)
        today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        for l in order:
            if built >= REELS_PER_RUN:
                break
            card = card_ok.get(l["id"], {}).get("photo_file")
            skip = skips.get(l["id"]) or set()
            if skip:
                card = None   # the review turned down a photo of this listing: use only the ones it did not name
            photos, urls = clean_photos(cv2, np, l, card, skip)
            if not photos:
                print(f"  skip {l['id']}: no usable photo")
                continue
            slug = f"listed-{slugify(jl.nice_title(l['title']))}-{l['id'][-5:]}"
            rel = f"reels/library/yardswaps-{slug}-9x16.mp4"
            out = os.path.join(tempfile.gettempdir(), os.path.basename(rel)) if dry else os.path.join(ROOT, rel)
            sheet = os.path.join(tempfile.gettempdir() if dry else PREVIEWS, f"{l['id']}.jpg")
            q = QUESTIONS[(len(have) + built) % len(QUESTIONS)]
            secs = render(l, photos, q, out, sheet)
            entry = {"added": today, "slug": slug, "file": rel, "priority": 0, "body": body_for(l),
                     "question": q, "ig_tags": tags_for(l), "category": l.get("category"),
                     "machine": "listing-" + l["id"], "listing_id": l["id"], "real": True,
                     "cut": "listing", "seconds": secs, "endcard": f"seller-{endcard.VERSION}",
                     "look": kit.LOOK}
            if not card:
                entry["hold"] = True
                entry["hold_reason"] = "awaiting the daily listing review (listings/reel-queue.json)"
                rq.append({"listing_id": l["id"], "slug": slug, "title": jl.nice_title(l["title"]),
                           "category": l.get("category"), "photos": urls,
                           "preview": f"listings/reel-previews/{l['id']}.jpg", "status": "pending",
                           "added": jl.iso(jl.now())})
            vids.append(entry)
            built += 1
            changed = True
            if skip:
                print(f"  rebuilt {slug} without {len(skip)} rejected photo(s)")
            print(f"  built {slug} ({secs}s, {len(photos)} photo(s), "
                  f"{'card photo, no hold' if card else 'held for review'}) -> {out}")
    print(f"built {built} listing Reel(s)")
    # 2b. older clips get the current look, a few a run
    n = restyle(vids, active, rq, queue, dry, int(os.environ.get("RESTYLE_PER_RUN") or 4))
    if n:
        print(f"restyled {n} older listing Reel(s)")
        changed = True
    if changed and not dry:
        save_json(LIBRARY, lib)
        save_json(REEL_QUEUE, rq)
    # 3. YardSwaps Studio POV clips (studio/make_pov.py, our replacement for the HeyCatch shorts)
    try:
        sys.path.insert(0, os.path.join(ROOT, "studio"))
        import make_pov
        make_pov.main()
    except Exception as e:  # never let the studio stop the listing Reels
        print(f"studio: skipped ({e})")
    # every clip ends on the YardSwaps end card (Alan, 2026-11-25), whichever pipeline added it
    endcard.fix(dry=dry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
