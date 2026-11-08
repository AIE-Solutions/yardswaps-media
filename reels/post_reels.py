#!/usr/bin/env python3
"""Post one YardSwaps Reel to Instagram and Facebook per run.

Runs from .github/workflows/reels.yml; posts at most once per Central-time
slot (SLOTS_CT, four a day since Nov 8). Standard library only.

Picks the next video from reels/library.json (never-posted first, newest
first; then, among videos posted at least MIN_GAP_DAYS ago, the one whose
past Reels earned the most follows, shares, comments and likes), builds
the seller-first caption, uploads the file bytes straight to Meta (no public
URL needed) and appends the result to reels/posted.json.

Env:
  META_PAGE_TOKEN  Page access token for the YardSwaps Facebook Page (secret;
                   expires, see reels/README.md Renewal). Missing = log a
                   notice and exit 0.
  FB_PAGE_ID       default 1291163214083476
  IG_USER_ID       default 17841429324062623 (@yardswaps)
  PLATFORMS        "instagram,facebook" (default) or one of them
  SLUG             force one video (manual runs)
  DRY_RUN          "1" = pick and print captions, post nothing
  CHECK_ONLY       "1" = only say whether a slot is open (due=0/1 to GITHUB_OUTPUT)
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

GRAPH = "https://graph.facebook.com/v23.0"
RUPLOAD_IG = "https://rupload.facebook.com/ig-api-upload/v23.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY = os.path.join(ROOT, "reels", "library.json")
POSTED = os.path.join(ROOT, "reels", "posted.json")
# Written by metrics/scorecard.py (daily, metrics.yml): "boost" per slug for the
# week's best Reels and "retire" for clear losers, which stop repeating.
RANK = os.path.join(ROOT, "metrics", "rank.json")

MIN_GAP_DAYS = 10          # same video never twice on a platform inside this
CLEAR_MINUTES = 90         # skip a platform if anything went up this recently (HeyCatch)

# Daily Reel slots in Central time (Nov 8: raised from 2 to 4 a day, Alan:
# "amplify our video postings"). Each entry is (slot time, latest start). A
# scheduled run posts once per slot, only between those two times, so every
# post stays 90+ minutes from HeyCatch (about :33 past 4 am, 12 pm and 8 pm
# Central, and the extra Instagram/Facebook posts it puts in those same
# slots) and from the 2:15 pm Just listed post:
#   7:00 am   until 9:30 am   (HeyCatch 4:33 am is 2.5 h before)
#   10:00 am  until 11:00 am  (HeyCatch 12:33 pm is 93+ min after)
#   4:30 pm   until 6:00 pm   (Just listed 2:15 pm is 2+ h before)
#   6:30 pm   until 7:00 pm   (HeyCatch 8:33 pm is 93+ min after)
# A run GitHub starts too late for its slot does nothing; the next slot's
# runs pick up. library.json "slots" (["07:00-09:30", ...]) overrides this.
CENTRAL = ZoneInfo("America/Chicago")
SLOTS_CT = [((7, 0), (9, 30)), ((10, 0), (11, 0)), ((16, 30), (18, 0)), ((18, 30), (19, 0))]
SLOT_EARLY_MINUTES = 5     # a run that starts up to 5 minutes early counts for the slot



def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(s):
    s = s.replace("Z", "+00:00")
    if len(s) > 5 and (s[-5] in "+-") and s[-3] != ":":
        s = s[:-2] + ":" + s[-2:]
    return dt.datetime.fromisoformat(s)


# ---------- captions ----------

FOLLOW_IG = "Follow @yardswaps for a new one every day."
FOLLOW_FB = "Follow the YardSwaps page for a new one every day."


# Broad hashtags from Meta's Page assistant (Nov 1): jobsite / trade tags reach
# past people who already search a machine. Instagram allows 5 per post, so a
# Reel keeps its 2 machine tags, always gets #UsedEquipment, and rotates 2 of the
# rest. Facebook has no cap and gets the whole set. library.json "broad_tags"
# overrides the list.
# Nov 5: TikTok Creator Search Insights showed #BlueCollar (2.02M searches),
# Construction Life and small business trending, so they join the rotation,
# ordered so each pair of 2 mixes a search term with a Meta jobsite tag.
BROAD_TAGS = ["#UsedEquipment", "#BlueCollar", "#Jobsite", "#ConstructionLife",
              "#Tradespeople", "#SmallBusiness", "#IndustrialEquipment",
              "#EquipmentMarketplace", "#VerifiedSeller"]
# TikTok (5 tags): 2 machine tags + #BlueCollar + #UsedEquipment + 1 of these,
# rotating. library.json "tt_tags" on a video replaces the lot.
TT_ROTATE = ["#ConstructionLife", "#SmallBusiness", "#BuildingThings", "#Jobsite"]
GENERIC = {"#usedequipment", "#yardswaps", "#equipmentforsale", "#sellequipment",
           "#sellyourequipment"}


def machine_tags(v, n=2):
    """The video's own tags that name a machine or trade, generic ones last."""
    tags = v["ig_tags"].split()
    specific = [t for t in tags if t.lower() not in GENERIC]
    return (specific + [t for t in tags if t.lower() in GENERIC
                        and t.lower() != "#usedequipment"])[:n]


def ig_tags(v, turn=0):
    if v.get("ig_tags_fixed"):
        return v["ig_tags"]
    rest = [t for t in BROAD_TAGS if t.lower() != "#usedequipment"]
    k = (turn * 2) % len(rest)
    rot = (rest + rest)[k:k + 2]
    return " ".join(machine_tags(v) + [BROAD_TAGS[0]] + rot)


def tt_tags(v, turn=0):
    """TikTok hashtags: search terms first (CAPTIONS.md, Nov 5)."""
    if v.get("tt_tags"):
        return v["tt_tags"]
    return " ".join(machine_tags(v) + ["#BlueCollar", "#UsedEquipment",
                                       TT_ROTATE[turn % len(TT_ROTATE)]])


def fb_tags(v):
    if v.get("fb_tags"):
        return v["fb_tags"]
    return " ".join(machine_tags(v) + ["#YardSwaps"] + BROAD_TAGS)


def ig_caption(v, turn=0):
    # Instagram captions don't click, so the short link is typed or found in bio.
    return (f"{v['body']}\n\n{FOLLOW_IG} Get the free YardSwaps app: "
            f"yardswaps.com/i (link in bio).\n\n{ig_tags(v, turn)}\n\n{v['question']}")


def fb_caption(v):
    # Facebook captions click, so the link carries a per-Reel tag (UTM-LINKS.md).
    link = ("https://www.yardswaps.com/sell-equipment?utm_source=facebook"
            f"&utm_medium=social&utm_campaign=reels_{v['slug']}")
    return (f"{v['body']}\n\n{FOLLOW_FB} Get the free app and list it free: {link}"
            f"\n\n{fb_tags(v)}\n\n{v['question']}")


# ---------- HTTP ----------

class GraphError(Exception):
    pass


def call(method, url, params=None, data=None, headers=None, timeout=300):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    body = None
    if isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode()
    elif data is not None:
        body = data
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        raise GraphError(f"{method} {url.split('?')[0]} -> {e.code}: {raw[:600]}")


def graph(method, path, token, **fields):
    if method == "GET":
        return call("GET", f"{GRAPH}/{path}", params={**fields, "access_token": token})
    return call("POST", f"{GRAPH}/{path}", data={**fields, "access_token": token})


# ---------- picking ----------

def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def pick(videos, posted, platform, force=None, scores=None):
    ok = [p for p in posted if p["platform"] == platform and p.get("status") == "posted"]
    last = {}
    for p in ok:
        t = parse_time(p["time"])
        last[p["slug"]] = max(last.get(p["slug"], t), t)
    if force:
        return next((v for v in videos if v["slug"] == force), None), force in last
    cutoff = now() - dt.timedelta(days=MIN_GAP_DAYS)
    # "hold": true keeps a video out of the queue (for example while its cut
    # is being fixed) without losing its place or history.
    usable = [v for v in videos if not v.get("hold") and os.path.exists(os.path.join(ROOT, v["file"]))]
    fresh = [v for v in usable if v["slug"] not in last]
    if fresh:
        fresh.sort(key=lambda v: (-int(v.get("added", "0").replace("-", "")), v.get("priority", 999)))
        return fresh[0], False
    rank = load(RANK, {})
    retired = rank.get("retire") or {}
    old = [v for v in usable if last[v["slug"]] <= cutoff and v["slug"] not in retired]
    if not old:
        return None, False
    # Repeats: best performer first (follows weigh most), then the one
    # posted longest ago. `boost` in library.json lets the weekly batch push
    # a cut up by hand; metrics/rank.json adds the scorecard's boost for the
    # week's measured winners (IG + FB engagement and Reel-link signups).
    scores = scores or {}
    auto = rank.get("boost") or {}
    # Once the scorecard is running (rank.json from the last 8 days), its
    # measured boosts replace the hand-set ones; an entry can keep its hand
    # boost with "boost_keep": true.
    fresh_rank = bool(rank.get("generatedAt")) and parse_time(rank["generatedAt"]) >= now() - dt.timedelta(days=8)
    hand = lambda v: v.get("boost", 0) if (not fresh_rank or v.get("boost_keep")) else 0
    old.sort(key=lambda v: (-(scores.get(v["slug"], 0) + hand(v) + auto.get(v["slug"], 0)), last[v["slug"]]))
    return old[0], True


# ---------- engagement score (for repeats) ----------

SCORE_WEIGHTS = {"follows": 10, "shares": 4, "saved": 3, "comments": 3, "likes": 1}


def ig_scores(token, posted, days=60):
    """Score each slug by what its Instagram Reels earned.

    like_count and comments_count come with instagram_basic. follows, shares
    and saved need instagram_manage_insights; if the token lacks it the first
    insights call fails and the score falls back to likes and comments.
    """
    since = now() - dt.timedelta(days=days)
    mine = [p for p in posted if p["platform"] == "instagram" and p.get("status") == "posted"
            and p.get("id") and parse_time(p["time"]) >= since]
    scores, insights_ok = {}, True
    for i in range(0, len(mine), 50):
        chunk = mine[i:i + 50]
        try:
            r = graph("GET", "", token, ids=",".join(p["id"] for p in chunk),
                      fields="like_count,comments_count")
        except GraphError as e:
            print(f"  could not read Reel likes/comments: {e}")
            r = {}
        for p in chunk:
            m = r.get(p["id"], {})
            s = SCORE_WEIGHTS["likes"] * int(m.get("like_count", 0) or 0) \
                + SCORE_WEIGHTS["comments"] * int(m.get("comments_count", 0) or 0)
            if insights_ok:
                try:
                    ins = graph("GET", f"{p['id']}/insights", token, metric="follows,shares,saved")
                    for row in ins.get("data", []):
                        val = (row.get("values") or [{}])[0].get("value", row.get("total_value", {}).get("value", 0))
                        s += SCORE_WEIGHTS.get(row.get("name"), 0) * int(val or 0)
                except GraphError as e:
                    insights_ok = False
                    print(f"  Reel insights unavailable, scoring by likes and comments only: {str(e)[:200]}")
            scores[p["slug"]] = scores.get(p["slug"], 0) + s
    return scores


def ours_recent(posted, platform):
    # One-off posts run by hand (SLUG set) are extra and don't use up a daily slot.
    since = now() - dt.timedelta(hours=20)
    return sum(1 for p in posted if p["platform"] == platform and p.get("status") == "posted"
               and not p.get("forced") and parse_time(p["time"]) >= since)


def slot_window(t):
    """(start, end) of the slot window time t falls in, or None outside them."""
    day = t.astimezone(CENTRAL)
    mk = lambda hm: day.replace(hour=hm[0], minute=hm[1], second=0, microsecond=0)
    early = dt.timedelta(minutes=SLOT_EARLY_MINUTES)
    for start, end in SLOTS_CT:
        if mk(start) - early <= t < mk(end):
            return mk(start) - early, mk(end)
    return None


def slot_done(posted, platform, t=None):
    win = slot_window(t or now())
    if win is None:
        return True
    return any(p["platform"] == platform and p.get("status") == "posted"
               and not p.get("forced") and parse_time(p["time"]) >= win[0] for p in posted)


def slots_text():
    f = lambda t: f"{t[0]}:{t[1]:02d}"
    return ", ".join(f"{f(a)}-{f(b)}" for a, b in SLOTS_CT)


def max_ours_per_20h():
    """Safety cap per platform, one per daily slot."""
    return len(SLOTS_CT)


def set_slots(lib):
    hm = lambda x: tuple(int(n) for n in x.strip().split(":"))
    if lib.get("slots"):
        SLOTS_CT[:] = [(hm(w.split("-")[0]), hm(w.split("-")[1])) for w in lib["slots"]]


LISTINGS_POSTED = os.path.join(ROOT, "listings", "posted.json")


def is_ours(posted, platform, when, slack_minutes=10):
    """True when a post time on the account is one of our own logged posts
    (Reels, or the daily "Just listed" photo post from listings/)."""
    return any(p["platform"] == platform and p.get("status") == "posted"
               and abs((parse_time(p["time"]) - when).total_seconds()) <= slack_minutes * 60
               for p in posted + load(LISTINGS_POSTED, []))


# ---------- Instagram ----------

def token_days_left(token):
    """Days until the token stops working, or None if it never expires."""
    d = graph("GET", "debug_token", token, input_token=token).get("data", {})
    if d and not d.get("is_valid", True):
        print(f"::warning::debug_token says META_PAGE_TOKEN is not valid: {d.get('error', d)}")
    ends = [t for t in (d.get("expires_at"), d.get("data_access_expires_at")) if t]
    if not ends:
        return None
    return (min(ends) - now().timestamp()) / 86400


LOCATIONS = []  # filled from library.json "locations"
_RESOLVED = {}


def wikidata_place_id(qid, name):
    """Facebook Places ID (Wikidata P1997) for a city, or None."""
    try:
        # Wikimedia refuses requests without a descriptive User-Agent.
        req = urllib.request.Request(
            f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",
            headers={"User-Agent": "yardswaps-reels/1.0 (https://github.com/AIE-Solutions/yardswaps-media; yardswaps@gmail.com)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            ent = json.loads(r.read())["entities"][qid]
    except Exception as e:  # network or format trouble: just skip the tag
        print(f"  wikidata lookup failed for {name}: {e}")
        return None
    label = ent.get("labels", {}).get("en", {}).get("value", "")
    if not name.lower().startswith(label.lower()):
        print(f"  wikidata {qid} is '{label}', not {name}; skipping")
        return None
    for c in ent.get("claims", {}).get("P1997", []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if v:
            return str(v)
    return None


def location_entry(day=None):
    """Today's place from library.json "locations": each entry has a name and
    either a Facebook place Page `id` or a Wikidata `wikidata` id to look one
    up, plus an optional `weight` (days per cycle)."""
    cycle = [loc for loc in LOCATIONS for _ in range(int(loc.get("weight", 1)))]
    if not cycle:
        return None
    return cycle[(day if day is not None else now().toordinal()) % len(cycle)]


def location_for(ig_id, caption, day=None):
    loc = location_entry(day)
    if not loc:
        return None
    key = loc["name"]
    if key not in _RESOLVED:
        _RESOLVED[key] = str(loc["id"]) if loc.get("id") else (
            wikidata_place_id(loc["wikidata"], loc["name"]) if loc.get("wikidata") else None)
        print(f"  location tag: {key} -> {_RESOLVED[key]}")
    if _RESOLVED[key]:
        return _RESOLVED[key]
    # No id for today's city: fall back to the first place with a fixed id.
    first = next((l for l in LOCATIONS if l.get("id")), None)
    return str(first["id"]) if first else None


def ig_last_post_time(token, ig_id):
    r = graph("GET", f"{ig_id}/media", token, fields="timestamp", limit="3")
    times = [parse_time(m["timestamp"]) for m in r.get("data", []) if m.get("timestamp")]
    return max(times) if times else None


def ig_publish(token, ig_id, path, caption, repeat, story=False):
    size = os.path.getsize(path)
    if story:
        # Stories take no caption; the API cannot add a link sticker.
        fields = {"media_type": "STORIES", "upload_type": "resumable"}
    else:
        fields = {"media_type": "REELS", "upload_type": "resumable",
                  "caption": caption, "share_to_feed": "true"}
    # Try the richest container first and fall back if Meta refuses a part:
    # Trial Reel (repeats only) and location tag (Reels only).
    attempts = []
    loc = None if story else location_for(ig_id, caption)
    if repeat and not story:
        trial = {"trial_params": json.dumps({"graduation_strategy": "SS_PERFORMANCE"})}
        if loc:
            attempts.append({**fields, **trial, "location_id": loc})
        attempts.append({**fields, **trial})
    if loc:
        attempts.append({**fields, "location_id": loc})
    attempts.append(fields)
    container = None
    for i, a in enumerate(attempts):
        try:
            container = graph("POST", f"{ig_id}/media", token, **a)
            break
        except GraphError as e:
            if i == len(attempts) - 1:
                raise
            print(f"  container refused ({', '.join(k for k in a if k in ('trial_params', 'location_id')) or 'plain'}), trying simpler: {str(e)[:200]}")
    cid = container["id"]
    with open(path, "rb") as f:
        blob = f.read()
    call("POST", f"{RUPLOAD_IG}/{cid}", data=blob, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
    for _ in range(60):  # up to 10 minutes
        st = graph("GET", cid, token, fields="status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise GraphError(f"Instagram processing failed: {st}")
        time.sleep(10)
    else:
        raise GraphError("Instagram still processing after 10 minutes; nothing published")
    pub = graph("POST", f"{ig_id}/media_publish", token, creation_id=cid)
    mid = pub["id"]
    try:
        link = graph("GET", mid, token, fields="permalink").get("permalink", "")
    except GraphError:
        link = ""
    return mid, link


# ---------- Facebook ----------

def fb_last_post_time(token, page_id):
    r = graph("GET", f"{page_id}/posts", token, fields="created_time", limit="3")
    times = [parse_time(p["created_time"]) for p in r.get("data", []) if p.get("created_time")]
    return max(times) if times else None


def fb_publish(token, page_id, path, caption):
    size = os.path.getsize(path)
    start = graph("POST", f"{page_id}/video_reels", token, upload_phase="start")
    vid = start["video_id"]
    url = start.get("upload_url") or f"https://rupload.facebook.com/video-upload/v23.0/{vid}"
    with open(path, "rb") as f:
        blob = f.read()
    call("POST", url, data=blob, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
    graph("POST", f"{page_id}/video_reels", token, upload_phase="finish",
          video_id=vid, video_state="PUBLISHED", description=caption)
    return vid, f"https://www.facebook.com/reel/{vid}"


def fb_story_publish(token, page_id, path):
    size = os.path.getsize(path)
    start = graph("POST", f"{page_id}/video_stories", token, upload_phase="start")
    vid = start["video_id"]
    url = start.get("upload_url") or f"https://rupload.facebook.com/video-upload/v23.0/{vid}"
    with open(path, "rb") as f:
        blob = f.read()
    call("POST", url, data=blob, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
    fin = graph("POST", f"{page_id}/video_stories", token, upload_phase="finish", video_id=vid)
    return fin.get("post_id") or vid, f"https://www.facebook.com/stories/{page_id}"


# ---------- Stories ----------
# A Story re-shares the newest Reel posted on the same platform in the last
# 24 hours that has not been a Story yet. Stories never count toward the Reel
# cap or the 90-minute HeyCatch spacing (they don't appear in the feed).

STORY_BASE = {"instagram_story": "instagram", "facebook_story": "facebook"}


def story_pick(videos, posted, story_platform):
    base = STORY_BASE[story_platform]
    since = now() - dt.timedelta(hours=24)
    done = {p["slug"] for p in posted if p["platform"] == story_platform
            and p.get("status") == "posted" and parse_time(p["time"]) >= since}
    reels = sorted((p for p in posted if p["platform"] == base and p.get("status") == "posted"
                    and parse_time(p["time"]) >= since and p["slug"] not in done),
                   key=lambda p: p["time"], reverse=True)
    for r in reels:
        v = next((v for v in videos if v["slug"] == r["slug"]), None)
        if v and not v.get("hold") and os.path.exists(os.path.join(ROOT, v["file"])):
            return v
    return None


# ---------- main ----------

def check_only(platforms, force, dry):
    """Cheap gate for the workflow: due=1 when this run has something to post.

    Needs no token and no video files (the gate job checks out only the JSON
    and this script), so the many backup crons cost seconds, not a full checkout.
    """
    set_slots(load(LIBRARY, {}))
    posted = load(POSTED, [])
    reels = [p for p in platforms if p in ("instagram", "facebook")]
    if force or dry or not reels:
        due, why = True, "manual run"
    elif slot_window(now()) is None:
        due, why = False, "outside the posting slots"
    else:
        open_ = [p for p in reels if not slot_done(posted, p)
                 and ours_recent(posted, p) < max_ours_per_20h()]
        due, why = bool(open_), ("slot open on " + ",".join(open_)) if open_ else "this slot already posted"
    win = slot_window(now())
    print(f"due={int(due)} ({why}); now {now().astimezone(CENTRAL):%a %H:%M} Central"
          + (f", window {win[0]:%H:%M}-{win[1]:%H:%M}" if win else ""))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"due={int(due)}\n")
    return 0


def main():
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    dry = os.environ.get("DRY_RUN") == "1"
    page_id = os.environ.get("FB_PAGE_ID") or "1291163214083476"
    ig_id = os.environ.get("IG_USER_ID") or "17841429324062623"
    platforms = [p.strip() for p in (os.environ.get("PLATFORMS") or "instagram,facebook,instagram_story,facebook_story").split(",") if p.strip()]
    force = (os.environ.get("SLUG") or "").strip() or None

    if os.environ.get("CHECK_ONLY") == "1":
        return check_only(platforms, force, dry)

    if not token and not dry:
        print("::notice::META_PAGE_TOKEN is not set yet, so nothing was posted. See reels/README.md.")
        return 0

    renew_warning = None
    if not dry:
        try:
            left = token_days_left(token)
            if left is not None and left < 14:
                renew_warning = (f"META_PAGE_TOKEN stops working in {left:.0f} days. "
                                 "Make a new one (reels/README.md, steps 3-6) and replace the secret.")
                print(f"::warning::{renew_warning}")
        except GraphError as e:
            # debug_token may refuse a Page token; the real calls below still
            # fail loudly if the token is dead.
            left = None
            print(f"::warning::Could not check the token's expiry: {e}")

    lib = load(LIBRARY, {"videos": []})
    set_slots(lib)
    videos = lib["videos"]
    LOCATIONS[:] = lib.get("locations", [])
    if lib.get("broad_tags"):
        BROAD_TAGS[:] = lib["broad_tags"]
    posted = load(POSTED, [])
    summary, failed = [], False
    scores = None

    if dry and LOCATIONS:
        # Show every place in the rotation; with a token, ask Meta what each id is.
        for d in range(sum(int(l.get("weight", 1)) for l in LOCATIONS)):
            pid = location_for(ig_id, "", now().toordinal() + d)
            if pid and token:
                try:
                    info = graph("GET", pid, token, fields="name,location")
                    summary.append(f"location day+{d}: {pid} = {info.get('name')} {info.get('location', {}).get('city', '')}")
                except GraphError as e:
                    # Reading another Page needs extra Meta access; the real
                    # test is whether a Reel container accepts the id.
                    summary.append(f"location day+{d}: {location_entry(now().toordinal() + d)['name']} -> {pid} (Meta lookup not allowed: {str(e)[60:140]})")
            else:
                summary.append(f"location day+{d}: {location_entry(now().toordinal() + d)['name']} -> {pid}")

    reel_platforms = [p for p in platforms if p in ("instagram", "facebook")]
    story_platforms = [p for p in platforms if p in STORY_BASE]

    for platform in reel_platforms:
        video, repeat = pick(videos, posted, platform, force)
        if repeat and not force and token:
            # Only score when a repeat is due, so fresh weeks cost no extra calls.
            if scores is None:
                scores = ig_scores(token, posted)
                if scores:
                    top = sorted(scores.items(), key=lambda kv: -kv[1])[:5]
                    print("  top Reels by engagement: " + ", ".join(f"{k} {v}" for k, v in top))
            video, repeat = pick(videos, posted, platform, force, scores)
        if not video:
            summary.append(f"{platform}: skipped, every video was posted in the last {MIN_GAP_DAYS} days")
            continue
        path = os.path.join(ROOT, video["file"])
        turn = sum(1 for p in posted if p["platform"] == platform and p.get("status") == "posted")
        caption = ig_caption(video, turn) if platform == "instagram" else fb_caption(video)
        if dry:
            summary.append(f"{platform}: would post {video['slug']} (repeat={repeat})\n{caption}\n")
            continue
        # GitHub can start a scheduled run hours late or drop it, so each slot
        # has backup crons. The first run in a slot window posts; the rest stop.
        if not force and slot_window(now()) is None:
            summary.append(f"{platform}: skipped, outside the slot windows (" + slots_text() + " Central)")
            continue
        if not force and slot_done(posted, platform):
            summary.append(f"{platform}: skipped, this slot already posted (late or backup run)")
            continue
        if not force and ours_recent(posted, platform) >= max_ours_per_20h():
            summary.append(f"{platform}: skipped, already posted {max_ours_per_20h()} in the last 20 hours")
            continue
        entry = {"time": iso(now()), "platform": platform, "slug": video["slug"], "repeat": repeat}
        if force:
            entry["forced"] = True
        try:
            last = ig_last_post_time(token, ig_id) if platform == "instagram" else fb_last_post_time(token, page_id)
            # The 90-minute gap keeps clear of HeyCatch; our own one-off posts don't count.
            if (not force and last and now() - last < dt.timedelta(minutes=CLEAR_MINUTES)
                    and not is_ours(posted, platform, last)):
                summary.append(f"{platform}: skipped, a post went up {int((now()-last).total_seconds()//60)} min ago (HeyCatch spacing)")
                continue
        except GraphError as e:
            print(f"  could not read recent {platform} posts, posting anyway: {e}")
        try:
            if platform == "instagram":
                mid, link = ig_publish(token, ig_id, path, caption, repeat)
            else:
                mid, link = fb_publish(token, page_id, path, caption)
            entry.update(status="posted", id=mid, url=link)
            summary.append(f"{platform}: posted {video['slug']} {link}")
        except GraphError as e:
            entry.update(status="failed", error=str(e)[:500])
            summary.append(f"{platform}: FAILED {video['slug']}: {e}")
            failed = True
        posted.append(entry)

    for platform in story_platforms:
        video = story_pick(videos, posted, platform)
        if dry:
            # In a dry run the Reel above is not logged, so show what it would be.
            summary.append(f"{platform}: would re-share {video['slug'] if video else 'the Reel posted above'} as a Story")
            continue
        if not video:
            summary.append(f"{platform}: skipped, no new Reel in the last 24 hours to re-share")
            continue
        path = os.path.join(ROOT, video["file"])
        entry = {"time": iso(now()), "platform": platform, "slug": video["slug"], "repeat": False}
        try:
            if platform == "instagram_story":
                mid, link = ig_publish(token, ig_id, path, "", False, story=True)
            else:
                mid, link = fb_story_publish(token, page_id, path)
            entry.update(status="posted", id=mid, url=link)
            summary.append(f"{platform}: posted {video['slug']} {link}")
        except GraphError as e:
            # A failed Story never fails the run: the Reels are what matter.
            entry.update(status="failed", error=str(e)[:500])
            summary.append(f"{platform}: FAILED {video['slug']}: {e}")
            print(f"::warning::{platform} failed: {str(e)[:300]}")
        posted.append(entry)

    if not dry:
        with open(POSTED, "w", encoding="utf-8") as f:
            json.dump(posted, f, indent=1, ensure_ascii=False)
            f.write("\n")
    text = "\n".join(summary)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### Reels run\n\n```\n" + text + "\n```\n")
    if renew_warning:
        with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a", encoding="utf-8") as f:
            f.write(f"\n**{renew_warning}**\n")
    # Fail the run (GitHub emails the repo admin) once fewer than 7 days are left.
    if renew_warning and left is not None and left < 7:
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
