#!/usr/bin/env python3
"""Post YardSwaps YouTube Shorts from youtube/queue.json, through Buffer.

Runs from .github/workflows/youtube-shorts.yml. Standard library only.

Why Buffer and not the YouTube Data API: Google locks every video that an
unaudited API project uploads with videos.insert to private viewing, and the
owner can't make it public afterwards (YouTube Data API docs, videos.insert:
"All videos uploaded via the videos.insert endpoint from unverified API
projects created after 28 July 2020 will be restricted to private viewing
mode"). The audit takes days to months. Buffer is an approved YouTube app,
the YardSwaps channel is already connected there, and the BUFFER_API_KEY
secret the TikTok poster uses works for it too. We hand Buffer at most 2
Shorts in 24 hours (our cadence); HeyCatch's own Buffer posts don't count.

What a run does:
  1. Finds the YouTube channel in Buffer and updates youtube/posted.json with
     what Buffer has published (link) or failed (reason) since last time.
  2. If a slot is open (SLOTS_CT, Central time, each posts once a day) and we
     are under the daily cap, takes the first row of queue.json that
       - hasn't gone to YouTube (posted.json, or the same title on the channel),
       - isn't marked "skip" and is past its "not_before",
       - passes the copy checks (title <= 100 characters, no < or >, the
         description ends with a question, no category count, no banned tags),
       - is allowed by the machine rotation (rotation/rotation.py: a machine
         shown on any channel is blocked 14 days after its 36-hour run; if no
         row is allowed, the first row whose machine wasn't shown in the last
         7 days may go, the same fallback the Reels poster uses),
     and hands it to Buffer to publish 5 minutes later, public, as a Short
     (vertical and under 3 minutes, so YouTube files it under Shorts).
  3. Writes the result to posted.json, which rotation.py also reads.

Env:
  BUFFER_API_KEY  Buffer personal API key (secret). Missing = notice, exit 0.
  SLUG            post this queue row now (manual runs; ignores the slot, not the cap)
  DRY_RUN         "1" = print what would post and the next picks, post nothing
  CHECK           "1" = list the Buffer channels, the YouTube channel's recent
                  Buffer posts and the channel's latest videos, post nothing
  CHECK_ONLY      "1" = only say whether a slot is open (gate job), no API calls
  GITHUB_SHA, GITHUB_REPOSITORY, GITHUB_OUTPUT, GITHUB_STEP_SUMMARY  (Actions)
"""
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "rotation"))
try:
    import rotation as rot  # noqa: E402
except ImportError:
    rot = None

API = "https://api.buffer.com"
QUEUE = os.path.join(HERE, "queue.json")
LOG = os.path.join(HERE, "posted.json")
CENTRAL = ZoneInfo("America/Chicago")
CHANNEL_ID = "UCC_TtVN5pOfs4z9OruWUlhw"   # YardSwaps on YouTube (METRICOOL.md)
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

# Two Shorts a day (SHORTS-CADENCE.md): 10:00 am and 4:00 pm Central. Each
# slot posts once, only between its time and its latest start, so a run GitHub
# starts hours late never posts next to HeyCatch's YouTube Short (about :33
# past 4 am, 12 pm and 8 pm Central): 10:00 am is 93+ min before 12:33 pm,
# and 6:30 pm is two hours before 8:33 pm.
SLOTS_CT = [((10, 0), (11, 0)), ((16, 0), (18, 30))]
SLOT_EARLY_MINUTES = 5
MAX_PER_24H = 2            # our cadence: 2 Shorts a day (HeyCatch posts to the channel separately)
SCHEDULE_AHEAD_MIN = 5     # Buffer publishes this many minutes after the run
JSDELIVR_MAX_BYTES = 19_000_000
BANNED_TAGS = ("#fyp", "#reels", "#explore", "#smallbusiness")
CATEGORY_COUNT = re.compile(r"\b\d+\s+(equipment\s+)?categories\b", re.I)


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(s):
    s = s.replace("Z", "+00:00")
    if "." in s:
        s = re.sub(r"\.\d+", "", s)
    return dt.datetime.fromisoformat(s)


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_log(posted):
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(posted, f, indent=1, ensure_ascii=False)
        f.write("\n")


# ---------- slots ----------

def open_slot(queue, t=None):
    """The slot key ("2026-11-24 10:00") whose window is open now, or None.
    queue["hold_slots"] lists slot keys another service already fills (the
    Metricool Shorts of Dec 1 to 7), so we post nothing in them."""
    local = (t or now()).astimezone(CENTRAL)
    slots = SLOTS_CT
    if queue.get("slots_ct"):  # e.g. ["10:00-11:00", "16:00-18:30"] overrides SLOTS_CT
        slots = [tuple(tuple(int(x) for x in end.split(":")) for end in s.split("-"))
                 for s in queue["slots_ct"]]
    for (h, m), (lh, lm) in slots:
        start = local.replace(hour=h, minute=m, second=0, microsecond=0)
        end = local.replace(hour=lh, minute=lm, second=0, microsecond=0)
        if start - dt.timedelta(minutes=SLOT_EARLY_MINUTES) <= local <= end:
            key = start.strftime("%Y-%m-%d %H:%M")
            if key in set(queue.get("hold_slots", [])):
                return None
            return key
    return None


def live(posted):
    return [p for p in posted if p.get("status") in ("posted", "scheduled", "unconfirmed")]


def slot_used(posted, key):
    return any(p.get("slot") == key for p in live(posted))


def handed_last_24h(posted, t=None):
    t = t or now()
    return sum(1 for p in live(posted) if t - parse_time(p["time"]) < dt.timedelta(hours=24))


# ---------- copy checks ----------

def copy_problems(row):
    title, desc = row.get("title", ""), row.get("description", "")
    out = []
    if not title.strip():
        out.append("no title")
    if len(title) > 100:
        out.append(f"title is {len(title)} characters (YouTube allows 100)")
    if len(desc) > 5000:
        out.append("description is over 5000 characters")
    if any(c in title + desc for c in "<>"):
        out.append("YouTube rejects < and > in titles and descriptions")
    lines = [ln.strip() for ln in desc.strip().splitlines() if ln.strip()]
    if not lines or not lines[-1].endswith("?"):
        out.append("description must end with the open question")
    low = (title + " " + desc).lower()
    if CATEGORY_COUNT.search(low):
        out.append("never state a category count")
    for tag in BANNED_TAGS:
        if re.search(re.escape(tag) + r"\b", low):
            out.append(f"banned tag {tag}")
    if row.get("audience") == "dealer" and ("list it free" in low or "free to list" in low):
        out.append("storefront clips never say list it free")
    return out


# ---------- rotation ----------

def rotation_state(queue_rows):
    """(history, library by slug) or (None, {}) when rotation.py isn't checked out."""
    if rot is None:
        return None, {}
    lib = {v["slug"]: v for v in rot.library()}
    try:
        return rot.uses(), lib
    except Exception as e:  # a broken log must not stop posting; say so loudly
        print(f"::warning::rotation history unreadable ({e}); posting without the rotation check")
        return None, lib


def entry_for(row, lib):
    v = dict(lib.get(row.get("library_slug") or row["slug"], {}))
    v.setdefault("slug", row.get("library_slug") or row["slug"])
    if row.get("machine"):
        v["machine"] = row["machine"]
    return v


# ---------- picking ----------

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", html.unescape(s or "").lower()).strip()


def channel_titles():
    """Titles of the channel's latest 15 videos from its public feed (best effort)."""
    try:
        req = urllib.request.Request(FEED, headers={"User-Agent": "yardswaps-media-youtube"})
        with urllib.request.urlopen(req, timeout=30) as r:
            xml = r.read().decode("utf-8", errors="replace")
        return [html.unescape(t) for t in re.findall(r"<media:title>(.*?)</media:title>", xml, re.S)]
    except Exception as e:
        print(f"  could not read the channel feed ({e}); relying on posted.json for repeats")
        return None


def candidates(queue, posted, on_channel, t=None):
    """Queue rows in order with why each can or can't post now:
    [(row, "ok" | "fallback" | reason)]."""
    t = t or now()
    done = {p["slug"] for p in live(posted)}
    titles = {norm(x) for x in (on_channel or [])}
    history, lib = rotation_state(queue.get("shorts", []))
    out = []
    for row in queue.get("shorts", []):
        if row.get("skip"):
            out.append((row, "skip: " + row.get("skip_reason", "marked skip")))
            continue
        if row["slug"] in done:
            out.append((row, "already posted"))
            continue
        fails = [p for p in posted if p.get("slug") == row["slug"] and p.get("status") == "failed"]
        if len(fails) >= 2:
            out.append((row, "failed twice, fix or skip it: " + (fails[-1].get("error") or "")[:200]))
            continue
        if norm(row.get("title")) in titles:
            out.append((row, "already on the channel (same title)"))
            continue
        if row.get("not_before") and t < parse_time(row["not_before"]):
            out.append((row, f"waits until {row['not_before']}"))
            continue
        if not os.path.exists(os.path.join(ROOT, row["file"])) and not git_size(row["file"]):
            out.append((row, f"file missing: {row['file']}"))
            continue
        if not row.get("endcard"):
            # every video ends on the YardSwaps end card (Alan, 2026-11-25); brand/endcard/endcard.py
            # fix adds it and marks the row
            out.append((row, "waits for the end card check (brand/endcard/endcard.py fix)"))
            continue
        probs = copy_problems(row)
        if probs:
            out.append((row, "copy: " + "; ".join(probs)))
            continue
        if history is None:
            out.append((row, "ok"))
            continue
        v = entry_for(row, lib)
        if rot.allowed(v, history, t):
            out.append((row, "ok"))
        elif rot.fallback_ok(v, history, t):
            out.append((row, "fallback"))
        else:
            r = rot.runs(history, t).get(rot.machine_of(v))
            out.append((row, "rotation: machine shown recently, free from "
                        + (rot.fmt(rot.free_from(r)) if r else "?")))
    return out


def choose(cands):
    for want in ("ok", "fallback"):
        for row, why in cands:
            if why == want:
                return row, why
    return None, None


# ---------- Buffer ----------

class BufferError(Exception):
    pass


def gql(key, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "User-Agent": "yardswaps-media-youtube"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise BufferError(f"Buffer API {e.code}: {e.read().decode(errors='replace')[:500]}")
    if out.get("errors"):
        raise BufferError(f"Buffer API: {json.dumps(out['errors'])[:500]}")
    return out.get("data") or {}


Q_ORGS = "query { account { organizations { id name } } }"
Q_CHANNELS = """query Channels($org: OrganizationId!) {
  channels(input: { organizationId: $org }) { id name displayName service isQueuePaused }
}"""
Q_POSTS = """query Posts($org: OrganizationId!, $ch: [ChannelId!], $st: [PostStatus!]) {
  posts(first: 20, input: { organizationId: $org,
        sort: [{ field: dueAt, direction: desc }],
        filter: { status: $st, channelIds: $ch } }) {
    edges { node { id status dueAt sentAt externalLink text error { message rawError } } }
  }
}"""
M_CREATE = """mutation Create($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}"""


def find_youtube(key):
    seen = []
    for org in gql(key, Q_ORGS).get("account", {}).get("organizations", []):
        for ch in gql(key, Q_CHANNELS, {"org": org["id"]}).get("channels", []):
            seen.append((org, ch))
    for org, ch in seen:
        if str(ch.get("service", "")).lower() == "youtube":
            return org["id"], ch, seen
    return None, None, seen


def buffer_posts(key, org_id, channel, status):
    try:
        d = gql(key, Q_POSTS, {"org": org_id, "ch": [channel["id"]], "st": [status]})
    except BufferError:
        # Older schema: status takes one value, not a list.
        q = Q_POSTS.replace("[PostStatus!]", "PostStatus")
        d = gql(key, q, {"org": org_id, "ch": [channel["id"]], "st": status})
    return [e["node"] for e in d.get("posts", {}).get("edges", [])]


def git_size(rel):
    """Blob size from the tree, so a sparse checkout needn't hold the video."""
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-tree", "-l", "HEAD", "--", rel],
                             capture_output=True, text=True, timeout=30).stdout.split()
        return int(out[3]) if len(out) >= 4 else None
    except Exception:
        return None


def video_urls(rel):
    """Where Buffer can fetch the video: jsDelivr first (when under its size cap), then raw GitHub."""
    repo = os.environ.get("GITHUB_REPOSITORY") or "AIE-Solutions/yardswaps-media"
    ref = os.environ.get("GITHUB_SHA") or "main"
    path = os.path.join(ROOT, rel)
    size = os.path.getsize(path) if os.path.exists(path) else git_size(rel)
    raw = f"https://raw.githubusercontent.com/{repo}/{ref}/{rel}"
    if size and size <= JSDELIVR_MAX_BYTES:
        return [f"https://cdn.jsdelivr.net/gh/{repo}@{ref}/{rel}", raw]
    return [raw]


def video_url(rel):
    return video_urls(rel)[0]


def url_is_video(url):
    """HEAD the URL. This also warms jsDelivr's copy of a new commit before Buffer
    asks for it: on 11-24 Buffer's first fetch of a fresh commit came back
    "Video could not be read from its URL"."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status == 200 and r.headers.get("Content-Type", "").startswith("video/")
    except Exception:
        return False


def create_post(key, channel, row, meta, due):
    """createPost with the first URL that serves the video; on Buffer's
    "could not be read" error, try the next URL."""
    urls = video_urls(row["file"])
    good = [u for u in urls if url_is_video(u)] or urls
    last = None
    for url in good:
        try:
            res = gql(key, M_CREATE, {"input": {
                "channelId": channel["id"], "text": row["description"],
                "schedulingType": "automatic", "mode": "customScheduled",
                "dueAt": due.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "metadata": {"youtube": meta},
                "assets": [{"video": {"url": url}}],
            }}).get("createPost") or {}
            if res.get("message") or not res.get("post"):
                raise BufferError(res.get("message") or f"unexpected reply {res}")
            return res, url
        except BufferError as e:
            last = e
            if "could not be read" not in str(e).lower():
                raise
            print(f"  Buffer could not read {url.split('/')[2]}, trying the next URL")
    raise last


def sync_log(key, org_id, channel, posted):
    """Mark scheduled posts posted (with link) or failed (with reason)."""
    try:
        sent = {n["id"]: n for n in buffer_posts(key, org_id, channel, "sent")}
        errs = {n["id"]: n for n in buffer_posts(key, org_id, channel, "error")}
    except BufferError as e:
        print(f"  could not read the channel's Buffer posts: {e}")
        return [], []
    for p in posted:
        if p.get("status") not in ("scheduled", "unconfirmed"):
            continue
        if p.get("buffer_id") in sent:
            n = sent[p["buffer_id"]]
            p.update(status="posted", url=n.get("externalLink") or "", sent=n.get("sentAt"))
        elif p.get("buffer_id") in errs:
            err = errs[p["buffer_id"]].get("error") or {}
            p.update(status="failed", error=(err.get("rawError") or err.get("message") or "")[:500])
            print(f"::warning::{p['slug']} failed on YouTube: {p['error']}")
        elif p.get("status") == "scheduled" and now() - parse_time(p["time"]) > dt.timedelta(hours=3):
            p["status"] = "unconfirmed"
            print(f"::warning::{p['slug']} was handed to Buffer at {p['time']} and isn't marked sent. "
                  "Look at the YouTube channel in Buffer.")
    return list(sent.values()), list(errs.values())


def buffer_last_24h(sent):
    """Posts Buffer published on this channel in the last 24 hours (ours or anyone's)."""
    t = now()
    return sum(1 for n in sent if n.get("sentAt") and t - parse_time(n["sentAt"]) < dt.timedelta(hours=24))


# ---------- main ----------

def summary_out(lines):
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### YouTube Shorts run\n\n```\n" + text + "\n```\n")


def set_output(name, value):
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")


def main():
    key = os.environ.get("BUFFER_API_KEY", "").strip()
    dry = os.environ.get("DRY_RUN") == "1"
    check = os.environ.get("CHECK") == "1"
    gate = os.environ.get("CHECK_ONLY") == "1"
    force = (os.environ.get("SLUG") or "").strip() or None
    queue = load(QUEUE, {"shorts": []})
    posted = load(LOG, [])

    slot = open_slot(queue)
    if gate:
        due = bool(force or dry or check or (slot and not slot_used(posted, slot)
                                             and handed_last_24h(posted) < MAX_PER_24H))
        print(f"slot={slot} due={int(due)}")
        set_output("due", "1" if due else "0")
        return 0

    lines = []
    if not key and not dry:
        print("::notice::BUFFER_API_KEY is not set, so nothing went to YouTube.")
        return 0

    org_id = channel = None
    sent = []
    if key:
        org_id, channel, seen = find_youtube(key)
        if check or not channel:
            for org, ch in seen:
                print(f"  Buffer channel: {ch.get('service')} {ch.get('name')} "
                      f"(org {org.get('name')}, paused={ch.get('isQueuePaused')})")
        if not channel:
            print("::error::No YouTube channel in Buffer. Connect the YardSwaps channel in Buffer (youtube/README.md).")
            return 1
        sent, errs = sync_log(key, org_id, channel, posted)
        if check:
            print(f"YouTube channel in Buffer: {channel.get('name')} (paused={channel.get('isQueuePaused')})")
            for label, nodes in (("sent", sent), ("error", errs)):
                print(f"  Buffer {label}: {len(nodes)}")
                for n in nodes[:8]:
                    print("    " + json.dumps({k: n.get(k) for k in
                                               ("dueAt", "sentAt", "externalLink", "error")})
                          + " " + (n.get("text") or "")[:60].replace("\n", " "))

    on_channel = channel_titles()
    if check and on_channel is not None:
        print(f"Latest {len(on_channel)} videos on the channel:")
        for x in on_channel:
            print("  " + x)

    cands = candidates(queue, posted, on_channel)
    if force:
        row = next((r for r in queue.get("shorts", []) if r["slug"] == force), None)
        why = "forced"
        if row and copy_problems(row):
            lines.append(f"youtube: {force} not posted, copy: {'; '.join(copy_problems(row))}")
            row = None
        elif not row:
            lines.append(f"youtube: no queue row with slug {force}")
    else:
        row, why = choose(cands)

    if check or dry:
        lines.append(f"slot open now: {slot or 'none'} (Central); handed to Buffer in the last 24 h: "
                     f"{handed_last_24h(posted)} ours, {buffer_last_24h(sent)} published by Buffer")
        lines.append("queue:")
        for r, w in cands:
            lines.append(f"  {r['slug']}: {w}")
        if row:
            lines.append(f"\nnext pick: {row['slug']} ({why})\nvideo: {video_url(row['file'])}\n"
                         f"title: {row['title']}\n\n{row['description']}\n")
        summary_out(lines)
        if key:
            save_log(posted)
        return 0

    failed = False
    if not row:
        lines.append(f"youtube: nothing to post ({'slot ' + slot if slot else 'no slot open'}); "
                     "every queue row is posted, waiting, held by the rotation or failing a copy check")
    elif not force and not slot:
        lines.append("youtube: no slot open now (10:00-11:00 am and 4:00-6:30 pm Central)")
    elif not force and slot_used(posted, slot):
        lines.append(f"youtube: slot {slot} already posted")
    elif handed_last_24h(posted) >= MAX_PER_24H:
        # Only our own posts count: HeyCatch also publishes to this channel through
        # Buffer (3 on Nov 22), so counting every Buffer post would block us for good.
        lines.append(f"youtube: skipped, we already handed {MAX_PER_24H} Shorts to Buffer in the last 24 hours")
    else:
        due = now() + dt.timedelta(minutes=SCHEDULE_AHEAD_MIN)
        entry = {"time": iso(now()), "slot": slot if not force else None, "slug": row["slug"],
                 "title": row["title"], "pick": why}
        if force:
            entry["forced"] = True
        for k in ("library_slug", "machine"):
            if row.get(k):
                entry[k] = row[k]
        meta = {"title": row["title"], "categoryId": str(row.get("category_id", "28")),
                "privacy": "public", "madeForKids": False, "notifySubscribers": True,
                "license": "youtube", "embeddable": True}
        try:
            res, url = create_post(key, channel, row, meta, due)
            entry.update(status="scheduled", buffer_id=res["post"]["id"], due=res["post"].get("dueAt"),
                         video_host=url.split("/")[2])
            lines.append(f"youtube: handed {row['slug']} to Buffer ({why}), public about "
                         f"{due.astimezone(CENTRAL).strftime('%-I:%M %p')} Central\ntitle: {row['title']}")
        except BufferError as e:
            entry.update(status="failed", error=str(e)[:500])
            lines.append(f"youtube: FAILED {row['slug']}: {e}")
            failed = True
        posted.append(entry)

    left = sum(1 for _, w in cands if w in ("ok", "fallback") or w.startswith(("rotation", "waits")))
    lines.append(f"queue rows still to post: {left}")
    if left < 4:
        lines.append("::warning::fewer than 4 Shorts left in youtube/queue.json; the weekly batch should add rows")
    save_log(posted)
    summary_out(lines)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
