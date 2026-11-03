#!/usr/bin/env python3
"""Weekly YardSwaps scorecard: one place that says what is working, and acts on it.

Inputs (all optional; a missing source is reported, never guessed):
  metrics/meta/YYYY-MM-DD.json      daily IG/FB snapshots (collect_meta.py)
  reels/posted.json, reels/library.json, metrics/formats.json
  metrics/inputs/YYYY-MM-DD/        written each Monday by the YouTube report run:
      growth.json   the app's latest [GrowthDigest] log line (Railway logs)
      ops.json      the app's latest [OpsDigest] log line
      youtube.json  {"channel": {...}, "videos": [{id, title, views, subscribersGained, ours, slug?}]}
      metricool.json  optional extra per-network numbers

Outputs:
  metrics/scorecard.json  everything below, machine-readable (Monday batch reads it)
  metrics/SCORECARD.md    the same as a short plain-English page
  metrics/rank.json       what the Reels/TikTok posters act on: boost and retire per slug
  metrics/history.csv     one row per week of the goal numbers

Goals (Alan): engagement, followers/subscribers, app downloads; supply
(listings) is the bottleneck, so signups and listings sit next to them.
Standard library only.
"""
import csv
import datetime as dt
import glob
import json
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "metrics")

# Engagement points for one post. Follows count most (the goal), then the
# actions that spread a Reel (shares, saves), then comments and likes. Views
# only break ties when insights are missing. A signup from a Reel's tagged
# link is worth more than anything a post can earn on the platform.
WEIGHTS = {"follows": 10, "shares": 4, "saved": 3, "comments": 3, "likes": 1}
VIEW_POINTS = 1 / 100
SIGNUP_POINTS = 25
SETTLE_HOURS = 48           # a post younger than this is not judged yet
MIN_FORMAT_POSTS = 3        # a hook/angle/category needs this many settled posts for a verdict
BOOST_TOP = 3
RETIRE_MAX = 3              # retire at most this many per run
MIN_ACTIVE = 12             # never retire below this many usable videos
RETIRE_RATIO = 0.4          # per-post points under 40% of the median, after 2+ settled Instagram posts
WIN_RATIO, LOSE_RATIO = 1.3, 0.6


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def parse_t(s):
    try:
        return dt.datetime.strptime((s or "")[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def num(x):
    try:
        return float(x or 0)
    except (TypeError, ValueError):
        return 0.0


def points(row):
    p = sum(w * num(row.get(k)) for k, w in WEIGHTS.items())
    return p + VIEW_POINTS * reel_views(row)


def reel_views(row):
    return num(row.get("views") or row.get("fb_reels_total_plays") or row.get("blue_reels_play_count"))


def snapshots():
    files = sorted(glob.glob(os.path.join(M, "meta", "*.json")))
    return [(os.path.basename(f)[:10], load(f, {})) for f in files]


def latest_inputs(now):
    dirs = sorted(d for d in glob.glob(os.path.join(M, "inputs", "*")) if os.path.isdir(d))
    if not dirs:
        return None, {}
    d = dirs[-1]
    out = {}
    for name in ("growth", "ops", "youtube", "metricool"):
        v = load(os.path.join(d, name + ".json"), None)
        if v is not None:
            out[name] = v
    return os.path.basename(d), out


def followers(snaps, now):
    """Latest follower counts and the change over the last 7 days of snapshots."""
    if not snaps:
        return {}
    def acct(s, net, field):
        return (s.get("account", {}).get(net) or {}).get(field)
    last_day, last = snaps[-1]
    cutoff = (now - dt.timedelta(days=7)).strftime("%Y-%m-%d")
    base = next((s for d, s in snaps if d >= cutoff), snaps[0][1])
    out = {}
    for net, field in (("instagram", "followers_count"), ("facebook", "followers_count")):
        a, b = acct(last, net, field), acct(base, net, field)
        if a is not None:
            out[net] = {"now": a, "change7d": (a - b) if b is not None else None, "asOf": last_day}
    return out


def signups_by_reel(growth):
    """utm_campaign reels_<slug> signups from the app digest (Facebook Reel links)."""
    out = {}
    for row in ((growth or {}).get("w30") or {}).get("byCampaign", []):
        src, _, camp = row["key"].partition("/")
        if camp.startswith("reels_"):
            out[camp[len("reels_"):]] = out.get(camp[len("reels_"):], 0) + int(row["count"])
    return out


def reel_scores(snap, formats, growth, now):
    """Per slug: settled posts, totals and points per post, from the newest snapshot."""
    per = {}
    rows = [dict(r, platform="instagram") for r in (snap or {}).get("instagram", []) if r.get("ours") and r.get("slug")]
    rows += [dict(r, platform="facebook") for r in (snap or {}).get("facebook", []) if r.get("slug")]
    for r in rows:
        t = parse_t(r.get("time"))
        settled = bool(t and (now - t).total_seconds() >= SETTLE_HOURS * 3600)
        s = per.setdefault(r["slug"], {"slug": r["slug"], "posts": 0, "settled": 0, "igSettled": 0, "points": 0.0,
                                         "views": 0, "likes": 0, "comments": 0, "shares": 0, "saved": 0, "follows": 0})
        s["posts"] += 1
        for k in ("likes", "comments", "shares", "saved", "follows"):
            s[k] += int(num(r.get(k)))
        s["views"] += int(reel_views(r))
        if settled:
            s["settled"] += 1
            s["igSettled"] += r["platform"] == "instagram"
            s["points"] += points(r)
    for slug, n in signups_by_reel(growth).items():
        s = per.setdefault(slug, {"slug": slug, "posts": 0, "settled": 0, "igSettled": 0, "points": 0.0, "views": 0, "likes": 0,
                                  "comments": 0, "shares": 0, "saved": 0, "follows": 0})
        s["signups"] = n
        s["points"] += SIGNUP_POINTS * n
    for s in per.values():
        s.setdefault("signups", 0)
        s["perPost"] = round(s["points"] / s["settled"], 2) if s["settled"] else None
        s.update(formats.get(s["slug"], {}))
    judged = [s["perPost"] for s in per.values() if s["perPost"] is not None]
    med = statistics.median(judged) if judged else None
    for s in per.values():
        s["ratio"] = round(s["perPost"] / med, 2) if (med and s["perPost"] is not None) else None
    return sorted(per.values(), key=lambda s: (-(s["perPost"] or -1), s["slug"])), med


def format_table(scores, key, med):
    groups = {}
    for s in scores:
        if s["perPost"] is None or not s.get(key):
            continue
        g = groups.setdefault(s[key], {"value": s[key], "posts": 0, "points": 0.0, "slugs": []})
        g["posts"] += s["settled"]
        g["points"] += s["points"]
        g["slugs"].append(s["slug"])
    out = []
    for g in groups.values():
        per_post = g["points"] / g["posts"] if g["posts"] else 0
        ratio = per_post / med if med else None
        verdict = "testing"
        if g["posts"] >= MIN_FORMAT_POSTS and ratio is not None:
            verdict = "winner" if ratio >= WIN_RATIO else "loser" if ratio <= LOSE_RATIO else "average"
        out.append({"value": g["value"], "posts": g["posts"], "perPost": round(per_post, 2),
                    "ratio": round(ratio, 2) if ratio is not None else None, "verdict": verdict, "slugs": g["slugs"]})
    return sorted(out, key=lambda g: -g["perPost"])


def actions(scores, library, med):
    """Boost the best settled slugs; retire clear losers (repeats only), within safety limits."""
    usable = [v for v in library.get("videos", []) if not v.get("hold")]
    boost, retire = {}, {}
    ranked = [s for s in scores if s["ratio"] is not None]
    for s in ranked[:BOOST_TOP]:
        if s["ratio"] >= WIN_RATIO or s.get("signups"):
            boost[s["slug"]] = int(min(60, round(20 * s["ratio"]))) + 25 * int(s.get("signups") or 0)
    room = max(0, len(usable) - MIN_ACTIVE)
    for s in sorted(ranked, key=lambda s: s["ratio"]):
        if len(retire) >= min(RETIRE_MAX, room):
            break
        if s["igSettled"] >= 2 and s["ratio"] < RETIRE_RATIO and not s.get("signups") and s["slug"] not in boost:
            retire[s["slug"]] = f"{s['perPost']} points per post, {s['ratio']}x the median over {s['settled']} posts"
    return boost, retire


TITLE_SHAPES = [
    ("pov-reaction", re.compile(r"^pov:\s*my reaction when", re.I)),
    ("pov", re.compile(r"^pov\b", re.I)),
    ("me-when", re.compile(r"^(me|when)\b", re.I)),
    ("how-to", re.compile(r"^how to\b", re.I)),
    ("hashtag-shorts", re.compile(r"#shorts", re.I)),
]


def title_shape(title):
    for name, rx in TITLE_SHAPES:
        if rx.search(title or ""):
            return name
    return "other"


def youtube_block(yt):
    if not yt:
        return None
    vids = yt.get("videos") or []
    shapes = {}
    for v in vids:
        k = (title_shape(v.get("title")), "ours" if v.get("ours") else "heycatch")
        g = shapes.setdefault(k, {"shape": k[0], "who": k[1], "videos": 0, "views": 0, "subs": 0})
        g["videos"] += 1
        g["views"] += int(num(v.get("views")))
        g["subs"] += int(num(v.get("subscribersGained")))
    table = sorted(({**g, "viewsPerVideo": round(g["views"] / g["videos"], 1)} for g in shapes.values()),
                   key=lambda g: -g["viewsPerVideo"])
    ours = [g for g in table if g["who"] == "ours" and g["videos"] >= 2]
    top = sorted(vids, key=lambda v: -num(v.get("views")))[:5]
    return {"channel": yt.get("channel"), "titleShapes": table,
            "bestTitleShape": ours[0]["shape"] if ours else None,
            "top": [{"title": v.get("title"), "views": v.get("views"), "subs": v.get("subscribersGained"),
                     "ours": bool(v.get("ours"))} for v in top]}


def demand_block(growth):
    w30 = (growth or {}).get("w30") or {}
    cats = w30.get("categories") or []
    gaps = [c for c in cats if (c.get("zero") or 0) > 0 or "needs_supply" in (c.get("flags") or [])]
    gaps.sort(key=lambda c: (-(int(c.get("zero") or 0) + 2 * int(c.get("saved") or 0)), int(c.get("live") or 0), c["id"]))
    return {
        "gaps": gaps[:8],
        "zeroResultTerms": (w30.get("searches") or {}).get("zeroResultTop", [])[:10],
        "zeroResultRate30d": (w30.get("searches") or {}).get("zeroResultRate"),
    }


def build_next(formats_tables, demand, formats):
    """What the Monday batch should brief Motion with: winning shapes x categories buyers want."""
    hooks = [g["value"] for g in formats_tables["hook"] if g["verdict"] == "winner"] or \
            [g["value"] for g in formats_tables["hook"][:1]]
    angles = [g["value"] for g in formats_tables["angle"] if g["verdict"] == "winner"] or \
             [g["value"] for g in formats_tables["angle"][:1]]
    covered = {}
    for f in formats.values():
        covered[f.get("category")] = covered.get(f.get("category"), 0) + 1
    gap_cats = [c["id"] for c in demand["gaps"]]
    # Categories buyers search for first, least covered by our videos first.
    cats = sorted(gap_cats, key=lambda c: (covered.get(c, 0), gap_cats.index(c)))[:3]
    retire_shapes = [g["value"] for t in ("hook", "angle") for g in formats_tables[t] if g["verdict"] == "loser"]
    return {"hooks": hooks, "angles": angles, "categories": cats, "stopMaking": retire_shapes}


def goals_block(follow, growth, yt, ops=None):
    w7 = (growth or {}).get("w7") or {}
    if not w7 and ops:
        # Before the first [GrowthDigest] line: the [OpsDigest] has the totals.
        u, l = ops.get("users") or {}, ops.get("listings") or {}
        w7 = {"signups": u.get("signups7d"), "signupsPrev": u.get("signupsPrev7d"), "byPlatform": u.get("signupPlatform7d") or [],
              "listingsPublished": l.get("published7d"), "listingsPublishedPrev": l.get("publishedPrev7d"), "activeListings": l.get("active")}
    platform = {r["key"]: r["count"] for r in w7.get("byPlatform", [])}
    return {
        "followers": {**follow, "youtube": (yt or {}).get("channel")},
        "signups7d": w7.get("signups"), "signupsPrev7d": w7.get("signupsPrev"),
        # Store installs are not readable from here; app signups by platform are the proxy.
        "appSignups7d": sum(v for k, v in platform.items() if k in ("ios", "android", "mobile")) if platform else None,
        "listingsPublished7d": w7.get("listingsPublished"), "listingsPublishedPrev7d": w7.get("listingsPublishedPrev"),
        "activeListings": w7.get("activeListings"),
        "signupsBySource7d": w7.get("bySource"), "heardFrom7d": w7.get("byHeardFrom"),
    }


def fmt_change(x):
    return "n/a" if x is None else (f"+{x}" if x > 0 else str(x))


def markdown(card):
    g, lines = card["goals"], []
    lines.append(f"# YardSwaps weekly scorecard ({card['week']})")
    lines.append("")
    lines.append(f"Generated {card['generatedAt']} by metrics/scorecard.py. Sources: " + ", ".join(
        f"{k} {'yes' if v else 'MISSING'}" for k, v in card["sources"].items()) + ".")
    lines.append("")
    lines.append("## Goals")
    f = g["followers"]
    for net in ("instagram", "facebook"):
        if net in f:
            lines.append(f"- {net.title()} followers: {f[net]['now']} ({fmt_change(f[net]['change7d'])} in 7 days)")
    if f.get("youtube"):
        lines.append(f"- YouTube: {json.dumps(f['youtube'])}")
    lines.append(f"- Signups 7d: {g['signups7d']} (prev {g['signupsPrev7d']}); from the app (iOS/Android): {g['appSignups7d']}")
    lines.append(f"- Listings published 7d: {g['listingsPublished7d']} (prev {g['listingsPublishedPrev7d']}); live now: {g['activeListings']}")
    if g.get("signupsBySource7d"):
        lines.append("- Signups by source 7d: " + ", ".join(f"{r['key']} {r['count']}" for r in g["signupsBySource7d"]))
    if g.get("heardFrom7d"):
        lines.append("- Heard about us 7d: " + ", ".join(f"{r['key']} {r['count']}" for r in g["heardFrom7d"]))
    lines.append("")
    lines.append("## Reels (our IG + FB posts, settled 48h+)")
    lines.append(f"Median points per post: {card['reels']['median']}. Points = follows x10, shares x4, saves x3, comments x3, likes x1, views/100, Reel-link signups x25.")
    lines.append("")
    lines.append("| Video | Posts | Views | Likes | Comments | Shares | Saves | Follows | Signups | Points/post | vs median |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in card["reels"]["slugs"]:
        lines.append(f"| {s['slug']} | {s['posts']} | {s['views']} | {s['likes']} | {s['comments']} | {s['shares']} | {s['saved']} | {s['follows']} | {s['signups']} | {s['perPost'] if s['perPost'] is not None else 'too new'} | {s['ratio'] if s['ratio'] is not None else '-'} |")
    lines.append("")
    for t, label in (("hook", "Opener shapes"), ("angle", "Topics"), ("category", "Categories")):
        lines.append(f"### {label}")
        for r in card["formats"][t]:
            lines.append(f"- {r['value']}: {r['perPost']} points/post over {r['posts']} posts ({r['verdict']})")
        lines.append("")
    yt = card.get("youtube")
    if yt:
        lines.append("## YouTube title shapes")
        for r in yt["titleShapes"]:
            lines.append(f"- {r['shape']} ({r['who']}): {r['viewsPerVideo']} views/video over {r['videos']} videos, {r['subs']} subs")
        lines.append(f"Best shape of ours: {yt['bestTitleShape']}")
        lines.append("")
    d = card["demand"]
    lines.append("## Buyer demand we can't serve yet (30 days)")
    lines.append(f"Zero-result search rate: {d['zeroResultRate30d']}")
    for c in d["gaps"]:
        lines.append(f"- {c['id']}: {c.get('zero', 0)} empty searches, {c.get('saved', 0)} saved searches, {c.get('live', 0)} live listings")
    if d["zeroResultTerms"]:
        lines.append("- Empty search terms: " + ", ".join(f"{t['query']} ({t['count']})" for t in d["zeroResultTerms"]))
    lines.append("")
    o = card.get("outreach")
    if o:
        lines.append("## Outreach (all sends so far)")
        for r in o.get("bySegment", []):
            lines.append(f"- {r['key']}: sent {r['sent']}, replies {r['replied']}, clicks {r['clicked']}, signups {r['converted']}, unsub {r['unsubscribed']} (reply rate {r['replyRate']})")
        lines.append(f"- By step: " + ", ".join(f"#{r['key']} {r['replied']}/{r['sent']}" for r in o.get("byStep", [])))
        lines.append(f"- Best segments: {', '.join(o.get('segmentRanking') or []) or 'not enough sends yet (20+ each)'}")
        lines.append("")
    a = card["actions"]
    lines.append("## What changed automatically")
    lines.append("- Reels boosted (posted first among repeats): " + (", ".join(f"{k} +{v}" for k, v in a["boost"].items()) or "none"))
    lines.append("- Reels retired (no more repeats; Motion rebuilds the idea): " + (", ".join(f"{k} ({v})" for k, v in a["retire"].items()) or "none"))
    b = a["buildNext"]
    lines.append(f"- Build next: opener {', '.join(b['hooks']) or 'n/a'}; topic {', '.join(b['angles']) or 'n/a'}; categories buyers want {', '.join(b['categories']) or 'n/a'}")
    if b["stopMaking"]:
        lines.append(f"- Stop making: {', '.join(b['stopMaking'])}")
    lines.append("")
    return "\n".join(lines)


def main():
    now = dt.datetime.now(dt.timezone.utc)
    library = load(os.path.join(ROOT, "reels", "library.json"), {"videos": []})
    formats = load(os.path.join(M, "formats.json"), {}).get("videos", {})
    snaps = snapshots()
    week, inp = latest_inputs(now)
    growth, yt = inp.get("growth"), inp.get("youtube")
    snap = snaps[-1][1] if snaps else None

    scores, med = reel_scores(snap, formats, growth, now)
    tables = {k: format_table(scores, k, med) for k in ("hook", "angle", "category")}
    demand = demand_block(growth)
    boost, retire = actions(scores, library, med)
    card = {
        "v": 1,
        "week": week or now.strftime("%Y-%m-%d"),
        "generatedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {"meta snapshot": bool(snap), "app growth digest": bool(growth), "app ops digest": bool(inp.get("ops")), "youtube": bool(yt),
                    "metricool": bool(inp.get("metricool"))},
        "goals": goals_block(followers(snaps, now), growth, yt, inp.get("ops")),
        "reels": {"median": med, "slugs": scores, "insights": (snap or {}).get("insights")},
        "formats": tables,
        "youtube": youtube_block(yt),
        "demand": demand,
        "outreach": (growth or {}).get("outreach"),
        "actions": {"boost": boost, "retire": retire, "buildNext": build_next(tables, demand, formats)},
    }
    with open(os.path.join(M, "scorecard.json"), "w", encoding="utf-8") as f:
        json.dump(card, f, indent=1)
        f.write("\n")
    with open(os.path.join(M, "SCORECARD.md"), "w", encoding="utf-8") as f:
        f.write(markdown(card))
    with open(os.path.join(M, "rank.json"), "w", encoding="utf-8") as f:
        json.dump({"generatedAt": card["generatedAt"], "boost": boost, "retire": retire}, f, indent=1)
        f.write("\n")

    g = card["goals"]
    hist = os.path.join(M, "history.csv")
    rows = list(csv.DictReader(open(hist, encoding="utf-8"))) if os.path.exists(hist) else []
    row = {"week": card["week"], "ig_followers": (g["followers"].get("instagram") or {}).get("now"),
           "fb_followers": (g["followers"].get("facebook") or {}).get("now"),
           "signups7d": g["signups7d"], "app_signups7d": g["appSignups7d"],
           "listings_published7d": g["listingsPublished7d"], "active_listings": g["activeListings"],
           "reel_median_points": med}
    rows = [r for r in rows if r["week"] != row["week"]] + [row]
    with open(hist, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        w.writeheader()
        w.writerows(rows)
    print(f"Scorecard {card['week']}: {len(scores)} slugs scored (median {med}); boost {boost or 'none'}; "
          f"retire {list(retire) or 'none'}; sources {card['sources']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
