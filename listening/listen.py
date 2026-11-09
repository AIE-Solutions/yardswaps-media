#!/usr/bin/env python3
"""Weekly listening list: public posts from people asking to buy or sell
used work equipment, with a draft reply for each (listening/README.md).

Reads the public feeds in sources.json (subreddit and Reddit search RSS,
trade-forum RSS), keeps posts from the last
LOOKBACK_DAYS that show buy or sell intent AND name equipment, and writes:

  listening/latest.json        rolling pool of kept posts (last LOOKBACK_DAYS)
  listening/LIST.md            the same as a reading list with draft replies

Standard library only. Nothing is posted anywhere: a person reads the list
and replies by hand, as the business, where the place's rules allow it.

MODE=probe (pull requests) prints what each source returned and writes
nothing.
"""
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "8"))
MODE = os.environ.get("MODE", "run")
UA = "YardSwapsListening/1.0 (weekly read of public feeds; +https://www.yardswaps.com)"
NOW = dt.datetime.now(dt.timezone.utc)
SINCE = NOW - dt.timedelta(days=LOOKBACK_DAYS)

# Intent. Titles count double: a "WTB" in a title is a stronger signal than
# the same words deep in a body.
BUY = re.compile(
    r"\b(wtb|want(?:ed)? to buy|in the market for|looking (?:to buy|for (?:a |an )?(?:used|cheap|second[- ]hand))|"
    r"anyone (?:selling|have (?:a|an) .{0,30}for sale)|where (?:can|do|should) (?:i|we|you) (?:buy|find|get) (?:a |an )?used|"
    r"need (?:a|an) used)", re.I)
SELL = re.compile(
    r"\b(where (?:can|do|should) (?:i|we) sell|where to sell|best (?:place|way|site|website) to sell|how (?:do (?:i|we) |to )sell|"
    r"selling (?:my|our|off)|need to sell|trying to sell|getting rid of|liquidat\w+|closing (?:the |my |our )?(?:shop|business|restaurant|doors)|"
    r"retiring and|wts\b|fs:|for sale:)", re.I)

# Classified-style title tags: "WTB lathe", "For sale: 20kw generator".
TITLE_BUY = re.compile(r"^\s*\[?(wtb|wanted|iso)\b", re.I)
TITLE_SELL = re.compile(r"(^\s*\[?(fs|wts|for sale)\b)|\bfor sale\b", re.I)

# Equipment words -> YardSwaps category (ids from packages/shared CATEGORIES).
CATS = [
    ("fleet", "Fleet Trucks", r"box truck|dump truck|service truck|bucket truck|flatbed|work truck|work van|f-?[345]50|cargo van"),
    ("trailers", "Trailers", r"trailer"),
    ("generators", "Generators", r"generator|genset"),
    ("pressure", "Pressure Washers", r"pressure washer|power washer|surface cleaner|soft ?wash"),
    ("vacuum", "Vacuum Trucks", r"vac(?:uum)? truck|hydro ?vac|vactor|septic truck"),
    ("hydro", "Hydro Jetting", r"jetter|hydro ?jet"),
    ("pumps", "Pumps & Motors", r"trash pump|water pump|transfer pump|electric motor"),
    ("inspection", "Pipe Inspection", r"sewer camera|pipe camera|inspection camera"),
    ("compressors", "Compressors", r"compressor"),
    ("welding", "Welding Equipment", r"welder|welding|plasma cutter|miller|lincoln electric|hypertherm"),
    ("machining", "Metalworking & CNC", r"\blathe\b|mill(?:ing machine)?\b|micrometer|measuring tools|bridgeport|\bcnc\b|haas|press brake|bandsaw|band saw"),
    ("automotive", "Auto Shop Equipment", r"car lift|2[- ]post lift|4[- ]post lift|tire changer|wheel balancer|alignment machine"),
    ("excavators", "Excavators & Loaders", r"excavator|backhoe|skid ?steer|bobcat|loader|dozer|mini ex|track loader"),
    ("paving", "Paving & Compaction", r"compactor|drum roller|road roller|plate tamper|paver"),
    ("forklifts", "Forklifts", r"forklift|fork lift|pallet jack|reach truck|telehandler"),
    ("aerial", "Aerial Lifts", r"scissor lift|boom lift|man ?lift|aerial lift"),
    ("cranes", "Cranes & Rigging", r"\bcrane\b|hoist|gantry"),
    ("concrete", "Concrete & Masonry", r"concrete mixer|cement mixer|power trowel|concrete saw|core drill"),
    ("drilling", "Drilling & Boring", r"directional drill|boring machine|auger rig|drill rig"),
    ("agriculture", "Farm & Ag", r"\btractor\b|baler|combine harvester|hay rake|brush hog|planter"),
    ("landscaping", "Landscaping & Turf", r"zero[- ]turn|mower|stump grinder|chipper|aerator|trencher"),
    ("restaurant", "Restaurant Equipment", r"restaurant equipment|commercial kitchen|food truck|prep table|dish ?machine"),
    ("refrigeration", "Commercial Refrigeration", r"walk[- ]in (?:cooler|freezer)|reach[- ]in|ice machine|commercial (?:fridge|refrigerator|freezer)"),
    ("cooking", "Cooking & Ovens", r"fryer|griddle|pizza oven|convection oven|combi oven|range hood"),
    ("warehouse", "Warehouse Storage", r"pallet rack|warehouse racking|shelving"),
    ("laundry", "Commercial Laundry", r"commercial (?:washer|dryer)|laundromat"),
    ("hvac", "Commercial HVAC", r"rooftop unit|\brtu\b|chiller|air handler"),
    ("tools", "Power & Hand Tools", r"table saw|tool chest|toolbox|power tools"),
]
CAT_RES = [(cid, name, re.compile(r"\b(?:" + pat + r")", re.I)) for cid, name, pat in CATS]

SELL_LINK = "https://www.yardswaps.com/sell-equipment?utm_source={src}&utm_medium=social&utm_campaign=listening_{cat}"
HOME_LINK = "https://www.yardswaps.com/?utm_source={src}&utm_medium=social&utm_campaign=listening_{cat}"


def fetch(url, accept="application/rss+xml, application/atom+xml, application/xml, text/xml, application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 2:
                raise
            wait = e.headers.get("Retry-After", "30")
            time.sleep(min(int(wait) if wait.isdigit() else 30, 90))


def clean(text, limit=600):
    text = re.sub(r"<[^>]+>", " ", html.unescape(text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d


def parse_feed(raw):
    """RSS 2.0 or Atom -> [{title, link, text, author, time}]."""
    root = ET.fromstring(raw)
    out = []
    atom = "{http://www.w3.org/2005/Atom}"
    dc = "{http://purl.org/dc/elements/1.1/}"
    for it in root.iter("item"):
        out.append({
            "title": clean(it.findtext("title"), 200),
            "link": (it.findtext("link") or "").strip(),
            "text": clean(it.findtext("description") or it.findtext("{http://purl.org/rss/1.0/modules/content/}encoded")),
            "author": clean(it.findtext(dc + "creator") or it.findtext("author"), 80),
            "time": parse_date(it.findtext("pubDate") or it.findtext(dc + "date")),
        })
    for en in root.iter(atom + "entry"):
        link = en.find(atom + "link")
        out.append({
            "title": clean(en.findtext(atom + "title"), 200),
            "link": link.get("href") if link is not None else "",
            "text": clean(en.findtext(atom + "content") or en.findtext(atom + "summary")),
            "author": clean(en.findtext(atom + "author/" + atom + "name"), 80),
            "time": parse_date(en.findtext(atom + "published") or en.findtext(atom + "updated")),
            "where": (en.find(atom + "category").get("term", "") if en.find(atom + "category") is not None else ""),
        })
    return out


def classify(post):
    title, text = post["title"], post["text"]
    both = title + " " + text
    buy = (2 if BUY.search(title) or TITLE_BUY.search(title) else 0) + (1 if BUY.search(text) else 0)
    sell = (2 if SELL.search(title) or TITLE_SELL.search(title) else 0) + (1 if SELL.search(text) else 0)
    if not buy and not sell:
        return None
    # Equipment named in the title wins over equipment mentioned in passing.
    cats = ([(cid, name) for cid, name, rx in CAT_RES if rx.search(title)]
            or [(cid, name) for cid, name, rx in CAT_RES if rx.search(text)])
    if not cats:
        return None
    # A forum or Reddit post needs the intent in its title, or the equipment
    # in its title: intent words deep in a long thread are mostly noise.
    if title and max(buy, sell) < 2 and not any(rx.search(title) for _, _, rx in CAT_RES):
        return None
    intent = "sell" if sell >= buy else "buy"
    # A buyer has to name the machine in the title: "Looking for a VHF set"
    # with "tractor" further down is not a tractor buyer (seen 11-09).
    if intent == "buy" and title and not any(rx.search(title) for _, _, rx in CAT_RES):
        return None
    return {"intent": intent, "category": cats[0][0], "category_name": cats[0][1],
            "score": max(buy, sell) + (1 if rx_in_title(cats[0][0], title) else 0)}


def rx_in_title(cid, title):
    for c, _, rx in CAT_RES:
        if c == cid:
            return bool(rx.search(title))
    return False


def drafts(item):
    """Two drafts as the business: no link (default) and with a tagged link
    for places whose rules allow it. Never promises buyers, views or sales."""
    src = "reddit" if item["platform"] == "Reddit" else "forum"
    if item["intent"] == "sell":
        base = ("For a used machine like this, the usual routes are Facebook Marketplace, Craigslist, a local dealer or an auction if it's big iron. "
                "We run YardSwaps, a free marketplace just for used work equipment, so that's one more place to list it at no cost "
                "(no fee, no cut, buyer picks up and pays you). Clear photos of the data plate and hours help on any site. "
                "What's the condition on it?")
        link = SELL_LINK.format(src=src, cat=item["category"])
    else:
        base = ("Worth checking local dealers, auctions and Marketplace for a used one. "
                "We run YardSwaps, a marketplace for used work equipment from local owners and shops; it's early, so there may not be one near you yet. "
                "What size and budget are you after?")
        link = HOME_LINK.format(src=src, cat=item["category"])
    return {"no_link": base, "with_link": base + "\n" + link}


def collect(sources):
    posts, report = [], []
    feeds = []
    # Reddit allows few anonymous requests a minute, so the trade subreddits
    # are searched together (one multireddit) once per phrase set.
    multi = "+".join(sources.get("reddit_subs", []))
    for search in sources.get("reddit_searches", []):
        base = f"https://www.reddit.com/r/{multi}/search.rss?" if multi else "https://www.reddit.com/search.rss?"
        u = base + urllib.parse.urlencode({"q": search["q"], "restrict_sr": "1" if multi else "0", "sort": "new", "t": "week", "limit": 100})
        feeds.append(("Reddit", search["name"], u, False))
    for f in sources.get("forums", []):
        feeds.append(("Forum", f["name"], f["url"], bool(f.get("links_ok"))))

    for platform, name, url, links_ok in feeds:
        try:
            items = parse_feed(fetch(url))
            recent = [p for p in items if p["time"] and p["time"] >= SINCE]
            report.append((name, "ok", len(items), len(recent)))
            for p in recent:
                where = p.pop("where", "")
                p.update(platform=platform, source=f"r/{where}" if platform == "Reddit" and where else name, links_ok=links_ok)
                posts.append(p)
        except Exception as e:  # one dead feed must not stop the run
            report.append((name, f"error: {type(e).__name__}: {str(e)[:80]}", 0, 0))
        time.sleep(8 if platform == "Reddit" else 2)

    return posts, report


def main():
    with open(os.path.join(HERE, "sources.json")) as f:
        sources = json.load(f)
    posts, report = collect(sources)

    # The forum feeds only hold the last day or two, so the job runs daily
    # and keeps a rolling pool of the last LOOKBACK_DAYS in latest.json.
    pool_path = os.path.join(HERE, "latest.json")
    if MODE != "probe" and os.path.exists(pool_path):
        try:
            with open(pool_path) as f:
                for old in json.load(f).get("posts", []):
                    old["time"] = parse_date(old.get("time"))
                    if old["time"] and old["time"] >= SINCE:
                        posts.append(old)
        except (OSError, ValueError):
            pass

    kept, seen = [], set()
    for p in posts:
        key = p["link"].split("?")[0].rstrip("/")
        if not key or key in seen:
            continue
        seen.add(key)
        if "intent" not in p:  # new this run; pooled posts keep their earlier classification
            c = classify(p)
            if not c:
                continue
            p.update(c)
            p["drafts"] = drafts(p)
            p["first_seen"] = NOW.isoformat()
        kept.append(p)
    kept.sort(key=lambda p: (p["intent"] != "sell", -p["score"], -(p["time"] or SINCE).timestamp()))

    print(f"## Listening run {NOW:%Y-%m-%d %H:%M} UTC (last {LOOKBACK_DAYS} days)\n")
    print("| Source | Status | Items | In window |\n|---|---|---|---|")
    for name, status, n, r in report:
        print(f"| {name} | {status} | {n} | {r} |")
    print(f"\nKept {len(kept)} posts: {sum(p['intent'] == 'sell' for p in kept)} selling, "
          f"{sum(p['intent'] == 'buy' for p in kept)} buying.\n")
    for p in kept[:15]:
        print(f"- [{p['intent']}] {p['category_name']} · {p['source']} · {(p['title'] or p['text'])[:90]}")

    if MODE == "probe":
        return 0

    out = [{**p, "time": p["time"].isoformat() if p["time"] else None} for p in kept]
    with open(pool_path, "w") as f:
        json.dump({"generated_at": NOW.isoformat(), "lookback_days": LOOKBACK_DAYS,
                   "sources": [{"name": n, "status": s, "items": i, "in_window": r} for n, s, i, r in report],
                   "posts": out}, f, indent=1)

    lines = [f"# Listening list, updated {NOW:%a %b %d, %Y}", "",
             "People asking to buy or sell used work equipment in public places, last "
             f"{LOOKBACK_DAYS} days. Nothing here was posted. Reply by hand, as the business, "
             "only where the place's rules allow it; use the link version only where links are allowed.", ""]
    if not kept:
        lines.append("No matching posts this week.")
    for i, p in enumerate(kept, 1):
        when = p["time"].strftime("%a %b %d") if p["time"] else "date unknown"
        lines += [f"## {i}. {'Selling' if p['intent'] == 'sell' else 'Buying'}: {p['category_name']} ({p['source']}, {when})", "",
                  f"> {(p['title'] + ' - ' if p['title'] else '') + p['text'][:400]}", "",
                  f"Open: {p['link']}", "", "Draft reply:", "", "```", p["drafts"]["no_link"], "```", ""]
        if p["links_ok"]:
            lines += ["Link version (links allowed here):", "", "```", p["drafts"]["with_link"], "```", ""]
    with open(os.path.join(HERE, "LIST.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
