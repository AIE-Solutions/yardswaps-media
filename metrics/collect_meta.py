#!/usr/bin/env python3
"""Daily Instagram + Facebook stats snapshot for the weekly scorecard.

Runs from .github/workflows/metrics.yml once a day with the same
META_PAGE_TOKEN the Reels poster uses. Standard library only, read-only on
Meta (GET calls only). Writes metrics/meta/YYYY-MM-DD.json:

  account   IG followers / media count, FB Page followers / fans
  instagram every IG post of the last 45 days (ours and HeyCatch's): type,
            time, first caption line, likes, comments, and the Reel insights
            the token allows (views, reach, shares, saved, follows,
            total_interactions, average watch time). Ours carry their slug
            from reels/posted.json.
  facebook  our Facebook Reels from reels/posted.json: likes, comments and the
            video insights the token allows.

Insights need instagram_manage_insights / read_insights. Without them the
snapshot still has followers, likes and comments, and `insights` says which
metrics were refused, so the scorecard knows what it is ranking on.
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reels"))
from post_reels import GraphError, graph, load, POSTED  # noqa: E402

OUT_DIR = os.path.join(ROOT, "metrics", "meta")
DAYS = 45
IG_REEL_METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "follows",
                   "total_interactions", "ig_reels_avg_watch_time"]
IG_FEED_METRICS = ["views", "reach", "shares", "saved", "follows", "total_interactions"]
FB_REEL_METRICS = ["fb_reels_total_plays", "blue_reels_play_count", "post_impressions_unique",
                   "post_video_avg_time_watched", "post_video_followers", "post_video_social_actions"]


def first_line(text, n=90):
    return ((text or "").strip().split("\n")[0])[:n]


def insights(path, metrics, token, ok_cache):
    """Ask for every metric at once; if Meta refuses the set, find which ones work (cached per kind)."""
    key = tuple(metrics)
    usable = ok_cache.get(key, metrics)
    if not usable:
        return {}
    try:
        res = graph("GET", path, token, metric=",".join(usable))
        return {row["name"]: (row.get("values") or [{}])[0].get("value", row.get("total_value", {}).get("value"))
                for row in res.get("data", [])}
    except GraphError as e:
        if key in ok_cache:
            return {}
        good, refused = [], []
        for m in metrics:
            try:
                graph("GET", path, token, metric=m)
                good.append(m)
            except GraphError as e2:
                refused.append(f"{m}: {str(e2)[-160:]}")
        ok_cache[key] = good
        REFUSED.extend(refused)
        print(f"  insights {path.split('/')[-1]}: usable {good or 'none'}; first error {str(e)[-200:]}")
        return insights(path, metrics, token, ok_cache) if good else {}


REFUSED = []


def main():
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    page_id = os.environ.get("FB_PAGE_ID") or "1291163214083476"
    ig_id = os.environ.get("IG_USER_ID") or "17841429324062623"
    if not token:
        print("::notice::META_PAGE_TOKEN is not set, no snapshot taken.")
        return 0

    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=DAYS)
    posted = load(POSTED, [])
    ours_ig = {p["id"]: p for p in posted if p.get("platform") == "instagram" and p.get("status") == "posted" and p.get("id")}
    ours_fb = [p for p in posted if p.get("platform") == "facebook" and p.get("status") == "posted" and p.get("id")]
    snap = {"v": 1, "takenAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "account": {}, "instagram": [], "facebook": [], "insights": {}}
    errors = []

    try:
        snap["account"]["instagram"] = graph("GET", ig_id, token, fields="followers_count,follows_count,media_count")
    except GraphError as e:
        errors.append(f"ig account: {e}")
    try:
        snap["account"]["facebook"] = graph("GET", page_id, token, fields="followers_count,fan_count")
    except GraphError as e:
        errors.append(f"fb page: {e}")

    cache = {}
    try:
        res = graph("GET", f"{ig_id}/media", token, limit="50",
                    fields="id,caption,media_product_type,media_type,timestamp,permalink,like_count,comments_count")
        for m in res.get("data", []):
            ts = dt.datetime.strptime(m["timestamp"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
            if ts < since:
                continue
            reel = m.get("media_product_type") == "REELS"
            row = {
                "id": m["id"], "time": m["timestamp"][:19] + "Z", "type": m.get("media_product_type") or m.get("media_type"),
                "permalink": m.get("permalink"), "caption": first_line(m.get("caption")),
                "likes": m.get("like_count", 0), "comments": m.get("comments_count", 0),
                "ours": m["id"] in ours_ig, "slug": ours_ig.get(m["id"], {}).get("slug"),
                "repeat": bool(ours_ig.get(m["id"], {}).get("repeat")),
            }
            row.update(insights(f"{m['id']}/insights", IG_REEL_METRICS if reel else IG_FEED_METRICS, token, cache))
            snap["instagram"].append(row)
    except GraphError as e:
        errors.append(f"ig media: {e}")

    for p in ours_fb:
        t = p.get("time", "")
        try:
            if dt.datetime.strptime(t[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc) < since:
                continue
        except ValueError:
            continue
        row = {"id": p["id"], "time": t, "slug": p.get("slug"), "repeat": bool(p.get("repeat"))}
        try:
            v = graph("GET", p["id"], token, fields="likes.summary(true).limit(0),comments.summary(true).limit(0)")
            row["likes"] = v.get("likes", {}).get("summary", {}).get("total_count", 0)
            row["comments"] = v.get("comments", {}).get("summary", {}).get("total_count", 0)
        except GraphError as e:
            errors.append(f"fb reel {p['id']}: {str(e)[-200:]}")
        row.update(insights(f"{p['id']}/video_insights", FB_REEL_METRICS, token, cache))
        snap["facebook"].append(row)

    snap["insights"] = {"usable": {",".join(k): v for k, v in cache.items()}, "refused": REFUSED[:20]}
    snap["errors"] = errors[:20]
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, now.strftime("%Y-%m-%d") + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=1, sort_keys=True)
        f.write("\n")
    acct = snap["account"]
    print(f"IG followers {acct.get('instagram', {}).get('followers_count')}, FB followers "
          f"{acct.get('facebook', {}).get('followers_count')}; {len(snap['instagram'])} IG posts, "
          f"{len(snap['facebook'])} FB Reels; {len(errors)} errors -> {os.path.relpath(path, ROOT)}")
    for e in errors[:5]:
        print(f"::warning::{e[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
