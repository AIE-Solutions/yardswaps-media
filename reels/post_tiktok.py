#!/usr/bin/env python3
"""Post one YardSwaps video to TikTok per run, through Buffer's free plan.

Runs from .github/workflows/tiktok.yml twice a day. Standard library only.

Why Buffer and not TikTok's own API: TikTok's Content Posting API only
lets an unaudited app post private ("only me") videos from a private
account, and TikTok's guidelines say an audit is not granted for "a utility
tool to help upload contents to the account(s) you or your team manages"
(developers.tiktok.com/doc/content-sharing-guidelines). Buffer is an
audited TikTok partner, its free plan has the API (1 key, 1,000 requests
per channel per 30 days) and 10 queued posts per channel that refill once
they publish, so one post at a time costs nothing.

Same library, same pick order and same 10-day no-repeat rule as
post_reels.py. Repeats are ranked by the video's Instagram engagement
(TikTok numbers aren't readable here), so a cut that earned follows on
Instagram comes back first on TikTok too.

Buffer can't take a file upload, only a public link, so the video is
served from this public repo through jsDelivr at the exact commit (falls
back to raw.githubusercontent.com).

Env:
  BUFFER_API_KEY   Buffer personal API key (secret). Missing = log a notice
                   and exit 0.
  META_PAGE_TOKEN  optional, only to rank repeats by Instagram engagement
  SLUG             force one video (manual runs)
  DRY_RUN          "1" = pick and print the caption and link, post nothing
  CHECK            "1" = only list the Buffer channels (setup check)
  GITHUB_SHA, GITHUB_REPOSITORY  set by GitHub Actions
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import post_reels as reels  # noqa: E402  (same folder; shared pick and scoring)

API = "https://api.buffer.com"
ROOT = reels.ROOT
LOG = os.path.join(ROOT, "reels", "tiktok-posted.json")
PLATFORM = "tiktok"
MAX_OURS_PER_20H = 2
SCHEDULE_AHEAD_MIN = 5      # Buffer publishes this many minutes after the run
JSDELIVR_MAX_BYTES = 19_000_000  # jsDelivr serves GitHub files up to 20 MB
HEYCATCH = os.path.join(ROOT, "reels", "heycatch-tiktok.json")
# HeyCatch posts to TikTok at about :33 past 4 am, 12 pm and 8 pm Central.
HEYCATCH_SLOTS_CENTRAL = [(4, 33), (12, 33), (20, 33)]
HEYCATCH_CLEAR_MIN = 90


def clear_of_heycatch(due):
    """Move `due` (UTC) later until it is 90+ minutes from every HeyCatch slot."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Chicago")
    for _ in range(6):
        local = due.astimezone(tz)
        clash = None
        for day in (-1, 0, 1):
            for h, m in HEYCATCH_SLOTS_CENTRAL:
                slot = (local + dt.timedelta(days=day)).replace(hour=h, minute=m, second=0, microsecond=0)
                if abs((local - slot).total_seconds()) < HEYCATCH_CLEAR_MIN * 60:
                    clash = slot
        if clash is None:
            return due
        due = (clash + dt.timedelta(minutes=HEYCATCH_CLEAR_MIN + 1)).astimezone(dt.timezone.utc)
    return due


# ---------- caption ----------

def tiktok_caption(v, turn=0):
    # TikTok captions don't click, so the short link is for typing or the bio.
    # No handle in the text: the account is still being renamed.
    return (f"{v['body']}\n\nFollow for a new one every day. Get the free YardSwaps app: "
            f"yardswaps.com/t (link in bio).\n\n{reels.tt_tags(v, turn)}\n\n{v['question']}")


# ---------- Buffer GraphQL ----------

class BufferError(Exception):
    pass


def gql(key, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "User-Agent": "yardswaps-media-tiktok"})
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
Q_SENT = """query Sent($org: OrganizationId!, $ch: [ChannelId!]) {
  posts(first: 20, input: { organizationId: $org,
        sort: [{ field: dueAt, direction: desc }],
        filter: { status: sent, channelIds: $ch } }) {
    edges { node { id status sentAt externalLink } }
  }
}"""
M_CREATE = """mutation Create($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}"""


def find_tiktok(key):
    """Return (organization id, channel) for the first TikTok channel, plus all channels."""
    seen = []
    for org in gql(key, Q_ORGS).get("account", {}).get("organizations", []):
        for ch in gql(key, Q_CHANNELS, {"org": org["id"]}).get("channels", []):
            seen.append((org, ch))
    for org, ch in seen:
        if str(ch.get("service", "")).lower() == "tiktok":
            return org["id"], ch, seen
    return None, None, seen


def video_url(path):
    repo = os.environ.get("GITHUB_REPOSITORY") or "AIE-Solutions/yardswaps-media"
    ref = os.environ.get("GITHUB_SHA") or "main"
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if os.path.getsize(path) <= JSDELIVR_MAX_BYTES:
        return f"https://cdn.jsdelivr.net/gh/{repo}@{ref}/{rel}"
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{rel}"


# ---------- main ----------

def main():
    key = os.environ.get("BUFFER_API_KEY", "").strip()
    dry = os.environ.get("DRY_RUN") == "1"
    check = os.environ.get("CHECK") == "1"
    force = (os.environ.get("SLUG") or "").strip() or None
    meta = os.environ.get("META_PAGE_TOKEN", "").strip()

    if not key and not dry:
        print("::notice::BUFFER_API_KEY is not set yet, so nothing went to TikTok. See reels/README.md, TikTok.")
        return 0

    videos = reels.load(reels.LIBRARY, {"videos": []})["videos"]
    posted = reels.load(LOG, [])
    summary, failed = [], False

    org_id = channel = None
    if key:
        org_id, channel, seen = find_tiktok(key)
        if check or not channel:
            for org, ch in seen:
                print(f"  Buffer channel: {ch.get('service')} {ch.get('name')} "
                      f"(org {org.get('name')}, paused={ch.get('isQueuePaused')})")
        if not channel:
            print("::error::No TikTok channel in Buffer yet. Connect TikTok in Buffer (README, TikTok step 2).")
            return 1
        if check:
            print(f"TikTok channel found: {channel.get('name')}. Setup is complete.")
            return 0
        # Fill in links for earlier posts that Buffer has published since.
        try:
            sent = gql(key, Q_SENT, {"org": org_id, "ch": [channel["id"]]})
            done = {e["node"]["id"]: e["node"] for e in sent.get("posts", {}).get("edges", [])}
            for p in posted:
                n = done.get(p.get("buffer_id"))
                if n and p.get("status") == "scheduled":
                    p.update(status="posted", url=n.get("externalLink") or "", sent=n.get("sentAt"))
        except BufferError as e:
            print(f"  could not read published posts from Buffer: {e}")
        stale = [p for p in posted if p.get("status") == "scheduled"
                 and reels.now() - reels.parse_time(p["time"]) > dt.timedelta(hours=3)]
        for p in stale:
            p["status"] = "unconfirmed"
            print(f"::warning::{p['slug']} was handed to Buffer at {p['time']} but Buffer hasn't marked it sent. "
                  "Check the TikTok channel in Buffer for a failed post.")

    # Count scheduled and posted as "used" for picking and the daily cap.
    used = [dict(p, platform=PLATFORM, status="posted") for p in posted
            if p.get("status") in ("posted", "scheduled", "unconfirmed")]
    # Videos HeyCatch already put on TikTok count as posted for the 10-day
    # rule (but not for the daily cap): [{"slug": ..., "time": ISO}, ...].
    hc = [dict(p, platform=PLATFORM, status="posted") for p in reels.load(HEYCATCH, [])
          if p.get("slug") and p.get("time")]
    video, repeat = reels.pick(videos, used + hc, PLATFORM, force)
    if repeat and not force and meta:
        scores = reels.ig_scores(meta, reels.load(reels.POSTED, []))
        video, repeat = reels.pick(videos, used + hc, PLATFORM, force, scores)

    if not video:
        summary.append(f"tiktok: skipped, every video was posted in the last {reels.MIN_GAP_DAYS} days")
    else:
        path = os.path.join(ROOT, video["file"])
        caption = tiktok_caption(video, turn=len(used))
        url = video_url(path)
        if dry:
            summary.append(f"tiktok: would post {video['slug']} (repeat={repeat})\n{url}\n\n{caption}\n")
        elif not force and reels.ours_recent(used, PLATFORM) >= MAX_OURS_PER_20H:
            summary.append(f"tiktok: skipped, already posted {MAX_OURS_PER_20H} in the last 20 hours")
        else:
            due = clear_of_heycatch(reels.now() + dt.timedelta(minutes=SCHEDULE_AHEAD_MIN))
            entry = {"time": reels.iso(reels.now()), "platform": PLATFORM,
                     "slug": video["slug"], "repeat": repeat}
            try:
                res = gql(key, M_CREATE, {"input": {
                    "channelId": channel["id"], "text": caption,
                    "schedulingType": "automatic", "mode": "customScheduled",
                    "dueAt": due.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "assets": [{"video": {"url": url, "metadata": {"thumbnailOffset": 1500}}}],
                }}).get("createPost") or {}
                if res.get("message") or not res.get("post"):
                    raise BufferError(res.get("message") or f"unexpected reply {res}")
                entry.update(status="scheduled", buffer_id=res["post"]["id"], due=res["post"].get("dueAt"))
                summary.append(f"tiktok: handed {video['slug']} to Buffer, goes live about "
                               f"{due.strftime('%H:%M')} UTC")
            except BufferError as e:
                entry.update(status="failed", error=str(e)[:500])
                summary.append(f"tiktok: FAILED {video['slug']}: {e}")
                failed = True
            posted.append(entry)

    if not dry:
        with open(LOG, "w", encoding="utf-8") as f:
            json.dump(posted, f, indent=1, ensure_ascii=False)
            f.write("\n")
    text = "\n".join(summary)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### TikTok run\n\n```\n" + text + "\n```\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
