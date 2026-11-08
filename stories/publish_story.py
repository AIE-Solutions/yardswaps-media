#!/usr/bin/env python3
"""Publish today's LIST IT FREE image as an Instagram Story (Instagram only).

Runs in GitHub Actions (story.yml) with META_PAGE_TOKEN. Never prints it.

  python3 stories/publish_story.py check     -> already=true|false (skip if today's is up)
  python3 stories/publish_story.py publish   -> one publish attempt, then a live check

Rules (Alan, 2026-11-08): Stories only, never feed/Reels/Facebook/Threads, no
captions or comments. One publish attempt per day: a failure is logged and
reported, never retried. "Today" is America/Chicago. Log: stories/posted.json.
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reels"))
from post_reels import GraphError, graph  # noqa: E402

LOG = os.path.join(ROOT, "stories", "posted.json")
CT = ZoneInfo("America/Chicago")


def out(**kv):
    for k, v in kv.items():
        print(f"{k}={v}")
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f:
            for k, v in kv.items():
                f.write(f"{k}={v}\n")


def load_log():
    try:
        with open(LOG, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_log(log):
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=1)
        f.write("\n")


def today():
    return datetime.now(CT).strftime("%Y-%m-%d")


def active_story_ids(token, ig_id):
    r = graph("GET", f"{ig_id}/stories", token, fields="id,timestamp,media_type", limit="50")
    return {m["id"] for m in r.get("data", [])}


def check(token, ig_id):
    date = today()
    mine = [e for e in load_log() if e.get("date") == date]
    if mine:
        # Any logged attempt today (posted, failed or unknown) means no second
        # publish today: Alan's rule is report a failure, never retry it.
        print(f"LIST IT FREE already handled today ({date}): {mine[-1].get('status')} {mine[-1].get('media_id', '')}")
        out(already="true")
        return
    out(already="false")


def publish(token, ig_id):
    date = today()
    image_url = os.environ["IMAGE_URL"]
    machine = os.environ["MACHINE"]
    if not image_url.startswith("https://raw.githubusercontent.com/AIE-Solutions/yardswaps-media/"):
        sys.exit(f"refusing image url {image_url}")
    log = load_log()
    entry = {"date": date, "machine": machine, "image_url": image_url,
             "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "status": "attempted"}
    log.append(entry)
    save_log(log)  # recorded before the call, so a crash can't lead to a second post today
    try:
        cid = graph("POST", f"{ig_id}/media", token, media_type="STORIES", image_url=image_url)["id"]
        for _ in range(30):
            st = graph("GET", cid, token, fields="status_code").get("status_code")
            if st == "FINISHED":
                break
            if st in ("ERROR", "EXPIRED"):
                raise GraphError(f"Instagram processing failed: {st}")
            time.sleep(5)
        else:
            raise GraphError("Instagram still processing after 150 s; nothing published")
        mid = graph("POST", f"{ig_id}/media_publish", token, creation_id=cid)["id"]
    except GraphError as e:
        entry.update(status="failed", error=str(e)[:400])
        save_log(log)
        out(result="failed", detail=str(e)[:200].replace("\n", " "))
        sys.exit(1)
    posted = datetime.now(timezone.utc)
    entry.update(status="posted", media_id=mid,
                 expires=(posted + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    save_log(log)
    live = False
    for _ in range(6):
        try:
            if mid in active_story_ids(token, ig_id):
                live = True
                break
        except GraphError as e:
            print(f"live check error: {e}")
        time.sleep(10)
    entry["verified_live"] = live
    save_log(log)
    exp_ct = (posted + timedelta(hours=24)).astimezone(CT).strftime("%a %b %-d, %-I:%M %p Central")
    out(result="posted" if live else "unverified", media_id=mid, expires=exp_ct.replace(" ", "_"))
    if not live:
        sys.exit(1)


def main():
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    if not token:
        sys.exit("META_PAGE_TOKEN not set; nothing posted")
    ig_id = os.environ.get("IG_USER_ID") or "17841429324062623"
    {"check": check, "publish": publish}[sys.argv[1]](token, ig_id)


if __name__ == "__main__":
    main()
