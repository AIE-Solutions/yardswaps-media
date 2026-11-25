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

Each Reel shows only the listing's own photos (up to 3, each the whole item fitted on a blurred fill of
itself, slow push-in), with the same checks as the Just listed card: no photo with a face, every word
with a digit blurred (plates, phones, street numbers), no title with contact details. On screen: a
"Just listed on YardSwaps" box with the title, the price, an open question, and the 2-second YardSwaps
end card every video ends on (brand/endcard: wordmark, "Add a photo. AI fills in the rest.", store badges,
yardswaps.com). After the build, brand/endcard/endcard.py fix checks every clip in the library and the
Shorts queue and adds the card where one is missing (posters only post clips it has marked). No seller name, no description, no location.
Music: one of the licensed beds in music/v2, low.

Review gate (listings/README.md "Review rules"): a clip whose only photo is the one the daily review
already approved on the listing's card goes straight in. Any other clip goes in with "hold": true and a
"pending" row in listings/reel-queue.json, with a contact sheet of every frame it uses in
listings/reel-previews/<id>.jpg, until the review task approves it.

Env: DRY_RUN=1 renders into /tmp and changes nothing; REELS_PER_RUN (default 6); LISTINGS_JSON = read the
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
import endcard  # noqa: E402
import just_listed as jl  # noqa: E402
import rotation as rot  # noqa: E402

LIBRARY = os.path.join(ROOT, "reels", "library.json")
CLIPS = os.path.join(ROOT, "reels", "library")
REEL_QUEUE = os.path.join(ROOT, "listings", "reel-queue.json")
PREVIEWS = os.path.join(ROOT, "listings", "reel-previews")
MUSIC = os.path.join(ROOT, "music", "v2")

REELS_PER_RUN = int(os.environ.get("REELS_PER_RUN") or 6)
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

def fit_frame(photo_rgb):
    """1080x1920: the whole photo fitted in the middle band over a blurred, darkened fill of itself."""
    from PIL import Image, ImageFilter, ImageEnhance
    ph = Image.fromarray(photo_rgb)
    s = max(W / ph.width, H / ph.height)
    bg = ph.resize((int(ph.width * s) + 1, int(ph.height * s) + 1)).crop((0, 0, W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.55)
    box_w, box_h = W - 60, 1060
    s = min(box_w / ph.width, box_h / ph.height)
    fg = ph.resize((int(ph.width * s), int(ph.height * s)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, 400 + (box_h - fg.height) // 2))
    return bg


def boxes(img, l, question):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    pad = 60
    tf = jl.font("SpaceGrotesk.ttf", 54, b"Bold")
    lf = jl.font("SpaceGrotesk.ttf", 34, b"Bold")
    pf = jl.font("SpaceGrotesk.ttf", 46, b"Bold")
    lines = jl.wrap(d, jl.nice_title(l["title"]), tf, W - 2 * pad - 40, 2)
    top = 120
    h = 40 + 44 + len(lines) * 66 + 70 + 30
    d.rounded_rectangle((pad, top, W - pad, top + h), radius=28, fill=WHITE)
    label = "JUST LISTED ON YARDSWAPS" if jl.is_new(l) else "FOR SALE ON YARDSWAPS"
    d.text((pad + 30, top + 30), label, font=lf, fill=BLUE)
    y = top + 30 + 52
    for line in lines:
        d.text((pad + 30, y), line, font=tf, fill=SLATE)
        y += 66
    d.text((pad + 30, y + 6), jl.price_text(l.get("price")), font=pf, fill=BLUE)
    qf = jl.font("SpaceGrotesk.ttf", 44, b"Bold")
    qlines = jl.wrap(d, question, qf, W - 2 * pad - 60, 2)
    qh = 40 + len(qlines) * 56
    qtop = 1500
    d.rounded_rectangle((pad + 20, qtop, W - pad - 20, qtop + qh), radius=26, fill=BLUE)
    y = qtop + 20
    for line in qlines:
        tw = d.textlength(line, font=qf)
        d.text(((W - tw) / 2, y), line, font=qf, fill=WHITE)
        y += 56
    return img


def end_card():
    """The YardSwaps end card (brand/endcard), the same one every video ends on."""
    from PIL import Image
    return Image.open(endcard.card_png("seller", W, H)).convert("RGB").resize((W, H))


def render(l, photos_rgb, question, out_mp4, sheet_jpg):
    """Encode the Reel; returns its length in seconds."""
    tmp = tempfile.mkdtemp(prefix="lr-")
    frames = []
    for i, ph in enumerate(photos_rgb):
        p = os.path.join(tmp, f"f{i}.png")
        boxes(fit_frame(ph), l, question).save(p)
        frames.append(p)
    endp = os.path.join(tmp, "end.png")
    end_card().save(endp)
    n = int(PHOTO_SECONDS * FPS)
    args, filters = ["ffmpeg", "-v", "error", "-y"], []
    for i, p in enumerate(frames):
        # one still frame in: zoompan turns it into n frames. (Looping the still for PHOTO_SECONDS
        # made zoompan emit n frames per looped frame, so the clip ran past its cut and the end
        # card never showed, 2026-11-21 to 11-25.)
        args += ["-i", p]
        # slow push-in, about 4% over the shot (slow walkthrough pace rule)
        filters.append(f"[{i}:v]scale={W * 2}:{H * 2},zoompan=z='1+0.04*on/{n}':d={n}:"
                       f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1[v{i}]")
    k = len(frames)
    args += ["-loop", "1", "-t", f"{END_SECONDS}", "-i", endp]
    filters.append(f"[{k}:v]fps={FPS},setsar=1[v{k}]")
    filters.append("".join(f"[v{i}]" for i in range(k + 1)) + f"concat=n={k + 1}:v=1:a=0,format=yuv420p[v]")
    total = k * PHOTO_SECONDS + END_SECONDS
    tracks = sorted(f for f in os.listdir(MUSIC) if f.endswith(".mp3")) if os.path.isdir(MUSIC) else []
    if tracks:
        args += ["-i", os.path.join(MUSIC, random.Random(l["id"]).choice(tracks))]
        filters.append(f"[{k + 1}:a]atrim=0:{total},volume=0.35,afade=t=out:st={total - 1.2}:d=1.2[a]")
    args += ["-filter_complex", ";".join(filters), "-map", "[v]"]
    if tracks:
        args += ["-map", "[a]", "-c:a", "aac", "-b:a", "128k"]
    args += ["-c:v", "libx264", "-preset", "medium", "-crf", "26", "-r", str(FPS),
             "-movflags", "+faststart", "-t", f"{total}", out_mp4]
    subprocess.run(args, check=True)
    # contact sheet for the review: every photo frame + the end card
    from PIL import Image
    thumbs = [Image.open(p).resize((270, 480)) for p in frames + [endp]]
    sheet = Image.new("RGB", (270 * len(thumbs) + 10 * (len(thumbs) - 1), 480), (255, 255, 255))
    for i, t in enumerate(thumbs):
        sheet.paste(t, (i * 280, 0))
    sheet.save(sheet_jpg, "JPEG", quality=82)
    return round(total, 1)


# ---------- photos ----------

def clean_photos(cv2, np, l, card_photo=None):
    """(photos_rgb, urls) that pass the face check, with digit words blurred."""
    out, urls = [], []
    if card_photo and os.path.exists(os.path.join(ROOT, card_photo)):
        img = cv2.imread(os.path.join(ROOT, card_photo))
        return [cv2.cvtColor(img, cv2.COLOR_BGR2RGB)], ["card"]
    for u in (l.get("photoUrls") or [])[:jl.PHOTOS_TRIED + 1]:
        if len(out) >= MAX_PHOTOS:
            break
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


def main():
    dry = os.environ.get("DRY_RUN") == "1"
    if os.environ.get("LISTINGS_JSON"):
        data = json.load(open(os.environ["LISTINGS_JSON"]))
    else:
        data = json.loads(jl.fetch(f"{jl.API}?sort=newest&limit=200"))
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
    rejected = {r["listing_id"] for r in rq if r.get("status") == "rejected"}
    card_ok = {q["listing_id"]: q for q in queue if q.get("status") in ("approved", "posted") and q.get("photo_file")}
    hist = rot.uses(vids)
    order = [l for l in rot.rank_listings(list(active.values()), hist, opted_out)
             if l["id"] not in have and l["id"] not in rejected and jl.safe_title(l)]
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
            photos, urls = clean_photos(cv2, np, l, card)
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
                     "cut": "listing", "seconds": secs, "endcard": f"seller-{endcard.VERSION}"}
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
            print(f"  built {slug} ({secs}s, {len(photos)} photo(s), "
                  f"{'card photo, no hold' if card else 'held for review'}) -> {out}")
    print(f"built {built} listing Reel(s)")
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
