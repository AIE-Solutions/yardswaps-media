#!/usr/bin/env python3
"""Upload YardSwaps long (16:9) YouTube videos from youtube/long-queue.json.

Runs from .github/workflows/youtube-long.yml. Standard library only.

This is the YardSwaps, Inc. internal publishing client: it uploads only the
company's own finished videos to the company's own YouTube channel
(YardSwaps, UCC_TtVN5pOfs4z9OruWUlhw). It has no users, no sign-in for anyone
else and reads no one else's YouTube data. Calls it makes, all on the
channel owner's OAuth grant (scope youtube.upload + youtube.readonly):
  - oauth2.googleapis.com/token          refresh the access token
  - channels.list (mine) + playlistItems  the channel's last 50 uploads, so a
                                           title already on the channel is
                                           never uploaded twice (2 units)
  - videos.insert (resumable)             the upload itself (100 units)
  - thumbnails.set                        the YardSwaps brand card (50 units)
  - captions.insert                       the narration's .srt (400 units)
About 550 quota units per video, one video a day: well inside the default
10,000-unit daily quota.

Why it waits for LIVE: Google restricts videos.insert uploads from an
unaudited API project to private ("All videos uploaded via the videos.insert
endpoint from unverified API projects created after 28 July 2020 will be
restricted to private viewing mode", developers.google.com/youtube/v3/docs/
videos/insert). Until YouTube's API audit passes, scheduled runs post nothing;
MODE=test uploads one private video so the flow can be shown working.

Env:
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN  (GitHub secrets). Any
                 missing = notice, exit 0.
  MODE           "dry"  (default) print the queue and the next pick, upload nothing
                 "test" upload the next pick as PRIVATE, log it as a test
                 "post" upload the next pick as public (manual runs)
  LIVE           "1" lets scheduled runs post (repo variable YT_LONG_LIVE, set
                 once the audit passes). Scheduled runs with LIVE unset only
                 print the next pick.
  SLUG           upload this queue row (manual runs)
  EVENT          GITHUB_EVENT_NAME ("schedule" or "workflow_dispatch")
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QUEUE = os.path.join(HERE, "long-queue.json")
LOG = os.path.join(HERE, "long-posted.json")
CT = ZoneInfo("America/Chicago")
SLOT_CT = (dt.time(8, 30), dt.time(11, 0))   # one long video a day, 8:30-11:00 am Central
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3"
BANNED = ("33 categories", " categories of equipment")


class YTError(Exception):
    pass


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def http(method, url, token=None, body=None, headers=None, raw=False):
    h = dict(headers or {})
    if token:
        h["Authorization"] = f"Bearer {token}"
    data = body
    if isinstance(body, (dict, list)):
        data = json.dumps(body).encode()
        h.setdefault("Content-Type", "application/json; charset=UTF-8")
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            out = r.read()
            if raw:
                return r, out
            return json.loads(out or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise YTError(f"{method} {url.split('?')[0]} -> {e.code}: {detail}")


def access_token():
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    res = http("POST", "https://oauth2.googleapis.com/token", body=body,
               headers={"Content-Type": "application/x-www-form-urlencoded"})
    return res["access_token"]


def channel_titles(token):
    ch = http("GET", f"{API}/channels?part=contentDetails,snippet&mine=true", token)
    items = ch.get("items") or []
    if not items:
        raise YTError("this Google account has no YouTube channel")
    print(f"Channel: {items[0]['snippet']['title']} ({items[0]['id']})")
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = http("GET", f"{API}/playlistItems?part=snippet&maxResults=50&playlistId={uploads}", token)
    return {i["snippet"]["title"].strip().lower() for i in pl.get("items", [])}


def copy_problems(row):
    p = []
    t, d = row.get("title", ""), row.get("description", "")
    if not t or len(t) > 100:
        p.append("title empty or over 100 characters")
    if any(c in t + d for c in "<>"):
        p.append("< or > in title or description (YouTube rejects them)")
    if len(d) > 5000:
        p.append("description over 5000 characters")
    low = (t + " " + d).lower()
    if any(b in low for b in BANNED):
        p.append("category count in copy")
    paras = [x for x in d.strip().split("\n\n") if x.strip() and not x.lstrip().startswith("#")]
    if not paras or "?" not in paras[-1]:
        p.append("description doesn't end on the open question")
    if not row.get("endcard"):
        p.append("no end card mark (every video ends on the blue YardSwaps card)")
    if not os.path.exists(os.path.join(ROOT, row.get("file", ""))):
        p.append(f"file missing: {row.get('file')}")
    return p


def pick(queue, log, on_channel, slug=None):
    done = {e["slug"] for e in log if e.get("status") in ("posted", "test")}
    fails = {}
    for e in log:
        if e.get("status") == "failed":
            fails[e["slug"]] = fails.get(e["slug"], 0) + 1
    now = dt.datetime.now(dt.timezone.utc)
    for row in queue:
        s = row["slug"]
        if slug and s != slug:
            continue
        why = []
        if s in done:
            why.append("already uploaded (log)")
        if row.get("title", "").strip().lower() in on_channel:
            why.append("same title already on the channel")
        if row.get("skip"):
            why.append("marked skip")
        nb = row.get("not_before")
        if nb and dt.datetime.fromisoformat(nb.replace("Z", "+00:00")) > now:
            why.append(f"not before {nb}")
        if fails.get(s, 0) >= 2:
            why.append("failed twice, fix or skip it")
        why += copy_problems(row)
        print(f"  {s}: {'ok' if not why else '; '.join(why)}")
        if not why:
            return row
    return None


def upload_video(token, row, privacy):
    path = os.path.join(ROOT, row["file"])
    size = os.path.getsize(path)
    meta = {
        "snippet": {
            "title": row["title"],
            "description": row["description"],
            "tags": row.get("tags", []),
            "categoryId": row.get("category_id", "28"),   # Science & Technology
            "defaultLanguage": row.get("language", "en"),
            "defaultAudioLanguage": row.get("language", "en"),
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "license": "youtube",
        },
    }
    r, _ = http("POST", f"{UPLOAD}/videos?uploadType=resumable&part=snippet,status", token,
                body=json.dumps(meta).encode(), raw=True,
                headers={"Content-Type": "application/json; charset=UTF-8",
                         "X-Upload-Content-Type": "video/mp4",
                         "X-Upload-Content-Length": str(size)})
    loc = r.headers["Location"]
    with open(path, "rb") as f:
        data = f.read()
    res = http("PUT", loc, token, body=data,
               headers={"Content-Type": "video/mp4", "Content-Length": str(size)})
    return res["id"], res.get("status", {}).get("privacyStatus")


def set_thumbnail(token, vid, rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        data = f.read()
    http("POST", f"{UPLOAD}/thumbnails/set?videoId={vid}", token, body=data,
         headers={"Content-Type": "image/jpeg"})


def add_captions(token, vid, rel, lang):
    with open(os.path.join(ROOT, rel), "rb") as f:
        srt = f.read()
    b = uuid.uuid4().hex
    meta = json.dumps({"snippet": {"videoId": vid, "language": lang, "name": "", "isDraft": False}})
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n"
            f"--{b}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + srt + f"\r\n--{b}--\r\n".encode()
    http("POST", f"{UPLOAD}/captions?uploadType=multipart&part=snippet", token, body=body,
         headers={"Content-Type": f"multipart/related; boundary={b}"})


def in_slot(now_ct, log):
    if not (SLOT_CT[0] <= now_ct.time() < SLOT_CT[1]):
        return False
    today = now_ct.date().isoformat()
    return not any(e.get("day") == today and e.get("status") == "posted" for e in log)


def main():
    mode = (os.environ.get("MODE") or "dry").strip().lower()
    event = os.environ.get("EVENT", "workflow_dispatch")
    live = os.environ.get("LIVE") == "1"
    slug = (os.environ.get("SLUG") or "").strip() or None
    queue, log = load(QUEUE, []), load(LOG, [])
    now_ct = dt.datetime.now(CT)

    if event == "schedule":
        if not live:
            mode = "dry"
            print("LIVE is off (YouTube API audit not passed yet): printing the next pick only.")
        elif not in_slot(now_ct, log):
            print(f"No open slot at {now_ct:%H:%M} Central (8:30-11:00 am, once a day).")
            return
        else:
            mode = "post"

    have = all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    if not have:
        print("::notice::YT_CLIENT_ID, YT_CLIENT_SECRET or YT_REFRESH_TOKEN is not set; checking the queue offline.")
        pick(queue, log, set(), slug)
        return

    token = access_token()
    on_channel = channel_titles(token)
    print(f"Queue ({len(queue)} rows):")
    row = pick(queue, log, on_channel, slug)
    if not row:
        print("Nothing to upload.")
        return
    print(f"Next: {row['slug']} | {row['title']}")
    if mode == "dry":
        return

    privacy = "private" if mode == "test" else "public"
    entry = {"time": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "day": now_ct.date().isoformat(), "slug": row["slug"], "title": row["title"]}
    try:
        vid, got = upload_video(token, row, privacy)
        entry.update(status="test" if mode == "test" else "posted", video_id=vid,
                     url=f"https://www.youtube.com/watch?v={vid}", privacy=got)
        print(f"Uploaded {vid} ({got}): {entry['url']}")
        if mode == "post" and got != "public":
            entry["note"] = f"YouTube kept it {got}: the API audit has not lifted the private lock"
            print(f"::warning::{entry['note']}")
        for step, fn, arg in (("thumbnail", set_thumbnail, row.get("thumbnail")),
                              ("captions", add_captions, row.get("captions"))):
            if not arg:
                continue
            try:
                fn(token, vid, arg, row.get("language", "en")) if step == "captions" else fn(token, vid, arg)
                entry[step] = "ok"
            except YTError as e:
                entry[step] = f"failed: {e}"[:300]
                print(f"::warning::{step} failed: {e}")
    except YTError as e:
        entry.update(status="failed", error=str(e)[:500])
        print(f"::error::{e}")
    log.append(entry)
    save(LOG, log)
    if entry["status"] == "failed":
        sys.exit(1)


if __name__ == "__main__":
    main()
