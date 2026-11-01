#!/usr/bin/env python3
"""Post one YardSwaps Reel to Instagram and Facebook per run.

Runs from .github/workflows/reels.yml twice a day. Standard library only.

Picks the next video from reels/library.json (never-posted first, newest
first; then the one posted longest ago, at least MIN_GAP_DAYS ago), builds
the seller-first caption, uploads the file bytes straight to Meta (no public
URL needed) and appends the result to reels/posted.json.

Env:
  META_PAGE_TOKEN  Page access token for the YardSwaps Facebook Page that
                   never expires (secret). Missing = log a notice and exit 0.
  FB_PAGE_ID       default 1291163214083476
  IG_USER_ID       default 17841429324062623 (@yardswaps)
  PLATFORMS        "instagram,facebook" (default) or one of them
  SLUG             force one video (manual runs)
  DRY_RUN          "1" = pick and print captions, post nothing
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com/v23.0"
RUPLOAD_IG = "https://rupload.facebook.com/ig-api-upload/v23.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY = os.path.join(ROOT, "reels", "library.json")
POSTED = os.path.join(ROOT, "reels", "posted.json")

MIN_GAP_DAYS = 10          # same video never twice on a platform inside this
CLEAR_MINUTES = 90         # skip a platform if anything went up this recently (HeyCatch)
MAX_OURS_PER_20H = 2       # safety cap per platform, matches the two daily slots

FB_TAGS = "#usedequipment #equipmentforsale #sellequipment"


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

def ig_caption(v):
    return (f"{v['body']}\n\n{v['question']} Tell us in the comments.\n\n"
            f"Link in bio.\n{v['ig_tags']}")


def fb_caption(v):
    link = ("https://www.yardswaps.com/sell-equipment?utm_source=facebook"
            f"&utm_medium=social&utm_campaign=reels_{v['slug']}")
    return (f"{v['body']}\n\n{v['question']} Tell us in the comments.\n\n"
            f"List it free: {link}\n{FB_TAGS}")


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


def pick(videos, posted, platform, force=None):
    ok = [p for p in posted if p["platform"] == platform and p.get("status") == "posted"]
    last = {}
    for p in ok:
        t = parse_time(p["time"])
        last[p["slug"]] = max(last.get(p["slug"], t), t)
    if force:
        return next((v for v in videos if v["slug"] == force), None), force in last
    cutoff = now() - dt.timedelta(days=MIN_GAP_DAYS)
    usable = [v for v in videos if os.path.exists(os.path.join(ROOT, v["file"]))]
    fresh = [v for v in usable if v["slug"] not in last]
    if fresh:
        fresh.sort(key=lambda v: (-int(v.get("added", "0").replace("-", "")), v.get("priority", 999)))
        return fresh[0], False
    old = [v for v in usable if last[v["slug"]] <= cutoff]
    if not old:
        return None, False
    old.sort(key=lambda v: last[v["slug"]])
    return old[0], True


def ours_recent(posted, platform):
    since = now() - dt.timedelta(hours=20)
    return sum(1 for p in posted if p["platform"] == platform and p.get("status") == "posted"
               and parse_time(p["time"]) >= since)


# ---------- Instagram ----------

def ig_last_post_time(token, ig_id):
    r = graph("GET", f"{ig_id}/media", token, fields="timestamp", limit="3")
    times = [parse_time(m["timestamp"]) for m in r.get("data", []) if m.get("timestamp")]
    return max(times) if times else None


def ig_publish(token, ig_id, path, caption, repeat):
    size = os.path.getsize(path)
    fields = {"media_type": "REELS", "upload_type": "resumable",
              "caption": caption, "share_to_feed": "true"}
    container = None
    if repeat:
        # Repeats go out as Trial Reels: shown to non-followers first, shared
        # to followers only if they do well. Fall back to a normal Reel.
        try:
            container = graph("POST", f"{ig_id}/media", token,
                              trial_params=json.dumps({"graduation_strategy": "SS_PERFORMANCE"}),
                              **fields)
        except GraphError as e:
            print(f"  trial reel refused, posting as a normal reel: {e}")
    if container is None:
        container = graph("POST", f"{ig_id}/media", token, **fields)
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


# ---------- main ----------

def main():
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    dry = os.environ.get("DRY_RUN") == "1"
    page_id = os.environ.get("FB_PAGE_ID") or "1291163214083476"
    ig_id = os.environ.get("IG_USER_ID") or "17841429324062623"
    platforms = [p.strip() for p in (os.environ.get("PLATFORMS") or "instagram,facebook").split(",") if p.strip()]
    force = (os.environ.get("SLUG") or "").strip() or None

    if not token and not dry:
        print("::notice::META_PAGE_TOKEN is not set yet, so nothing was posted. See reels/README.md.")
        return 0

    videos = load(LIBRARY, {"videos": []})["videos"]
    posted = load(POSTED, [])
    summary, failed = [], False

    for platform in platforms:
        video, repeat = pick(videos, posted, platform, force)
        if not video:
            summary.append(f"{platform}: skipped, every video was posted in the last {MIN_GAP_DAYS} days")
            continue
        path = os.path.join(ROOT, video["file"])
        caption = ig_caption(video) if platform == "instagram" else fb_caption(video)
        if dry:
            summary.append(f"{platform}: would post {video['slug']} (repeat={repeat})\n{caption}\n")
            continue
        if not force and ours_recent(posted, platform) >= MAX_OURS_PER_20H:
            summary.append(f"{platform}: skipped, already posted {MAX_OURS_PER_20H} in the last 20 hours")
            continue
        entry = {"time": iso(now()), "platform": platform, "slug": video["slug"], "repeat": repeat}
        try:
            last = ig_last_post_time(token, ig_id) if platform == "instagram" else fb_last_post_time(token, page_id)
            if not force and last and now() - last < dt.timedelta(minutes=CLEAR_MINUTES):
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

    if not dry:
        with open(POSTED, "w", encoding="utf-8") as f:
            json.dump(posted, f, indent=1, ensure_ascii=False)
            f.write("\n")
    text = "\n".join(summary)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### Reels run\n\n```\n" + text + "\n```\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
