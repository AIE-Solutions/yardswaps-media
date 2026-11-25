"""Account health for every platform we post to: a 0-10 score, a level, a daily cap and fixes.

Our version of HeyCatch's "Account health" (Alan 2026-11-25: "End to end a clone of heychat").
HeyCatch scores each connected account from measurable facts, gives it a level, and the level sets how
many posts a day it gets; when an account slips (views fall under a quarter of usual, followers drop
10% in a week) it pauses posting there for 48 hours. This does the same from data we already keep:

  - follower counts per day      metrics/meta/YYYY-MM-DD.json (Instagram, Facebook; daily)
  - likes + comments per post    the same snapshots, our posts only
  - views (optional)             studio/health-inputs.json, numbers an agent read from Metricool:
                                 {"instagram": {"viewsPerPost7d": n, "viewsPerPostBefore": n,
                                                "views7d": n, "viewsBeforePerWeek": n}, ...}
                                 views per post score; total views are shown for context
  - posting errors               reels/posted.json, reels/tiktok-posted.json, youtube/posted.json
  - profile drift                profiles/status.json (fields that don't match profiles.json)

The posters ask `cap(platform)` before each post. Policy (studio/health-policy.json):
  "enforce": "pause"  only the hard pauses stop posting (the safe default);
  "enforce": "caps"   the level's daily cap applies too;
  "enforce": "off"    report only.
Pure computation at post time, nothing to commit: the posters always see today's numbers.

    python3 studio/health.py            # prints the table and writes studio/HEALTH.md
"""
import datetime as dt
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
POLICY = os.path.join(HERE, "health-policy.json")
INPUTS = os.path.join(HERE, "health-inputs.json")
REPORT = os.path.join(HERE, "HEALTH.md")
INPUTS_MAX_DAYS = 4
META_DIR = os.path.join(ROOT, "metrics", "meta")
LOGS = {
    "reels": os.path.join(ROOT, "reels", "posted.json"),
    "tiktok": os.path.join(ROOT, "reels", "tiktok-posted.json"),
    "youtube": os.path.join(ROOT, "youtube", "posted.json"),
}
PLATFORMS = ("instagram", "facebook", "threads", "tiktok", "youtube")

# Our posts a day per level (feed posts only; Stories are not capped). "low" = score under 4.5.
CAPS = {
    "instagram": {"trusted": 10, "regular": 7, "held": 4, "low": 2},
    "facebook": {"trusted": 10, "regular": 7, "held": 4, "low": 2},
    "threads": {"trusted": 10, "regular": 7, "held": 4, "low": 2},
    "tiktok": {"trusted": 3, "regular": 2, "held": 1, "low": 1},
    "youtube": {"trusted": 3, "regular": 2, "held": 1, "low": 1},
}
PAUSE_HOURS = 48
LIMIT_WORDS = re.compile(r"spam|too much activity|limiting|rate limit|restricted|action blocked", re.I)


def now():
    return dt.datetime.now(dt.timezone.utc)


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def parse(ts):
    try:
        d = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def snapshots(days=35):
    """[(date, snapshot)] oldest first."""
    out = []
    for f in sorted(glob.glob(os.path.join(META_DIR, "*.json")))[-days:]:
        d = load(f, None)
        if d:
            out.append((os.path.basename(f)[:10], d))
    return out


def followers(snaps, platform):
    key = {"instagram": ("instagram", "followers_count"), "facebook": ("facebook", "followers_count")}.get(platform)
    if not key:
        return []
    return [(day, s.get("account", {}).get(key[0], {}).get(key[1])) for day, s in snaps
            if isinstance(s.get("account", {}).get(key[0], {}).get(key[1]), int)]


def engagement(snaps, platform, at):
    """(avg likes+comments per our post, last 7 days; the same for the 21 days before), from the newest snapshot."""
    if not snaps or platform not in ("instagram", "facebook"):
        return None, None
    # each snapshot holds only the newest posts, so merge them all (newest numbers win)
    merged = {}
    for _, snap in snaps:
        for p in snap.get(platform) or []:
            merged[p.get("id") or (p.get("slug"), p.get("time"))] = p
    recent, before = [], []
    for p in merged.values():
        if platform == "instagram" and not p.get("ours"):
            continue
        t = parse(p.get("time"))
        if not t:
            continue
        age = (at - t).days
        val = (p.get("likes") or 0) + (p.get("comments") or 0)
        if age < 2:
            continue  # too fresh to judge
        (recent if age < 9 else before if age < 30 else []).append(val)
    avg = lambda xs: sum(xs) / len(xs) if len(xs) >= 3 else None
    return avg(recent), avg(before)


def step(ratio, cuts):
    for limit, pts in cuts:
        if ratio >= limit:
            return pts
    return cuts[-1][1]


def posts_by_platform():
    out = {p: [] for p in PLATFORMS}
    for p in load(LOGS["reels"], []) + load(LOGS["tiktok"], []):
        if p.get("platform") in out:
            out[p["platform"]].append(p)
    for p in load(LOGS["youtube"], []):
        out["youtube"].append({**p, "platform": "youtube"})
    return out


def score_platform(platform, snaps, logs, inputs, profile, at):
    score, reasons, fixes = 6.0, [], []
    pause_until = None
    # followers, 7 days
    fol = followers(snaps, platform)
    if len(fol) >= 6 and fol[0][1]:
        last = fol[-1][1]
        week = next((v for d, v in reversed(fol) if (at.date() - dt.date.fromisoformat(d)).days >= 7), fol[0][1])
        pct = (last - week) / week * 100 if week else 0
        pts = 1 if pct >= 2 else 0.5 if pct >= 0.5 else 0 if pct > -1 else -1 if pct > -3 else -2
        score += pts
        reasons.append(f"followers {week} -> {last} in a week ({pct:+.1f}%)")
        if pct <= -10:
            pause_until = at + dt.timedelta(hours=PAUSE_HOURS)
            reasons.append("followers fell 10% or more in a week: pause")
        elif pct < -1:
            fixes.append("Followers are falling: post fewer, better clips here and answer every comment for a few days.")
    # engagement per post
    recent, before = engagement(snaps, platform, at)
    if recent is not None and before and before >= 1:  # under 1 a post is noise, not a trend
        r = recent / before
        score += step(r, [(1.2, 1), (0.8, 0), (0.5, -1), (0, -2)])
        reasons.append(f"likes+comments per post {before:.1f} -> {recent:.1f} ({r:.2f}x)")
        if r < 0.8:
            fixes.append("Each post gets less engagement than it did: repeat the best openers (metrics/rank.json boost) and retire the weakest.")
    # views (Metricool numbers, when an agent saved them)
    v = (inputs or {}).get(platform) or {}
    if v.get("views7d") is not None and v.get("viewsBeforePerWeek"):
        reasons.append(f"views a week, all posts {v['viewsBeforePerWeek']} -> {v['views7d']} "
                       f"({v['views7d'] / v['viewsBeforePerWeek']:.2f}x)")
    if v.get("viewsPerPost7d") is not None and v.get("viewsPerPostBefore"):
        r = v["viewsPerPost7d"] / v["viewsPerPostBefore"]
        score += step(r, [(1.2, 1), (0.8, 0), (0.5, -1), (0.25, -2), (0, -3)])
        reasons.append(f"views per post {v['viewsPerPostBefore']} -> {v['viewsPerPost7d']} ({r:.2f}x)")
        if r < 0.25:
            pause_until = max(pause_until or at, at + dt.timedelta(hours=PAUSE_HOURS))
            reasons.append("views under a quarter of a usual week: pause")
    # posting errors and platform warnings, 7 days
    week = [p for p in logs if (t := parse(p.get("time"))) and at - t <= dt.timedelta(days=7)]
    failed = [p for p in week if p.get("status") == "failed"]
    limited = [p for p in week if LIMIT_WORDS.search(str(p.get("error") or ""))]
    ours = [p for p in week if p.get("status") in ("posted", "scheduled")]
    reasons.append(f"{len(ours)} of our posts in 7 days ({len(ours) / 7:.1f} a day), {len(failed)} failed")
    if limited:
        score -= 2
        last = max(parse(p["time"]) for p in limited)
        pause_until = max(pause_until or at, last + dt.timedelta(hours=72))
        reasons.append(f"platform warning: {str(limited[-1].get('error'))[:80]}")
    elif len(failed) >= 3:
        score -= 1
        fixes.append(f"{len(failed)} posts failed this week ({str(failed[-1].get('error'))[:60]}): fix the cause before posting more.")
    if not ours:
        fixes.append("None of our posts went out here in 7 days: check the poster's token and that its slot fires.")
    # profile
    bad = [k for k, f in (profile or {}).items() if isinstance(f, dict) and f.get("ok") is False]
    if bad:
        score -= min(1.0, 0.5 * len(bad))
        fixes.append(f"Profile fields that don't match profiles.json: {', '.join(bad)}.")
    score = max(0.0, min(10.0, round(score, 1)))
    level = "trusted" if score >= 7.5 else "regular" if score >= 6 else "held" if score >= 4.5 else "low"
    paused = bool(pause_until and pause_until > at)
    return {"platform": platform, "score": score, "level": level, "cap": 0 if paused else CAPS[platform][level],
            "pausedUntil": pause_until.strftime("%Y-%m-%dT%H:%M:%SZ") if paused else None,
            "postsPerDay7d": round(len(ours) / 7, 1), "reasons": reasons, "fixes": fixes}


def report(at=None):
    at = at or now()
    snaps = snapshots()
    logs = posts_by_platform()
    inputs = load(INPUTS, {})
    try:  # views read more than INPUTS_MAX_DAYS ago could pause on old news: ignore them
        read = dt.datetime.fromisoformat(str(inputs.get("readAt", "")).replace("Z", "+00:00"))
        if at - read > dt.timedelta(days=INPUTS_MAX_DAYS):
            inputs = {}
    except ValueError:
        inputs = {}
    prof = load(os.path.join(ROOT, "profiles", "status.json"), {})
    out = {}
    for p in PLATFORMS:
        profile = prof.get(p) if p in ("instagram", "facebook") else None
        out[p] = score_platform(p, snaps, logs[p], inputs, profile, at)
    return {"checkedAt": at.strftime("%Y-%m-%dT%H:%M:%SZ"), "policy": policy(), "platforms": out}


def policy():
    p = load(POLICY, {})
    mode = p.get("enforce", "pause")
    return mode if mode in ("off", "pause", "caps") else "pause"


def cap(platform, at=None):
    """The most of OUR feed posts this platform may get today (Central day), or None for no limit.
    Never raises: a broken health check must not stop posting."""
    try:
        mode = policy()
        if mode == "off" or platform not in PLATFORMS:
            return None
        h = report(at)["platforms"][platform]
        if h["pausedUntil"]:
            return 0
        return h["cap"] if mode == "caps" else None
    except Exception as e:  # pragma: no cover
        print(f"  health check failed for {platform}: {e}; no cap")
        return None


def posted_today(entries, platform, at=None):
    """Our posts to a platform since midnight Central (CST, UTC-6; a DST hour early is fine for a cap)."""
    at = at or now()
    start = (at - dt.timedelta(hours=6)).replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(hours=6)
    return sum(1 for p in entries if p.get("platform", "youtube") == platform
               and p.get("status") in ("posted", "scheduled") and (t := parse(p.get("time"))) and t >= start)


def main():
    r = report()
    names = {"instagram": "Instagram", "facebook": "Facebook", "threads": "Threads", "tiktok": "TikTok", "youtube": "YouTube"}
    lines = [f"# Account health, {r['checkedAt']}", "",
             f"Policy: `{r['policy']}` (studio/health-policy.json). Scores 0-10 from measurable facts; level sets the daily cap.", "",
             "| Platform | Score | Level | Cap a day | Ours a day now | Paused until |", "|---|---|---|---|---|---|"]
    for p, h in r["platforms"].items():
        lines.append(f"| {names[p]} | {h['score']} | {h['level']} | {h['cap']} | {h['postsPerDay7d']} | {h['pausedUntil'] or ''} |")
    for p, h in r["platforms"].items():
        lines += ["", f"## {names[p]}", *[f"- {x}" for x in h["reasons"]]]
        if h["fixes"]:
            lines += ["", "Fixes:", *[f"1. {x}" for x in h["fixes"]]]
    text = "\n".join(lines) + "\n"
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
