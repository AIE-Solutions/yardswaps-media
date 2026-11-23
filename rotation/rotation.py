#!/usr/bin/env python3
"""Shared machine rotation: one machine is not shown again on any channel for ROTATION_DAYS.

Alan, 2026-11-21: "We keep reusing the same machines for our social media posts."

Every poster reads the same history before it picks:
  reels/posted.json        Instagram + Facebook Reels and Stories, Threads (post_reels.py)
  reels/tiktok-posted.json TikTok (post_tiktok.py)
  youtube/posted.json      YouTube Shorts (youtube/post_shorts.py)
  listings/posted.json     Just listed + wanted cards (just_listed.py)
  stories/posted.json      the 9:30 am LIST IT FREE Story (publish_story.py)
  reels/images-posted.json one-off image posts (post_image.py)
  rotation/manual.json     everything posted by hand or by a scheduled task outside this repo:
                           YouTube Shorts and long videos, Typefully X, LinkedIn, Reddit, Motion
                           cuts posted elsewhere, HeyCatch posts we spot that show one of our machines.
Nothing new writes into a shared file from two workflows at once (each poster keeps its own log), so
there are no merge fights; this module merges them on read. `python3 rotation/rotation.py log` writes
rotation/used.json, a readable snapshot of the last 30 days, for people and agents.

The rule (rotation/README.md):
  * A machine's "run" starts with its first post. For RUN_HOURS the SAME clip or listing may still go
    to the other surfaces (IG -> FB -> Stories -> Threads -> TikTok -> YouTube), because that is one
    post shared, not a repeat.
  * After that, nothing that shows the same machine (any clip, any photo of it, any channel) until
    ROTATION_DAYS after the run started.
  * Category spread: a poster prefers a clip whose category differs from its last SPREAD posts.
  * If nothing passes, the poster may fall back to the machine shown longest ago, but never one shown
    in the last FLOOR_DAYS; past that it skips the slot rather than repeat.

Machine keys: library.json "machine" (one key per physical machine or photo set; clips that reuse the
same opener photo share a key), "listing-<id>" for anything cut from a live listing, "story-<slug>" for
the LIST IT FREE Story backdrops. A clip without a key falls back to its slug.
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROTATION_DAYS = 14
RUN_HOURS = 36
FLOOR_DAYS = 7
SPREAD = 2

LIBRARY = os.path.join(ROOT, "reels", "library.json")
MANUAL = os.path.join(ROOT, "rotation", "manual.json")
SNAPSHOT = os.path.join(ROOT, "rotation", "used.json")

# LIST IT FREE Story backdrops (stories/bank/<slug>) -> category, so a Story generator counts
# against the generators category spread.
STORY_CATEGORY = {"generator": "generators", "conveyor-oven": "cooking", "dump-trailer": "trailers",
                  "walk-in-cooler": "refrigeration", "ice-machine": "refrigeration",
                  "zero-turn-mower": "landscaping", "scissor-lift": "aerial"}


def now():
    return dt.datetime.now(dt.timezone.utc)


def parse_time(s):
    s = str(s).replace("Z", "+00:00")
    if len(s) == 10:
        s += "T12:00:00+00:00"
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return default


def library():
    lib = load(LIBRARY, {})
    return lib.get("videos", []) if isinstance(lib, dict) else []


def machine_of(v):
    """The machine key of a library entry."""
    if v.get("machine"):
        return v["machine"]
    if v.get("listing_id"):
        return "listing-" + v["listing_id"]
    return v.get("slug", "")


def uses(videos=None):
    """Every post we know of: dicts with machine, category, channel, ref (slug / listing id), time."""
    videos = videos if videos is not None else library()
    by_slug = {v["slug"]: v for v in videos}
    out = []

    def add(machine, category, channel, ref, when):
        if not machine or not when:
            return
        try:
            t = parse_time(when)
        except ValueError:
            return
        out.append({"machine": machine, "category": category or "", "channel": channel, "ref": ref, "time": t})

    for p in load(os.path.join(ROOT, "reels", "posted.json"), []):
        if p.get("status") == "posted":
            v = by_slug.get(p.get("slug"), {"slug": p.get("slug")})
            add(machine_of(v), v.get("category"), p.get("platform"), p.get("slug"), p.get("time"))
    for p in load(os.path.join(ROOT, "reels", "tiktok-posted.json"), []):
        if p.get("status") in ("posted", "scheduled", "unconfirmed"):
            v = by_slug.get(p.get("slug"), {"slug": p.get("slug")})
            add(machine_of(v), v.get("category"), "tiktok", p.get("slug"), p.get("time"))
    for p in load(os.path.join(ROOT, "youtube", "posted.json"), []):
        # YouTube Shorts poster (youtube/post_shorts.py, from 2026-11-23)
        if p.get("status") in ("posted", "scheduled", "unconfirmed"):
            v = by_slug.get(p.get("library_slug") or p.get("slug"), {"slug": p.get("slug")})
            add(p.get("machine") or machine_of(v), v.get("category"), "youtube_short", p.get("slug"), p.get("time"))
    for p in load(os.path.join(ROOT, "reels", "heycatch-tiktok.json"), []):
        v = by_slug.get(p.get("slug"), {"slug": p.get("slug")})
        add(machine_of(v), v.get("category"), "heycatch", p.get("slug"), p.get("time"))
    queue = {q["listing_id"]: q for q in load(os.path.join(ROOT, "listings", "queue.json"), [])}
    for p in load(os.path.join(ROOT, "listings", "posted.json"), []):
        if p.get("status") == "posted":
            q = queue.get(p["listing_id"], {})
            add("listing-" + p["listing_id"], q.get("category"), "just_listed_" + p.get("platform", ""),
                p["listing_id"], p.get("time"))
    for p in load(os.path.join(ROOT, "stories", "posted.json"), []):
        if p.get("status") == "posted":
            slug = (p.get("machine") or "").replace(" ", "-")
            add("story-" + slug, STORY_CATEGORY.get(slug), "list_free_story", slug, p.get("time"))
    for p in load(os.path.join(ROOT, "reels", "images-posted.json"), []):
        if p.get("ok"):
            add("image-" + p.get("slug", ""), "", "image_" + p.get("platform", ""), p.get("slug"), p.get("time"))
    for p in load(MANUAL, {}).get("posts", []):
        v = by_slug.get(p.get("slug") or "", {})
        machine = p.get("machine") or (machine_of(v) if v else "") or (
            "listing-" + p["listing_id"] if p.get("listing_id") else "")
        add(machine, p.get("category") or v.get("category"), p.get("channel", "manual"),
            p.get("slug") or p.get("listing_id") or p.get("note", ""), p.get("time"))
    out.sort(key=lambda u: u["time"])
    return out


def runs(history, t=None):
    """machine -> (run start, refs posted in that run, last time) for runs that started in the window."""
    t = t or now()
    since = t - dt.timedelta(days=ROTATION_DAYS)
    state = {}
    for u in history:
        if u["time"] > t:
            continue
        m = u["machine"]
        cur = state.get(m)
        if cur is None or u["time"] >= free_from(cur):
            cur = state[m] = {"start": u["time"], "refs": set(), "last": u["time"], "first_ref": u["ref"]}
        cur["refs"].add(u["ref"])
        cur["last"] = max(cur["last"], u["time"])
    return {m: r for m, r in state.items() if r["last"] >= since or t < free_from(r)}


def allowed(v, history, t=None, ref=None):
    """True when entry `v` may post now under the rotation rule."""
    t = t or now()
    m = machine_of(v)
    ref = ref or v.get("slug")
    r = runs(history, t).get(m)
    if not r:
        return True
    if t >= free_from(r):
        return True
    # The same clip shown in the last RUN_HOURS (and nothing else of this machine): this is that one
    # showing crossing to the next surface, not a repeat.
    return burst_ok(m, ref, history, t)


def burst_ok(m, ref, history, t):
    """True when every showing of machine `m` in the last RUN_HOURS is clip `ref` AND that burst
    began after a gap of at least FLOOR_DAYS (a fresh run or a floor fallback). Without the gap
    check an old repeat kept re-opening a 36-hour window (forklift on TikTok, 11-21)."""
    recent = [u for u in history if u["machine"] == m and timedelta_ok(t - u["time"])]
    if not recent or any(u["ref"] != ref for u in recent):
        return False
    first = min(u["time"] for u in recent)
    before = [u for u in history if u["machine"] == m and first - dt.timedelta(days=FLOOR_DAYS) <= u["time"] < first]
    return not before


def in_run(v, history, t=None):
    """True when this exact clip went out on another surface in the last RUN_HOURS."""
    t = t or now()
    return burst_ok(machine_of(v), v.get("slug"), history, t)


def timedelta_ok(d):
    return dt.timedelta(0) <= d < dt.timedelta(hours=RUN_HOURS)


def free_from(r):
    """When a machine may run again: ROTATION_DAYS after its run started, or, when it was already
    shown again after its run (an old repeat), ROTATION_DAYS after that last showing."""
    if r["last"] - r["start"] > dt.timedelta(hours=RUN_HOURS):
        return r["last"] + dt.timedelta(days=ROTATION_DAYS)
    return r["start"] + dt.timedelta(days=ROTATION_DAYS)


def last_shown(v, history, t=None):
    """When this machine was last shown anywhere (None = never in the window)."""
    r = runs(history, t).get(machine_of(v))
    return r["last"] if r else None


def fallback_ok(v, history, t=None):
    """The floor for the fallback: never a machine shown in the last FLOOR_DAYS."""
    t = t or now()
    last = last_shown(v, history, t)
    return last is None or t - last >= dt.timedelta(days=FLOOR_DAYS)


def recent_categories(history, channel, n=SPREAD):
    cats = [u["category"] for u in history if u["channel"] == channel and u["category"]]
    return set(cats[-n:])


def spread(cands, history, channel):
    """Stable reorder: candidates whose category the channel didn't just show go first."""
    recent = recent_categories(history, channel)
    return [v for v in cands if (v.get("category") or "") not in recent] + \
           [v for v in cands if (v.get("category") or "") in recent]


# ---------- live listings (new listings first) ----------

def rank_listings(listings, history, opted_out=(), per_seller=1, t=None):
    """Live listings ordered for social use: not shown in the window, newest first, one per seller,
    categories interleaved so one dealer's 30 excavators don't fill a day."""
    t = t or now()
    shown = runs(history, t)
    ok = [l for l in listings if l.get("status", "active") == "active" and l.get("photoUrls")
          and l.get("sellerId") not in opted_out and ("listing-" + l["id"]) not in shown]
    ok.sort(key=lambda l: l.get("createdAt", ""), reverse=True)
    seen_seller, by_cat = {}, {}
    for l in ok:
        s = l.get("sellerId")
        if seen_seller.get(s, 0) >= per_seller:
            continue
        seen_seller[s] = seen_seller.get(s, 0) + 1
        by_cat.setdefault(l.get("category") or "", []).append(l)
    recent = recent_categories(history, "instagram", 6)
    cats = sorted(by_cat, key=lambda c: (c in recent, -len(by_cat[c])))
    out = []
    while any(by_cat.values()):
        for c in cats:
            if by_cat[c]:
                out.append(by_cat[c].pop(0))
    return out


# ---------- CLI ----------

def fmt(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def snapshot(days=30):
    hist = uses()
    since = now() - dt.timedelta(days=days)
    rows = [{**u, "time": fmt(u["time"])} for u in hist if u["time"] >= since]
    data = {"_about": "Generated by rotation/rotation.py log. Read-only: posters merge their own logs "
                      "and rotation/manual.json on every run; add hand posts to manual.json.",
            "rotation_days": ROTATION_DAYS, "run_hours": RUN_HOURS, "floor_days": FLOOR_DAYS,
            "generated": fmt(now()), "posts": rows}
    with open(SNAPSHOT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return data


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    hist = uses()
    if cmd == "log":
        d = snapshot()
        print(f"wrote {SNAPSHOT}: {len(d['posts'])} posts in 30 days")
    elif cmd == "check":
        # check <slug or machine>: may it post now?
        key = argv[2]
        v = next((x for x in library() if key in (x["slug"], machine_of(x))), {"slug": key, "machine": key})
        r = runs(hist).get(machine_of(v))
        print(json.dumps({"machine": machine_of(v), "allowed": allowed(v, hist),
                          "run_start": fmt(r["start"]) if r else None,
                          "last_shown": fmt(r["last"]) if r else None,
                          "free_from": fmt(free_from(r)) if r else "now"}, indent=1))
    elif cmd == "free":
        # library clips whose machine may post now, newest first
        vids = [v for v in library() if not v.get("hold") and allowed(v, hist)]
        vids.sort(key=lambda v: v.get("added", ""), reverse=True)
        for v in vids:
            print(f"{v.get('added','')}  {v.get('category','-'):14} {machine_of(v):32} {v['slug']}")
        print(f"{len(vids)} clips free to post now")
    elif cmd == "listings":
        # listings [file]: live listings in posting order (reads the public API JSON from a file or stdin)
        src = open(argv[2]) if len(argv) > 2 else sys.stdin
        data = json.load(src)
        ls = data.get("listings", data) if isinstance(data, dict) else data
        for l in rank_listings(ls, hist):
            print(f"{l.get('createdAt','')[:10]}  {l.get('category',''):14} {l['id']}  {l.get('title','')[:60]}")
    else:
        rs = runs(hist)
        lib = library()
        machines = {machine_of(v) for v in lib if not v.get("hold")}
        blocked = {m for m, r in rs.items() if now() < free_from(r)}
        print(f"{len(hist)} posts on record; {len(rs)} machines shown in the last {ROTATION_DAYS} days")
        print(f"library: {len(machines)} machines, {len(machines - blocked)} free now")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
