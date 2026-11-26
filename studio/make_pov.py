#!/usr/bin/env python3
"""YardSwaps Studio: short POV clips, our own replacement for the HeyCatch video posts.

Alan, 2026-11-25: "build us the same functionality Heychat provides so we don't have to pay for it",
"End to end". HeyCatch's Shorts and Reels are 4-10 second clips with a "POV: ..." line on screen, and
they hold viewers better than our 12-20 s cuts (YouTube Nov 9-16: HeyCatch avg 466 views per Short, ours
30; IG 3-second hold 30% vs 23%). This builds that format from our own material, three a day:

  - a live listing's photo that the daily listing review already approved (the Just listed card photo
    in listings/queue.json, or an approved row of listings/reel-queue.json), with a slow push-in, or
  - (off since 2026-11-26, Alan: the items must be real) a text-free stock equipment photo from
    studio/stock, only with STUDIO_STOCK=1, and such a clip never posts (reels/post_reels.py REAL_PICTURES), or
  - 5.5 s of a library clip marked "clean": true (most of our cuts carry their own words, so none yet),

then the POV hook from studio/hooks.json at the top (kept clear of TikTok's right and bottom UI), the
price under it for a listing, licensed music low, and the 2 s YardSwaps end card. About 7.5 s.

Each clip goes into reels/library.json with "cut": "pov" and "studio": true, so the posters we already
run put it on Instagram, Facebook, Threads, Stories and TikTok within their caps and the machine rotation,
and the YouTube Shorts poster takes it from the library too (youtube/post_shorts.py studio_rows, title =
the hook). Nothing here posts. The same machine id as its source keeps the 14-day rotation honest.

Runs at the end of listings/listing_reels.py (listings workflow prep, 9:10 am Central), so it needs no
workflow of its own. Env: DRY_RUN=1 renders into /tmp and saves nothing; STUDIO_PER_RUN (default 3);
STUDIO_BACKLOG (default 9: no new clip while this many studio clips have not posted yet).
"""
import datetime as dt
import json
import os
import random
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in ("listings", "rotation", os.path.join("brand", "endcard")):
    sys.path.insert(0, os.path.join(ROOT, p))
import just_listed as jl  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "brand", "posts"))
import kit  # noqa: E402
import rotation as rot  # noqa: E402
import endcard  # noqa: E402

LIBRARY = os.path.join(ROOT, "reels", "library.json")
POSTED = os.path.join(ROOT, "reels", "posted.json")
REEL_QUEUE = os.path.join(ROOT, "listings", "reel-queue.json")
HOOKS = os.path.join(HERE, "hooks.json")
CLIPS = os.path.join(ROOT, "reels", "library")
MUSIC = os.path.join(ROOT, "music", "v2")

PER_RUN = int(os.environ.get("STUDIO_PER_RUN") or 5)
BACKLOG = int(os.environ.get("STUDIO_BACKLOG") or 12)
W, H, FPS = 1080, 1920, 30
SHOT_SECONDS = 5.5
END_SECONDS = 2.0
WHITE, BLUE, SLATE = (255, 255, 255), (37, 99, 235), (26, 51, 83)
# TikTok draws its buttons over the right ~140 px and its caption over the bottom ~400 px.
SAFE_RIGHT, SAFE_BOTTOM = 140, 400
CATEGORY_COUNT = re.compile(r"\b\d+\s+(trade\s+|equipment\s+)?categories\b", re.I)
BANNED = ("guarantee", "will sell", "more views", "more sales", "free storefront", "dealer plan")

# Short names for a category, used when the listing title is too long for the hook.
NOUNS = {
    "fleet": "work truck", "trailers": "trailer", "generators": "generator", "pressure": "pressure washer",
    "vacuum": "vac truck", "pumps": "pump", "hydro": "jetter", "inspection": "sewer camera",
    "compressors": "compressor", "welding": "welder", "machining": "lathe", "automotive": "shop lift",
    "tools": "tool kit", "excavators": "excavator", "paving": "roller", "forklifts": "forklift",
    "aerial": "boom lift", "cranes": "crane", "concrete": "mixer", "drilling": "drill rig",
    "electrical": "panel", "environmental": "spill kit", "safety": "safety gear", "agriculture": "tractor",
    "landscaping": "mower", "restaurant": "kitchen gear", "refrigeration": "walk-in cooler",
    "cooking": "griddle", "warehouse": "pallet racking", "retail": "display case", "office": "office set",
    "laundry": "dryer", "hvac": "condenser", "parts": "parts bin",
}


def now():
    return dt.datetime.now(dt.timezone.utc)


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")


def slugify(t, n=30):
    s = re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")
    return s[:n].rstrip("-") or "clip"


# ---------- words ----------

# Words that describe a clip's machine key, not the machine ("forklift-yellow-warehouse" is a forklift).
MACHINE_EXTRA = {"yellow", "red", "orange", "black", "white", "green", "old", "small", "storm", "warehouse",
                 "row", "route", "rusty", "hot", "water", "skid", "manual", "shop", "cart", "mig", "thumb", "yard"}
TITLE_EXTRA = {"used", "commercial", "industrial", "heavy", "duty", "new", "like", "good", "great", "condition",
               "lot", "complete", "only", "in", "the", "a", "an", "of", "for"}
CONNECTORS = {"and", "&", "or"}


def thing_for(title, category):
    """The short name in the hook, taken from the listing's own title so it names the real item
    ("Caterpillar 140H V-Plow" -> "caterpillar v-plow", "Toyota electric forklift with ..." -> "electric
    forklift"). A category noun is only a fallback: "landscaping" covers a mower and a plow alike, and
    a hook that names the wrong machine reads as fake. Fleet listings are always "work truck"."""
    if category == "fleet":
        return NOUNS["fleet"]
    head = re.split(r"\s+[–—|/-]\s+|[,(|/]|\s+with\s+|\s+-\s+", title or "", maxsplit=1)[0]
    words = [w for w in re.sub(r"[^A-Za-z0-9&' -]+", " ", head).split()
             if not re.search(r"\d", w) and w.lower() not in TITLE_EXTRA and len(w.strip("'-")) > 1]
    if len(words) >= 2:
        # the longest ending of up to 3 words and 22 characters ("michelin tires and wheels" -> "tires and wheels")
        for n in (3, 2, 1):
            pick = words[-n:]
            if pick[0].lower() not in CONNECTORS and len(" ".join(pick)) <= 22:
                return " ".join(pick).lower()
    return NOUNS.get(category or "") or (words[0].lower() if words else "equipment")


def machine_thing(machine):
    """The short name of a library clip's machine key, or None when it has none we can trust."""
    words = [w for w in (machine or "").split("-") if w and w not in MACHINE_EXTRA]
    return " ".join(words[:2]) if words else None


def copy_problems(text):
    out = []
    if CATEGORY_COUNT.search(text):
        out.append("category count")
    low = text.lower()
    out += [b for b in BANNED if b in low]
    return out


def deck_weight(videos):
    """What the Studio deck (yardswaps.com/admin/studio) taught us per hook: each skip counts as two
    extra uses, each approval takes one away, so hooks the owner keeps skipping come up less and the
    ones he approves come back sooner. Auto-approved clips (nobody looked) teach nothing."""
    w = {}
    for v in videos:
        if not v.get("studio") or not v.get("hook"):
            continue
        if v.get("review") == "skipped":
            w[v["hook"]] = w.get(v["hook"], 0) + 2
        elif v.get("review") == "approved":
            w[v["hook"]] = w.get(v["hook"], 0) - 1
    return w


def pick_hook(hooks, used, seed, weight=None):
    """The hook used least often so far, adjusted by the deck's skips and approvals
    (ties: a stable shuffle), so all of them get a fair run."""
    live = [h for h in hooks["hooks"] if h not in set(hooks.get("retired") or [])]
    counts = {h: 0 for h in live}
    for u in used:
        if u in counts:
            counts[u] += 1
    weight = weight or {}
    rng = random.Random(seed)
    order = sorted(live, key=lambda h: (counts[h] + weight.get(h, 0), rng.random()))
    return order[0]


def hook_text(hook, thing):
    return hook.replace("{thing}", thing)


def captions(hook_line, src, question):
    """(body, ig_tags, tt_tags) in the seller voice of MESSAGING.md."""
    if src.get("listing"):
        l = src["listing"]
        lead = f"{jl.nice_title(l['title'])}, {jl.price_text(l.get('price'))} on YardSwaps.\n\n"
    else:
        lead = ""   # a stock photo or a library clip is not a listing, so the caption never says it is
    body = (f"{hook_line.replace(chr(10), ' ')}\n\n{lead}"
            "Equipment sitting idle? List it free. Snap a photo and the AI writes the listing. No selling fee.")
    cat = jl.CATEGORY_TAGS.get(src.get("category"), ["#Equipment", "#ForSale"])
    ig = " ".join([t.lower() for t in cat] + ["#usedequipment", "#bluecollar", "#yardswaps"])
    tt = " ".join(cat + ["#UsedEquipment", "#BlueCollar", "#POV"])
    return body, ig, tt


# ---------- sources ----------

def listing_sources(active, opted_out):
    """Listings with a photo a person already approved, still live, seller not opted out."""
    out = {}
    for q in load(jl.QUEUE, []):
        lid = q.get("listing_id")
        if q.get("status") in ("approved", "posted") and q.get("photo_file") and lid in active:
            if os.path.exists(os.path.join(ROOT, q["photo_file"])):
                out[lid] = {"photo_file": q["photo_file"]}
    for r in load(REEL_QUEUE, []):
        lid = r.get("listing_id")
        if r.get("status") == "approved" and r.get("photos") and lid in active and lid not in out:
            out[lid] = {"photo_url": r["photos"][0]}
    srcs = []
    for lid, ph in out.items():
        l = active[lid]
        if l.get("sellerId") in opted_out or not jl.safe_title(l):
            continue
        srcs.append({"kind": "listing", "machine": "listing-" + lid, "listing": l, "category": l.get("category"),
                     "listing_id": lid, **ph})
    return srcs


STOCK = os.path.join(HERE, "stock", "stock.json")
# Off since 2026-11-26 (Alan: "the items in the pictures need to improve and be real"): Studio clips use only
# real listing photos and real-item library clips. STUDIO_STOCK=1 turns the stock photos back on for a test;
# the posters still skip any clip that is not a real item (reels/post_reels.py REAL_PICTURES).
USE_STOCK = os.environ.get("STUDIO_STOCK") == "1"
STOCK_REUSE_DAYS = 21


def stock_sources():
    """Text-free stock equipment photos (studio/stock), for days with no free listing photo."""
    return [{"kind": "stock", "machine": p["machine"], "photo_file": p["file"], "category": p["category"],
             "thing": p["thing"], "slug": p["machine"]}
            for p in load(STOCK, {}).get("photos", []) if os.path.exists(os.path.join(ROOT, p["file"]))]


def clip_sources(videos):
    """Library clips marked "clean": true (no words burned in; most of our cuts carry their own hook
    box and question, which would sit under the POV line), cut to 5.5 s."""
    srcs = []
    for v in videos:
        if not v.get("clean") or v.get("hold") or v.get("studio") or v.get("audience") == "dealer":
            continue
        if v.get("cut") in ("listing", "pov") or v.get("platforms") or v.get("lang") not in (None, "en"):
            continue
        if not os.path.exists(os.path.join(ROOT, v.get("file", ""))) or not machine_thing(v.get("machine")):
            continue
        # real items only (Alan 11-26): a clip whose picture is not a real listing item is not a source
        if not (v.get("real") is True or v.get("picture") == "real"):
            continue
        srcs.append({"kind": "clip", "machine": rot.machine_of(v), "file": v["file"], "category": v.get("category"),
                     "slug": v["slug"], "seconds": v.get("seconds"), "thing": machine_thing(v.get("machine"))})
    return srcs


# ---------- frames ----------

def hook_parts(hook_line):
    """(label, lines of text): "POV:" and "Nobody:" style formats get their label in blue."""
    if hook_line.lower().startswith("pov:"):
        return "POV:", [hook_line[4:].strip()]
    if "\n" in hook_line:
        first, rest = hook_line.split("\n", 1)
        return first.strip(), [r.strip() for r in rest.split("\n") if r.strip()]
    return "", [hook_line]


def overlay_png(hook_line, price, path):
    """Transparent 1080x1920: the hook box at the top, the price pill under it, clear of TikTok's UI."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    left, right = 56, W - SAFE_RIGHT
    hf = jl.font("SpaceGrotesk.ttf", 66, b"Bold")
    pf = jl.font("SpaceGrotesk.ttf", 40, b"Bold")
    label, parts = hook_parts(hook_line)
    lines = []
    for part in parts:
        lines += jl.wrap(d, part, hf, right - left - 64, 4)
    lines = lines[:5]
    # the wordmark tab, as on every post (it sits on this layer so the slow push-in does not move it)
    wf = kit.sg(54)
    ww = int(kit.tracked_width(d, "YardSwaps", wf, -0.035)) + 68
    d.rounded_rectangle((left, 150, left + ww, 246), radius=22, fill=WHITE + (255,))
    kit.tracked(d, (left + 34, 167), "YardSwaps", wf, BLUE, -0.035)
    top = 270
    h = 34 + (82 if label else 0) + len(lines) * 80 + 30
    d.rounded_rectangle((left, top, right, top + h), radius=30, fill=WHITE + (245,))
    y = top + 26
    if label:
        d.text((left + 32, y), label, font=hf, fill=BLUE)
        y += 82
    for line in lines:
        d.text((left + 32, y), line, font=hf, fill=SLATE)
        y += 80
    if price:
        tw = d.textlength(price, font=pf)
        py = top + h + 24
        d.rounded_rectangle((left, py, left + tw + 56, py + 70), radius=35, fill=BLUE + (255,))
        d.text((left + 28, py + 12), price, font=pf, fill=WHITE)
    assert top + h + 120 < H - SAFE_BOTTOM
    img.save(path)
    return top + h + (94 if price else 0)     # where the words end; the photo starts under this


def still_frame(photo_rgb, path, top=620):
    """The whole photo as a card on the brand slate panel (post kit look, brand/posts/README.md; fit whole
    item rule). Until 2026-11-26 it sat on a blurred, darkened copy of itself, which Alan called "ai slop"."""
    from PIL import Image
    ph = Image.fromarray(photo_rgb)
    if ph.height / ph.width >= 1.6:     # already a tall 9:16 frame (the stock set): fill the screen
        s = max(W / ph.width, H / ph.height)
        ph.resize((round(ph.width * s), round(ph.height * s)), Image.LANCZOS).crop((0, 0, W, H)).save(path)
        return
    bg = Image.new("RGB", (W, H), kit.PANEL)
    top += 36
    box_w, box_h = W - 80, H - kit.SAFE_BOTTOM - top
    c = kit.card(ph, box_w, box_h)
    x, y = (W - c.width) // 2, top + (box_h - c.height) // 2
    bg = kit.drop_shadow(bg, (x, y, x + c.width, y + c.height))
    bg.paste(c, (x, y), c)
    bg.save(path)


def listing_photo(src):
    """The approved photo as RGB, faces refused and digit words blurred like every other listing clip."""
    import cv2
    import numpy as np
    if src.get("photo_file"):
        img = cv2.imread(os.path.join(ROOT, src["photo_file"]))
    else:
        u = src["photo_url"]
        raw = jl.fetch(u if u.startswith("http") else jl.SITE + u)
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img is None or jl.faces_in(img):
        return None
    img, _, _ = jl.blur_digit_text(img)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def render(src, hook_line, out_mp4, seed):
    """Encode the clip; returns its length in seconds, or None when the source can't be used."""
    tmp = tempfile.mkdtemp(prefix="pov-")
    over = os.path.join(tmp, "over.png")
    price = jl.price_text(src["listing"].get("price")) if src.get("listing") else ""
    words_end = overlay_png(hook_line, price, over)
    endp = os.path.join(tmp, "end.png")
    from PIL import Image
    Image.open(endcard.card_png("seller", W, H)).convert("RGB").resize((W, H)).save(endp)
    n = int(SHOT_SECONDS * FPS)
    args = ["ffmpeg", "-v", "error", "-y"]
    if src["kind"] in ("listing", "stock"):
        photo = listing_photo(src)
        if photo is None:
            return None
        still = os.path.join(tmp, "still.png")
        still_frame(photo, still, words_end)
        args += ["-i", still]
        shot = (f"[0:v]scale={W * 2}:{H * 2},zoompan=z='1+0.06*on/{n}':d={n}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1[s]")
    else:
        start = 0.6
        args += ["-ss", f"{start}", "-t", f"{SHOT_SECONDS}", "-i", os.path.join(ROOT, src["file"])]
        shot = (f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"trim=0:{SHOT_SECONDS},setpts=PTS-STARTPTS,setsar=1[s]")
    args += ["-loop", "1", "-t", f"{SHOT_SECONDS}", "-i", over,
             "-loop", "1", "-t", f"{END_SECONDS}", "-i", endp]
    filters = [shot,
               f"[1:v]fps={FPS},format=rgba[o]",
               "[s][o]overlay=0:0:shortest=1,setsar=1[a0]",
               f"[2:v]fps={FPS},setsar=1[e]",
               "[a0][e]concat=n=2:v=1:a=0,format=yuv420p[v]"]
    total = SHOT_SECONDS + END_SECONDS
    tracks = sorted(f for f in os.listdir(MUSIC) if f.endswith(".mp3")) if os.path.isdir(MUSIC) else []
    if tracks:
        args += ["-i", os.path.join(MUSIC, random.Random(seed).choice(tracks))]
        filters.append(f"[3:a]atrim=0:{total},volume=0.35,afade=t=out:st={total - 1.0}:d=1.0[a]")
    args += ["-filter_complex", ";".join(filters), "-map", "[v]"]
    if tracks:
        args += ["-map", "[a]", "-c:a", "aac", "-b:a", "128k"]
    args += ["-c:v", "libx264", "-preset", "medium", "-crf", "26", "-r", str(FPS),
             "-movflags", "+faststart", "-t", f"{total}", out_mp4]
    subprocess.run(args, check=True)
    return round(total, 1)


# ---------- main ----------

def unposted_studio(videos, posted):
    """Studio clips still to post: approved and waiting, or waiting in the deck for a decision."""
    done = {p.get("slug") for p in posted if p.get("status") == "posted"}
    return [v for v in videos if v.get("studio") and v["slug"] not in done
            and v.get("review") != "skipped" and (not v.get("hold") or v.get("review") == "pending")]


def rerender(videos, active, opted_out, dry=False):
    """Clips whose on-screen line was changed in the deck ("rerender_hook", set by sync_deck.py):
    make the video again with the new line, then let it post. Returns how many were made."""
    lsrc = {s["listing_id"]: s for s in listing_sources(active, opted_out)}
    ssrc = {s["slug"]: s for s in stock_sources()}
    csrc = {s["slug"]: s for s in clip_sources(videos)}
    done = 0
    for v in videos:
        line = (v.get("rerender_hook") or "").strip()
        if not v.get("studio") or not line:
            continue
        ref = v.get("source_ref")
        src = lsrc.get(ref) or ssrc.get(ref) or csrc.get(ref)
        problems = copy_problems(line)
        if not src or problems:
            print(f"  re-render {v['slug']}: {'copy rules ' + str(problems) if problems else 'source gone'}; keeping the old line")
            v.pop("rerender_hook", None)
            v["hold"] = v.get("review") == "skipped"
            continue
        out = os.path.join(tempfile.gettempdir(), os.path.basename(v["file"])) if dry else os.path.join(ROOT, v["file"])
        try:
            secs = render(src, line, out, ref)
        except Exception as e:
            print(f"  re-render {v['slug']} failed: {e}; trying again next run")
            continue
        if not secs:
            continue
        v["title"] = line.replace("\n", " ")
        v["seconds"] = secs
        v["hook_edited"] = True
        v.pop("rerender_hook", None)
        v["hold"] = v.get("review") == "skipped"
        done += 1
        print(f"  re-rendered {v['slug']}: {line}")
    return done


def plan(videos, posted, active, opted_out, hist, per_run=PER_RUN, backlog=BACKLOG):
    """The sources to build this run, listings first, both in machine-rotation order."""
    waiting = len(unposted_studio(videos, posted))
    room = max(0, min(per_run, backlog - waiting))
    if room == 0:
        return [], waiting
    have = {v.get("source_ref") for v in videos if v.get("studio")}
    # a stock photo comes back with a new hook once STOCK_REUSE_DAYS have passed since its last clip
    cut = (now() - dt.timedelta(days=STOCK_REUSE_DAYS)).strftime("%Y-%m-%d")
    recent = {v.get("source_ref") for v in videos if v.get("studio") and v.get("added", "") >= cut}
    lsrc = [s for s in listing_sources(active, opted_out) if s["listing_id"] not in have]
    csrc = [s for s in clip_sources(videos) if s["slug"] not in have]
    if USE_STOCK:
        csrc += [s for s in stock_sources() if s["slug"] not in recent]

    def last(s):
        return rot.last_shown({"machine": s["machine"]}, hist) or dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc)
    lsrc.sort(key=last)
    csrc.sort(key=last)
    order, seen = [], set()
    for s in lsrc + csrc:
        if s["machine"] in seen:
            continue
        seen.add(s["machine"])
        order.append(s)
    return order[:room * 2], waiting   # spares for sources that fail the photo checks


def main():
    dry = os.environ.get("DRY_RUN") == "1"
    lib = load(LIBRARY, {"videos": []})
    videos = lib["videos"]
    posted = load(POSTED, [])
    hooks = load(HOOKS, {"hooks": [], "questions": []})
    if os.environ.get("LISTINGS_JSON"):
        data = json.load(open(os.environ["LISTINGS_JSON"]))
    else:
        data = json.loads(jl.fetch(f"{jl.API}?sort=newest&limit=200"))
    got = data.get("listings", data) if isinstance(data, dict) else data
    active = {l["id"]: l for l in got if l.get("status", "active") == "active"}
    opted_out = set((jl.feature_list().get("optedOut") or []))
    hist = rot.uses(videos)
    remade = rerender(videos, active, opted_out, dry)
    todo, waiting = plan(videos, posted, active, opted_out, hist)
    print(f"studio: {waiting} POV clip(s) waiting to post; {len(todo)} source(s) lined up")
    used = [v.get("hook") for v in videos if v.get("studio")]
    weight = deck_weight(videos)
    today = now().strftime("%Y-%m-%d")
    built = 0
    os.makedirs(CLIPS, exist_ok=True)
    for src in todo:
        if built >= min(PER_RUN, max(0, BACKLOG - waiting)):
            break
        ref = src.get("listing_id") or src["slug"]
        thing = thing_for(src["listing"]["title"], src.get("category")) if src.get("listing") else src["thing"]
        hook = pick_hook(hooks, used, ref, weight)
        line = hook_text(hook, thing)
        q = hooks["questions"][(len(used)) % len(hooks["questions"])]
        body, ig, tt = captions(line, src, q)
        problems = copy_problems(" ".join([line, body, q]))
        if problems:
            print(f"  skip {ref}: copy rules {problems}")
            continue
        tail = slugify(ref)[-6:] if src["kind"] != "stock" else "s" + today.replace("-", "")[2:]
        slug = f"pov-{slugify(thing)}-{tail}"
        rel = f"reels/library/yardswaps-{slug}-9x16.mp4"
        out = os.path.join(tempfile.gettempdir(), os.path.basename(rel)) if dry else os.path.join(ROOT, rel)
        try:
            secs = render(src, line, out, ref)
        except Exception as e:
            print(f"  skip {ref}: render failed: {e}")
            continue
        if not secs:
            print(f"  skip {ref}: photo failed the face check")
            continue
        entry = {"added": today, "slug": slug, "file": rel, "priority": 0, "body": body, "question": q,
                 "ig_tags": ig, "tt_tags": tt, "category": src.get("category"), "machine": src["machine"],
                 "real": src["kind"] in ("listing", "clip"), "cut": "pov", "studio": True, "hook": hook, "title": line.replace("\n", " "),
                 "source_ref": ref, "seconds": secs, "endcard": f"seller-{endcard.VERSION}",
                 # waits in the Studio deck (yardswaps.com/admin/studio) until approved, skipped or
                 # auto-approved after a day; studio/sync_deck.py applies the decision
                 "review": "pending", "hold": True, "made": now().strftime("%Y-%m-%dT%H:%M:%SZ")}
        if src.get("listing_id"):
            entry["listing_id"] = src["listing_id"]
        if src["kind"] == "stock":
            entry["picture"] = "stock"
        videos.append(entry)
        used.append(hook)
        built += 1
        print(f"  built {slug} ({secs}s, {src['kind']}): {line} -> {out}")
    print(f"studio: built {built} POV clip(s), re-rendered {remade}")
    if (built or remade) and not dry:
        save(LIBRARY, lib)
    return built


if __name__ == "__main__":
    main()
