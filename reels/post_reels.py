#!/usr/bin/env python3
"""Post one YardSwaps Reel to Instagram and Facebook per run.

Runs from .github/workflows/reels.yml; posts at most once per Central-time
slot (SLOTS_CT, ten a day since Nov 23). Standard library only.

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
  THREADS_TOKEN    long-lived Threads user token for @yardswaps (secret; 60
                   days, refreshed by the runs). Missing = Threads is skipped
                   with a notice; Instagram and Facebook still post.
  PLATFORMS        default "instagram,facebook,instagram_story,facebook_story,threads"
  SLUG             force one video (manual runs)
  DRY_RUN          "1" = pick and print captions, post nothing
  CHECK_ONLY       "1" = only say whether a slot is open (due=0/1 and at=<time>
                   to GITHUB_OUTPUT)
  SLOT_AT          the gate job's time (reels.yml passes it): the posting job
                   judges the slot by it, so a slow video checkout can't push
                   a run that was due out of its window
  LIST_FREE        "1" = make this run's Reel the "list it free" post (manual
                   or dry runs; scheduled runs decide by LIST_FREE_FROM_CT)
  PROMO            a promos.json id = make this run's Reel that promotion post
                   (manual or dry runs; scheduled runs decide by slot_from_ct)
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

# Nov 21 (Alan: "We keep reusing the same machines for our social media posts"): every pick also
# obeys the shared machine rotation in rotation/rotation.py, which reads every channel's log.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rotation"))
try:
    import rotation as rot  # noqa: E402
except ImportError:  # a sparse checkout (caption fixes, profiles) that never picks a clip
    rot = None

# Account health (studio/health.py, 2026-11-25, our version of HeyCatch's): a 0-10 score per platform
# that can pause a platform for 48 h when it slips, and (policy "caps") hold it to its level's daily cap.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "studio"))
try:
    import health as account_health  # noqa: E402
except ImportError:
    account_health = None


def health_blocked(platform, posted):
    """Why account health stops another post to this platform today, or None. Never raises."""
    if account_health is None:
        return None
    try:
        c = account_health.cap(platform)
        if c is None:
            return None
        n = account_health.posted_today(posted, platform)
        if n >= c:
            return f"account health: paused (studio/HEALTH.md)" if c == 0 else f"account health cap {c} a day reached ({n} today)"
    except Exception as e:  # never stop posting over a broken check
        print(f"  account health check failed: {e}")
    return None

GRAPH = "https://graph.facebook.com/v23.0"
RUPLOAD_IG = "https://rupload.facebook.com/ig-api-upload/v23.0"
THREADS = "https://graph.threads.net/v1.0"
THREADS_MAX = 500          # characters in a Threads post
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
# scheduled run posts once per slot, only between those two times. No slot
# starts inside the 90 minutes after HeyCatch (about :33 past 4 am, 12 pm and
# 8 pm Central, and the extra Instagram/Facebook posts it puts in those same
# slots) or after the 2:15 pm Just listed post, because the script skips a
# platform when something that isn't ours went up there in the last 90 minutes:
#   6:10 am   until 6:55 am   (seventh slot, added Nov 13 when the library reached
#                              71 active; HeyCatch 4:33 am is 92+ min before the early edge)
#   7:00 am   until 8:00 am   (HeyCatch 4:33 am is 2.5 h before; the seller post since Nov 26)
#   8:30 am   until 9:30 am   (fifth slot, added Nov 8 when the library reached 50)
#   10:00 am  until 11:00 am
#   11:20 am  until 11:50 am  (moved here Nov 26 from 12:40 am; 43+ min before HeyCatch 12:33 pm)
#   3:55 pm   until 4:45 pm   (eighth slot, added Nov 18 when the library reached
#                              89 active; Just listed 2:15 pm is 95+ min before the early edge)
#   5:15 pm   until 6:00 pm   (was 4:30 pm until Nov 18; moved so it posts 55+ min
#                              after the 3:55 pm slot)
#   6:30 pm   until 7:00 pm
#   7:30 pm   until 8:00 pm   (moved here Nov 26 from 11:40 pm; 33+ min before HeyCatch 8:33 pm)
#   10:10 pm  until 11:00 pm  (sixth slot, added Nov 11 when the library reached
#                              64 active; HeyCatch 8:33 pm is 92+ min before the early edge)
# Nov 26 (Alan: "based on research is their optimal times to post"): the 11:40 pm and 12:40 am
# slots sat in the midnight to 4 am window that the 2026 Sprout Social, Buffer and Hootsuite
# studies all name as the worst, so they moved into late morning (our Facebook followers peak
# 10 am to noon, Metricool) and early evening. Still ten a day. A two-week test: compare the
# moved slots' Reels with the kept ones in metrics/ before keeping or undoing it.
# A run GitHub starts too late for its slot does nothing; the next slot's
# runs pick up. library.json "slots" (["07:00-09:30", ...]) overrides this.
CENTRAL = ZoneInfo("America/Chicago")
SLOTS_CT = [((6, 10), (6, 55)), ((7, 0), (8, 0)), ((8, 30), (9, 30)), ((10, 0), (11, 0)), ((11, 20), (11, 50)), ((15, 55), (16, 45)), ((17, 15), (18, 0)), ((18, 30), (19, 0)), ((19, 30), (20, 0)), ((22, 10), (23, 0))]
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


# Instagram captions don't click and bio taps are rare (about 5 humans a
# week across every platform, Nov 2-9 Railway logs), but a comment with the
# keyword "list" fires the live Meta comment-to-DM automation, which sends a
# tappable /c link to the sell page (DM-AUTOREPLIES.md). Lowercase on purpose:
# the automation lists both cases, lowercase is the safe match.
IG_COMMENT_CTA = ('Comment "list" and we\'ll message you the free listing link, '
                  "or tap yardswaps.com/i in our bio.")
# A storefront clip speaks to dealers, who never hear "free listing"
# (MESSAGING.md at the repo root): its close sends them to the storefront page.
STOREFRONT_IG_CTA = "To open your storefront, type yardswaps.com/s in your browser."
STOREFRONT_TYPED_LINK = "Open your storefront: yardswaps.com/s"


# A Spanish clip ("lang": "es" in library.json) gets its follow line and
# link line in Spanish, worded like the Spanish YouTube descriptions
# (WEEKLY-BATCH.md), and keeps its own Spanish hashtags (set ig_tags_fixed).
FOLLOW_ES = "Síguenos para ver uno nuevo cada día."


def is_spanish(v):
    return (v.get("lang") or "en").lower() == "es"


def ig_caption(v, turn=0):
    if is_spanish(v):
        return (f"{v['body']}\n\n{FOLLOW_ES} Publica gratis: yardswaps.com/i (link en el perfil)."
                f"\n\n{ig_tags(v, turn)}\n\n{v['question']}")
    cta = STOREFRONT_IG_CTA if is_dealer_clip(v) else IG_COMMENT_CTA
    return (f"{v['body']}\n\n{FOLLOW_IG} {cta}"
            f"\n\n{ig_tags(v, turn)}\n\n{v['question']}")


# Category ids with a seller page at yardswaps.com/sell-equipment/<id>
# (CATEGORIES in the app's packages/shared/src/listings.ts, minus "all").
SELLER_PAGES = {
    "fleet", "trailers", "generators", "pressure", "vacuum", "pumps", "hydro",
    "inspection", "compressors", "welding", "machining", "automotive", "tools",
    "excavators", "paving", "forklifts", "aerial", "cranes", "concrete",
    "drilling", "electrical", "environmental", "safety", "agriculture",
    "landscaping", "restaurant", "refrigeration", "cooking", "warehouse",
    "retail", "office", "laundry", "hvac", "parts",
}


def seller_path(v):
    """/sell-equipment/<category> when the clip names one category, else /sell-equipment."""
    cat = (v.get("category") or "").strip().lower()
    return f"/sell-equipment/{cat}" if cat in SELLER_PAGES else "/sell-equipment"


def is_dealer_clip(v):
    """A storefront clip ("audience": "dealer" in library.json) speaks to dealers."""
    return (v.get("audience") or "").strip().lower() == "dealer"


def fb_caption(v):
    # Facebook captions click, so the link carries a per-Reel tag (UTM-LINKS.md).
    # A clip about one category ("category" in library.json) links that
    # category's seller page; a storefront clip ("audience": "dealer") links
    # the storefront page (/dealers), where the storefront trial starts.
    path = "/dealers" if is_dealer_clip(v) else seller_path(v)
    cta = "Open your storefront:" if is_dealer_clip(v) else "Get the free app and list it free:"
    link = (f"https://www.yardswaps.com{path}?utm_source=facebook"
            f"&utm_medium=social&utm_campaign=reels_{v['slug']}")
    if is_spanish(v):
        return (f"{v['body']}\n\n{FOLLOW_ES} Publica gratis: {link}"
                f"\n\n{fb_tags(v)}\n\n{v['question']}")
    return (f"{v['body']}\n\n{FOLLOW_FB} {cta} {link}"
            f"\n\n{fb_tags(v)}\n\n{v['question']}")


def threads_caption(v):
    # Threads allows one topic tag (sent separately) and 500 characters, so
    # no hashtags here. The typed short link /h is tagged (UTM-LINKS.md).
    if is_spanish(v):
        app = "Descarga la app gratis: yardswaps.com/h"
    elif is_dealer_clip(v):
        app = STOREFRONT_TYPED_LINK
    else:
        app = "Get the free YardSwaps app: yardswaps.com/h"
    tail = f"\n\n{app}\n\n{v['question']}"
    body = v["body"]
    while len(body) + len(tail) > THREADS_MAX and ". " in body:
        body = body[:body.rstrip(".").rfind(". ") + 1]   # drop the last sentence
    return (body + tail)[:THREADS_MAX]


def threads_topic(v):
    """The video's first machine or trade tag, without the #, as the topic."""
    tags = machine_tags(v, 1)
    return tags[0].lstrip("#")[:50] if tags else "UsedEquipment"


# ---------- daily "List it free" Reel ----------
# Alan, Nov 15: a daily "list your equipment free" post on every social
# ("All socials yes"). One of the ten daily Reels carries it, so volume
# does not go up: the first Reel of the Central day at or after
# LIST_FREE_FROM_CT (the 7:00 am slot since Nov 26, when our Instagram followers
# are most active, 6 to 9 am in Metricool; it was 5:15 pm. If that run fails the
# next slot takes over) gets a "LIST IT FREE" caption and a clip picked for it:
#   - a real item first (the clip names one category; no dealer clips),
#   - a category the list-it-free posts have not shown in LIST_FREE_CATEGORY_DAYS
#     days, so the equipment rotates across the categories,
#   - the usual 10-day no-repeat rule per platform.
# The morning 9:27 am "LIST IT FREE" Instagram Story (stories/) is separate
# and stays as it is. Copy is seller-first: free to list, no cut of the sale,
# every 4 listings earns a free 7-day boost credit (up to 5; the seller spends
# it, so never say it boosts automatically). Never promise views or sales.
LIST_FREE_FROM_CT = (7, 0)
LIST_FREE_CATEGORY_DAYS = 7
LIST_FREE_HEAD = "LIST IT FREE"
# Rotate so no two days in a row read word for word the same.
LIST_FREE_LINES = [
    "Listing on YardSwaps is free and we take nothing from the sale. "
    "Every 4 listings you post earns a free 7-day boost, up to 5.",
    "It costs $0 to list and nothing comes out of the sale price. "
    "Post 4 listings and you earn a free 7-day boost. Bank up to 5.",
    "No listing fee. No cut when it sells. Buyers pick it up from you. "
    "Every fourth listing earns a free 7-day boost, up to 5 saved.",
    "Free to post, free to sell, and the whole price stays with you. "
    "Every 4 listings earns a free 7-day boost credit, up to 5.",
]
_LIST_FREE_DROP = ("free to list", "list it free:", "no listing fee",
                   "post 4 listings within")


def list_free_ok(v):
    """A clip that can carry the daily list-it-free post."""
    if v.get("list_free") is False or is_spanish(v):  # opt-out, e.g. invite-a-seller; English copy only
        return False
    cat = (v.get("category") or "").strip().lower()
    return cat in SELLER_PAGES and not is_dealer_clip(v)


def list_free_due(posted, platform, t=None, from_ct=None):
    """True when this run's post on `platform` should be today's list-it-free post."""
    t = t or now()
    local = t.astimezone(CENTRAL)
    from_ct = from_ct or LIST_FREE_FROM_CT
    start = local.replace(hour=from_ct[0], minute=from_ct[1],
                          second=0, microsecond=0) - dt.timedelta(minutes=SLOT_EARLY_MINUTES)
    if local < start:
        return False
    day = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return not any(p["platform"] == platform and p.get("status") == "posted" and p.get("list_free")
                   and parse_time(p["time"]) >= day for p in posted)


def list_free_pick(videos, posted, platform, scores=None):
    """pick() over list-it-free clips, skipping categories this platform's
    list-it-free posts showed in the last LIST_FREE_CATEGORY_DAYS days."""
    by_slug = {v["slug"]: v for v in videos}
    since = now() - dt.timedelta(days=LIST_FREE_CATEGORY_DAYS)
    recent = {(by_slug.get(p["slug"]) or {}).get("category")
              for p in posted
              if p["platform"] == platform and p.get("list_free")
              and p.get("status") == "posted" and parse_time(p["time"]) >= since}
    ok = [v for v in videos if list_free_ok(v)]
    fresh_cat = [v for v in ok if v.get("category") not in recent]
    # Sellers first (Alan, 2026-11-26: "our mission is for sellers to be posting equipment"): a seller
    # Reel ("cut": "seller", its whole first frame is the ask to list) carries this post when one is
    # free to run; a listing Reel only when none is.
    seller = [v for v in ok if v.get("cut") == "seller"]
    for pool in ([v for v in seller if v in fresh_cat], seller):
        if pool:
            video, repeat = pick(pool, posted, platform, None, scores)
            if video and not repeat:
                return video, repeat
    for pool in (fresh_cat, ok):
        video, repeat = pick(pool, posted, platform, None, scores)
        if video:
            return video, repeat
    return None, False


def list_free_body(v):
    """The clip's own text minus its closing free-listing line."""
    paras = [p for p in v["body"].split("\n\n")
             if not p.strip().lower().startswith(_LIST_FREE_DROP)]
    return "\n\n".join(paras)


def list_free_line(turn):
    return LIST_FREE_LINES[turn % len(LIST_FREE_LINES)]


def list_free_ig_caption(v, turn=0):
    return (f"{LIST_FREE_HEAD}\n\n{list_free_body(v)}\n\n{list_free_line(turn)}"
            f"\n\n{FOLLOW_IG} {IG_COMMENT_CTA}\n\n{ig_tags(v, turn)}\n\n{v['question']}")


def list_free_fb_caption(v, turn=0):
    # Tagged per post (UTM-LINKS.md): campaign listfree_<slug>, 40 characters max.
    campaign = f"listfree_{v['slug']}"[:40]
    link = (f"https://www.yardswaps.com{seller_path(v)}?utm_source=facebook"
            f"&utm_medium=social&utm_campaign={campaign}")
    return (f"{LIST_FREE_HEAD}\n\n{list_free_body(v)}\n\n{list_free_line(turn)}"
            f"\n\n{FOLLOW_FB} Get the free app and list yours: {link}"
            f"\n\n{fb_tags(v)}\n\n{v['question']}")


def list_free_threads_caption(v, turn=0):
    head = f"{LIST_FREE_HEAD}\n\n"
    tail = f"\n\n{list_free_line(turn)}\n\nGet the free YardSwaps app: yardswaps.com/h\n\n{v['question']}"
    body = list_free_body(v)
    while len(head) + len(body) + len(tail) > THREADS_MAX and ". " in body:
        body = body[:body.rstrip(".").rfind(". ") + 1]
    return (head + body + tail)[:THREADS_MAX]


# ---------- daily promotion post ----------
# Alan, Nov 15: "Let's add the promotions to the posting on socials". The
# promotions live in reels/promos.json (founding dealer price, Share my page
# and the invite reward). One Reel a day per platform carries one: the first
# run of the Central day at or after promos.json "slot_from_ct" (10:00 am; if
# that run fails a later slot takes over, after the list-it-free post
# when both are due). The active promotions take turns by day, so volume does
# not go up. A promotion only posts between its start and end dates and on its
# own "platforms". The caption opens with the promotion's head, keeps the
# clip's text, adds the promotion's line and ends on the clip's question.
PROMOS = os.path.join(ROOT, "reels", "promos.json")


def promos_config():
    return load(PROMOS, {"promos": []})


def active_promos(platform, t=None, cfg=None):
    """The promotions running today on `platform`, in file order."""
    cfg = cfg if cfg is not None else promos_config()
    day = (t or now()).astimezone(CENTRAL).date().isoformat()
    out = []
    for pr in cfg.get("promos", []):
        if platform not in (pr.get("platforms") or []):
            continue
        if pr.get("start") and day < pr["start"]:
            continue
        if pr.get("end") and day >= pr["end"]:
            continue
        out.append(pr)
    return out


def promo_groups(platform, t=None, cfg=None):
    """[(from_ct, promos)] for today on `platform`. With "daily_audience" set in promos.json (Alan,
    2026-11-26: "Storefronts are also very important and need to keep pushing"), that audience's
    promotions post every day from "slot_from_ct", taking turns by day among themselves, and the other
    promotions take turns in a second post from "second_slot_from_ct". A platform with only one of the
    two kinds keeps its single daily promotion post at "slot_from_ct"."""
    cfg = cfg if cfg is not None else promos_config()
    live = active_promos(platform, t, cfg)
    if not live:
        return []
    first = tuple(cfg.get("slot_from_ct") or (10, 0))
    aud = cfg.get("daily_audience")
    lead = [pr for pr in live if aud and pr.get("audience") == aud]
    rest = [pr for pr in live if pr not in lead]
    if not lead or not rest:
        return [(first, live)]
    return [(first, lead), (tuple(cfg.get("second_slot_from_ct") or (17, 15)), rest)]


def promo_now(posted, platform, t=None, cfg=None):
    """The promotion this run's post on `platform` should carry, or None."""
    cfg = cfg if cfg is not None else promos_config()
    t = t or now()
    local = t.astimezone(CENTRAL)
    day = local.replace(hour=0, minute=0, second=0, microsecond=0)
    done = {p.get("promo") for p in posted if p["platform"] == platform and p.get("status") == "posted"
            and p.get("promo") and parse_time(p["time"]) >= day}
    for from_ct, group in promo_groups(platform, t, cfg):
        start = local.replace(hour=from_ct[0], minute=from_ct[1],
                              second=0, microsecond=0) - dt.timedelta(minutes=SLOT_EARLY_MINUTES)
        if local < start or done & {pr["id"] for pr in group}:
            continue
        return group[local.date().toordinal() % len(group)]
    return None


def promo_of_day(platform, t=None, cfg=None):
    """Today's first promotion on `platform` (each group takes turns by day), or None."""
    groups = promo_groups(platform, t, cfg)
    if not groups:
        return None
    group = groups[0][1]
    return group[(t or now()).astimezone(CENTRAL).date().toordinal() % len(group)]


def promo_due(posted, platform, t=None, cfg=None):
    """True when this run's post on `platform` should be a promotion post."""
    return promo_now(posted, platform, t, cfg) is not None


def promo_pool(videos, promo):
    """Clips that can carry `promo`: storefront clips for a dealer promotion,
    real-item seller clips (invite-a-seller included) for a seller one."""
    videos = [v for v in videos if not is_spanish(v)]   # promotion lines are English
    if promo.get("audience") == "dealer":
        return [v for v in videos if is_dealer_clip(v)]
    return [v for v in videos if not is_dealer_clip(v)
            and (v.get("category") or "").strip().lower() in SELLER_PAGES]


def promo_pick(videos, posted, platform, promo, scores=None):
    """pick() over the promotion's clips (a storefront clip may repeat after
    the usual 10 days); a dealer promotion with no storefront clip due falls
    back to a real-item seller clip."""
    pools = [promo_pool(videos, promo)]
    if promo.get("audience") == "dealer":
        pools.append(promo_pool(videos, {"audience": "seller"}))
    for pool in pools:
        video, repeat = pick(pool, posted, platform, None, scores)
        if video:
            return video, repeat
    return None, False


def promo_lines(promo):
    if promo.get("reward_live") and promo.get("lines_reward"):
        return promo["lines_reward"]
    return promo.get("lines") or [""]


def promo_line(promo, turn=0):
    lines = promo_lines(promo)
    return lines[turn % len(lines)]


def promo_turn(posted, platform, promo):
    return sum(1 for p in posted if p["platform"] == platform and p.get("promo") == promo["id"]
               and p.get("status") == "posted")


def promo_body(v, promo):
    """The clip's text minus its free-listing closer and any sentence the
    promotion restates (the dealer clips' "$49 a month")."""
    drop = [d.lower() for d in promo.get("drop_sentences_with") or []]
    out = []
    for para in list_free_body(v).split("\n\n"):
        if drop:
            sents = [x for x in para.replace(". ", ".\n").split("\n")
                     if not any(d in x.lower() for d in drop)]
            para = " ".join(sents).strip()
        if para:
            out.append(para)
    return "\n\n".join(out)


def promo_ig_caption(v, promo, turn=0):
    cta = promo.get("ig_cta") or IG_COMMENT_CTA
    return (f"{promo['head']}\n\n{promo_body(v, promo)}\n\n{promo_line(promo, turn)}"
            f"\n\n{FOLLOW_IG} {cta}\n\n{ig_tags(v, turn)}\n\n{v['question']}")


def promo_fb_caption(v, promo, turn=0):
    # Tagged per post (UTM-LINKS.md): campaign promo_<id>_<slug>, 40 characters max.
    campaign = f"promo_{promo['id']}_{v['slug']}"[:40]
    path = promo.get("link_path") or seller_path(v)
    extra = f"&{promo['link_query']}" if promo.get("link_query") else ""
    link = (f"https://www.yardswaps.com{path}?utm_source=facebook"
            f"&utm_medium=social&utm_campaign={campaign}{extra}")
    cta = ("Open your storefront:" if promo.get("audience") == "dealer"
           else "Get the free app and list it free:")
    return (f"{promo['head']}\n\n{promo_body(v, promo)}\n\n{promo_line(promo, turn)}"
            f"\n\n{FOLLOW_FB} {cta} {link}\n\n{fb_tags(v)}\n\n{v['question']}")


def promo_threads_caption(v, promo, turn=0):
    head = f"{promo['head']}\n\n"
    link = promo.get("typed_link") or "yardswaps.com/h"
    tail = f"\n\n{promo_line(promo, turn)}\n\n{link}\n\n{v['question']}"
    body = promo_body(v, promo)
    while len(head) + len(body) + len(tail) > THREADS_MAX and ". " in body:
        body = body[:body.rstrip(".").rfind(". ") + 1]
    if len(head) + len(body) + len(tail) > THREADS_MAX:
        body = ""
    return (head + body + tail).replace("\n\n\n\n", "\n\n")[:THREADS_MAX]


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


def with_endcard(videos):
    """Only clips that end on the YardSwaps end card post anywhere (Alan, 2026-11-25). The mark comes
    from brand/endcard/endcard.py fix (run after every listings build), which adds the card where it's
    missing; a clip without the mark waits for that run."""
    ok = [v for v in videos if v.get("endcard")]
    left = [v["slug"] for v in videos if not v.get("endcard") and not v.get("hold")]
    if left:
        print(f"::notice::{len(left)} clip(s) wait for the end card check: {', '.join(left[:8])}")
    return ok


# Alan, 2026-11-26: "For the reels the items in the pictures need to improve and be real, the rig one looks
# terrible." Only a clip whose item is a real YardSwaps listing photo posts: "real": true (listing Reels, real-
# listing Motion cuts) or "picture": "real" (a Motion cut whose opener is a listing photo). A clip with no
# "picture" key is treated as not real, so a new stock or generated picture can never slip into the rotation;
# "picture": "stock" names the Canva/Pexels/Unsplash/Commons/generated ones. reels/README.md "Real items only".
REAL_PICTURES = ("real",)


def real_picture(v, allow=REAL_PICTURES):
    return v.get("real") is True or v.get("picture") in allow


def with_real_pictures(videos, allow=REAL_PICTURES):
    """Only clips that show a real item from a YardSwaps listing post (see REAL_PICTURES)."""
    ok = [v for v in videos if real_picture(v, allow)]
    left = len([v for v in videos if not v.get("hold") and not real_picture(v, allow)])
    if left:
        print(f"::notice::{left} clip(s) skipped: the picture is not a real YardSwaps listing item")
    return ok


# Alan, 2026-11-26: "Not paused but start replacing them and add them to Line up" and "Even swap the ones
# that got sent out with new and improved nice ones". The ads thread re-renders each listing Reel in the new
# white and blue look in place (same slug, "look": "k2", file ending -k2.mp4). From then on:
#   - only posts in the same look count for a clip's no-repeat history, so a k2 clip whose old-look version
#     already went out posts again as a normal Reel (not a Trial Reel);
#   - those swaps go first, then any other k2 clip; an old-look clip posts only when no k2 clip may;
#   - once a k2 Reel is live on Instagram or Facebook, takedown() removes that platform's old-look Reels of
#     the same clip, plus one stock (then one held, badly cropped) Reel: Alan picked "One down per new Reel up".
NEW_LOOK = "k2"
WALK_FROM_CT = (8, 30)     # the day's walkthrough posts in the first regular slot from here (Central)
WALK_ITEM_HOURS = 48       # a live-app walkthrough waits this long after its listing was last shown


def is_new_look(v):
    return (v or {}).get("look") == NEW_LOOK


def same_look(p, v):
    """Does this log row count toward clip v's no-repeat history? Rows only count within one look."""
    return (p.get("look") == NEW_LOOK) == is_new_look(v)


def history(videos, posted, platform):
    """slug -> last time this clip, in its current look, went out on the platform."""
    looks = {v["slug"]: v for v in videos}
    last = {}
    for p in posted:
        if p["platform"] != platform or p.get("status") != "posted":
            continue
        # Only where the old post can come down (TAKEDOWN_PLATFORMS) does a new look count as a new clip;
        # on TikTok and YouTube it would just post the same machine twice.
        if platform in TAKEDOWN_PLATFORMS and not same_look(p, looks.get(p["slug"])):
            continue
        t = parse_time(p["time"])
        last[p["slug"]] = max(last.get(p["slug"], t), t)
    return last


def swap_due(v, posted, platform):
    """A new-look clip whose old-look Reel is still up on this platform and has no new-look post yet."""
    if not is_new_look(v):
        return False
    rows = [p for p in posted if p["platform"] == platform and p["slug"] == v["slug"] and p.get("status") == "posted"]
    return any(not p.get("removed") and p.get("look") != NEW_LOOK for p in rows) and \
        not any(p.get("look") == NEW_LOOK for p in rows)


def new_look_first(pool):
    """Only the new-look clips while any is available, else the pool unchanged."""
    k2 = [v for v in pool if is_new_look(v)]
    return k2 or pool


def pick(videos, posted, platform, force=None, scores=None):
    last = history(videos, posted, platform)
    if force:
        return next((v for v in videos if v["slug"] == force), None), force in last
    cutoff = now() - dt.timedelta(days=MIN_GAP_DAYS)
    # "hold": true keeps a video out of the queue (for example while its cut
    # is being fixed) without losing its place or history.
    # "platforms": [...] limits a clip to those posters (a Spanish cut that
    # TikTok and the promotions skip); "not_before" (ISO time) keeps it out
    # of the queue until then, e.g. to space it from the same clip in English.
    # Nov 16: a Short cut from a real new listing ("listing_id" on the entry) waits a day when the Just-listed
    # card of the same listing went out today, so one new item is not posted twice the same day.
    today = now().strftime("%Y-%m-%d")
    listed_today = {p["listing_id"] for p in load(os.path.join(ROOT, "listings", "posted.json"), [])
                    if p.get("status") == "posted" and str(p.get("time", "")).startswith(today)}
    # A seller who switched off "Feature my listings in YardSwaps social posts" (just_listed.py marks their
    # queue entries opted_out) never gets a real-listing Short posted again.
    opted_out = {q["listing_id"] for q in load(os.path.join(ROOT, "listings", "queue.json"), []) if q.get("opted_out")}
    usable = [v for v in videos if not v.get("hold") and os.path.exists(os.path.join(ROOT, v["file"]))
              and v.get("listing_id") not in listed_today
              and v.get("listing_id") not in opted_out
              and platform in (v.get("platforms") or [platform])
              and (not v.get("not_before") or parse_time(v["not_before"]) <= now())]
    # Machine rotation (rotation/README.md): first only clips whose machine no channel has shown in
    # 14 days (the same clip may still cross-post inside its 36-hour run); if none, the machine shown
    # longest ago but never one from the last 7 days; past that the slot is skipped, not repeated.
    if rot is None:
        raise SystemExit("rotation/rotation.py is missing from this checkout; add it before picking a clip")
    hist = rot.uses()   # always the whole library, so a promo or list-it-free pool maps machines right
    # One walkthrough a day per platform, ahead of the swaps (Alan, 2026-11-26: "These are critical to our
    # promotion I really liked them"), in the first regular slot from WALK_FROM_CT so it never lands on a
    # night slot. The live-app set ("walkthrough": "live"; Alan the same day: "a live motion video of our
    # application in action", "Yup perfect") goes first; an earlier walkthrough ("earlier_look_ok") only on
    # a day no live-app one may run. A live-app clip is about the app, so its machine key is its own slug,
    # and "item_machine" names the listing in its opener: it waits while that listing was shown anywhere in
    # the last WALK_ITEM_HOURS, and the one whose listing was shown longest ago goes first. Same 10-day
    # no-repeat rule as everything else.
    local = now().astimezone(CENTRAL)
    walk_from = local.replace(hour=WALK_FROM_CT[0], minute=WALK_FROM_CT[1], second=0,
                              microsecond=0) - dt.timedelta(minutes=SLOT_EARLY_MINUTES)
    if platform in ("instagram", "facebook") and local >= walk_from:
        live = {v["slug"] for v in videos if v.get("walkthrough") == "live"}
        walk = live | {v["slug"] for v in videos if v.get("earlier_look_ok")}
        day = local.replace(hour=0, minute=0, second=0, microsecond=0)
        if walk and not any(p["platform"] == platform and p.get("status") == "posted" and p["slug"] in walk
                            and parse_time(p["time"]) >= day for p in posted):
            long_ago = now() - dt.timedelta(days=365)
            item_last = lambda v: rot.last_shown({"machine": v.get("item_machine") or v["slug"]}, hist) or long_ago
            for group in (live, walk - live):
                free = [v for v in usable if v["slug"] in group
                        and (v["slug"] not in last or last[v["slug"]] <= cutoff)]
                if group is live:
                    due = [v for v in free if now() - item_last(v) >= dt.timedelta(hours=WALK_ITEM_HOURS)
                           and (rot.allowed(v, hist) or rot.fallback_ok(v, hist))]
                    due.sort(key=lambda v: (last.get(v["slug"]) or long_ago, item_last(v)))
                else:
                    # Machine rule: 14 days clear first, else the rotation's own 7-day floor, never closer.
                    due = [v for v in free if rot.allowed(v, hist)] or [v for v in free if rot.fallback_ok(v, hist)]
                    due.sort(key=lambda v: last.get(v["slug"]) or long_ago)
                if due:
                    return due[0], due[0]["slug"] in last
    # Then swaps (see NEW_LOOK): the same machine already went out in the old look and that post comes down
    # once this one is up, so the machine rotation does not hold a swap back. Oldest old-look post first.
    swaps = [v for v in usable if swap_due(v, posted, platform)
             and platform in ("instagram", "facebook")]
    if swaps:
        first = {}
        for p in posted:
            if p["platform"] == platform and p.get("status") == "posted":
                first.setdefault(p["slug"], parse_time(p["time"]))
        swaps.sort(key=lambda v: first.get(v["slug"]) or now())
        return swaps[0], False
    usable = new_look_first(usable)
    strict = [v for v in usable if rot.allowed(v, hist)]
    # A clip another surface showed in the last 36 hours goes here next, so Instagram, Facebook and
    # TikTok share one showing of a machine instead of each using up a different one.
    cross = [v for v in strict if rot.in_run(v, hist) and (v["slug"] not in last or last[v["slug"]] <= cutoff)]
    if cross:
        cross.sort(key=lambda v: rot.last_shown(v, hist))
        return cross[0], cross[0]["slug"] in last
    video, repeat = _choose(strict, last, cutoff, platform, scores, hist)
    if video:
        return video, repeat
    floor = [v for v in usable if rot.fallback_ok(v, hist)]
    floor.sort(key=lambda v: rot.last_shown(v, hist) or now() - dt.timedelta(days=365))
    floor = [v for v in floor if v["slug"] not in last or last[v["slug"]] <= cutoff]
    if floor:
        print(f"rotation: no machine free for 14 days on {platform}; using {floor[0]['slug']}, "
              f"last shown {rot.last_shown(floor[0], hist)}")
        return floor[0], floor[0]["slug"] in last
    print(f"rotation: every machine was shown in the last {rot.FLOOR_DAYS} days; skipping this {platform} slot")
    return None, False


def _choose(usable, last, cutoff, platform, scores, hist):
    """The old order (week's push, fresh cuts, best repeats) over clips the rotation allows,
    with real listings first among the fresh cuts and categories spread."""
    # A week's push ("boost" with an active "boost_until") goes ahead of even
    # the fresh cuts once its 10 days are up, so the week's demand clips run
    # this week (Nov 16: generators, pumps, inspection cameras).
    pushed = [v for v in usable if v["slug"] in last and last[v["slug"]] <= cutoff
              and v.get("boost") and v.get("boost_until") and now() < parse_time(v["boost_until"])]
    if pushed:
        pushed.sort(key=lambda v: (-v["boost"], last[v["slug"]]))
        return rot.spread(pushed, hist, platform)[0], True
    fresh = [v for v in usable if v["slug"] not in last]
    if fresh:
        fresh.sort(key=lambda v: (not v.get("real"), -int(v.get("added", "0").replace("-", "")),
                                  v.get("priority", 999)))
        return rot.spread(fresh, hist, platform)[0], False
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
    # "boost_until" (ISO time) keeps a hand boost on top of the scorecard
    # until then, for a week's push (Nov 16: buyers' top searches).
    until = lambda v: bool(v.get("boost_until")) and now() < parse_time(v["boost_until"])
    hand = lambda v: (v.get("boost", 0) if (not fresh_rank or v.get("boost_keep") or until(v)) and
                      (not v.get("boost_until") or until(v)) else 0)
    old.sort(key=lambda v: (-(scores.get(v["slug"], 0) + hand(v) + auto.get(v["slug"], 0)), last[v["slug"]]))
    return rot.spread(old, hist, platform)[0], True


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


# The posting job's full checkout takes 4-5 minutes (all the videos), so a run
# the gate found due near a window's end used to land outside it and post
# nothing: the 3:55-4:45 pm slot never posted from Nov 18 to Nov 22 because its
# only reliable start was at 4:42 pm. The posting job now judges the slot by
# the gate's time (SLOT_AT) if that is at most SLOT_AT_MAX_MIN old.
SLOT_AT_MAX_MIN = 20


def slot_now():
    """Time to judge the slot by: the gate's time when recent, else now."""
    raw = (os.environ.get("SLOT_AT") or "").strip()
    if raw:
        try:
            t = parse_time(raw)
            if dt.timedelta(0) <= now() - t <= dt.timedelta(minutes=SLOT_AT_MAX_MIN):
                return t
        except ValueError:
            pass
    return now()


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
#
# Three re-shares a day per platform, not one per Reel (Alan, Nov 26: "Re-share
# 3 Reels a day"). Every Reel used to be re-shared, about eight Stories a day
# with no link, which buried the two Stories a day that carry a tappable link
# (stories/linked/, 9:30 am and 12:15 pm Central). STORY_RESHARE_FROM_CT is the
# earliest Central time for the day's first, second and third re-share: the
# 7:00 am seller post, the 3:55 pm Reel and the 6:30 pm Reel. A run that fails
# hands its turn to the next slot. A manual run that names a video (SLUG) is
# not capped. library.json "story_reshares" (["07:00", ...]) overrides the list;
# an empty list stops the re-shares.

STORY_BASE = {"instagram_story": "instagram", "facebook_story": "facebook"}
STORY_RESHARE_FROM_CT = [(7, 0), (15, 55), (18, 30)]


def set_story_reshares(lib):
    """library.json "story_reshares": ["07:00", "15:55", ...] replaces the default times."""
    times = lib.get("story_reshares")
    if times is None:
        return
    STORY_RESHARE_FROM_CT[:] = sorted(tuple(int(x) for x in str(s).split(":")[:2]) for s in times)


def story_reshare_wait(posted, story_platform, t=None):
    """None when a re-share may go now, else one line saying why not."""
    local = (t or now()).astimezone(CENTRAL)
    today = sum(1 for p in posted if p["platform"] == story_platform and p.get("status") == "posted"
                and not p.get("forced") and parse_time(p["time"]).astimezone(CENTRAL).date() == local.date())
    if today >= len(STORY_RESHARE_FROM_CT):
        return f"{today} re-shared today, the daily limit"
    h, m = STORY_RESHARE_FROM_CT[today]
    if (local.hour, local.minute) < (h, m):
        return f"re-share {today + 1} of {len(STORY_RESHARE_FROM_CT)} waits until {h}:{m:02d} Central"
    return None


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


# ---------- Threads ----------
# Threads takes no file upload: it fetches the video from a public URL. The
# repo is public, so the file at this exact commit is served by jsDelivr
# (video/mp4, 20 MB limit per file) with raw.githubusercontent.com as the
# fallback. Each Threads post follows the newest Instagram Reel from the last
# 24 hours that is not on Threads yet, so Threads gets what Instagram got.

def threads_api(method, path, token, **fields):
    if method == "GET":
        return call("GET", f"{THREADS}/{path}", params={**fields, "access_token": token})
    return call("POST", f"{THREADS}/{path}", data={**fields, "access_token": token})


def threads_pick(videos, posted):
    since = now() - dt.timedelta(hours=24)
    gap = now() - dt.timedelta(days=MIN_GAP_DAYS)
    done = {p["slug"] for p in posted if p["platform"] == "threads"
            and p.get("status") == "posted" and parse_time(p["time"]) >= gap}
    reels = sorted((p for p in posted if p["platform"] == "instagram" and p.get("status") == "posted"
                    and parse_time(p["time"]) >= since and p["slug"] not in done),
                   key=lambda p: p["time"], reverse=True)
    for r in reels:
        v = next((v for v in videos if v["slug"] == r["slug"]), None)
        if v and not v.get("hold") and os.path.exists(os.path.join(ROOT, v["file"])):
            return v
    return None


def commit_sha():
    try:
        import subprocess
        out = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return os.environ.get("GITHUB_SHA") or "main"


def threads_video_urls(v):
    repo = os.environ.get("GITHUB_REPOSITORY") or "AIE-Solutions/yardswaps-media"
    sha = commit_sha()
    return [f"https://cdn.jsdelivr.net/gh/{repo}@{sha}/{v['file']}",
            f"https://raw.githubusercontent.com/{repo}/{sha}/{v['file']}"]


def url_is_video(url):
    """HEAD the URL (this also warms the CDN copy before Threads asks for it)."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status == 200 and r.headers.get("Content-Type", "").startswith("video/")
    except Exception:
        return False


def threads_publish(token, user_id, v, caption):
    urls = threads_video_urls(v)
    if not url_is_video(urls[0]):
        print(f"  jsDelivr did not serve {v['file']} as video, using raw.githubusercontent.com")
        urls = urls[1:]
    last_error = None
    for url in urls:
        c = threads_api("POST", f"{user_id}/threads", token, media_type="VIDEO",
                        video_url=url, text=caption, topic_tag=threads_topic(v))
        cid = c["id"]
        status = {}
        for _ in range(60):                 # up to 10 minutes
            time.sleep(10)
            status = threads_api("GET", cid, token, fields="status,error_message")
            if status.get("status") in ("FINISHED", "ERROR", "EXPIRED"):
                break
        if status.get("status") == "FINISHED":
            mid = threads_api("POST", f"{user_id}/threads_publish", token, creation_id=cid)["id"]
            try:
                link = threads_api("GET", mid, token, fields="permalink").get("permalink", "")
            except GraphError:
                link = ""
            return mid, link
        last_error = f"container {status.get('status')}: {status.get('error_message', '')} ({url.split('/')[2]})"
        print(f"  Threads could not use {url.split('/')[2]}: {last_error}")
    raise GraphError(f"Threads video failed: {last_error}")


def threads_days_left(token):
    """Days left on the Threads token; refreshes it when under 30 days.

    A long-lived Threads token lasts 60 days and can be refreshed once it is a
    day old. Whether Meta extends the same token string is not documented, so
    the expiry is read again after the refresh rather than assumed.
    """
    def left():
        d = threads_api("GET", "debug_token", token, input_token=token).get("data", {})
        ends = [t for t in (d.get("expires_at"), d.get("data_access_expires_at")) if t]
        return min(ends) - time.time() if ends else None
    s = left()
    if s is not None and s < 30 * 86400:
        try:
            call("GET", f"{THREADS.rsplit('/', 1)[0]}/refresh_access_token",
                 params={"grant_type": "th_refresh_token", "access_token": token})
            s = left()
        except GraphError as e:
            print(f"::warning::Could not refresh THREADS_TOKEN: {str(e)[:200]}")
    return None if s is None else s / 86400


def run_threads(token, videos, posted, dry, summary, force=None):
    """Post the newest unshared Instagram Reel to Threads. Never fails the run."""
    video = threads_pick(videos, posted)
    if dry:
        v = video or pick(videos, posted, "instagram", force)[0]
        if v:
            cap = threads_caption(v)
            summary.append(f"threads: would post {video['slug'] if video else 'the Instagram Reel above'}"
                           f" (topic {threads_topic(v)}, {len(cap)} chars, "
                           f"{'token set' if token else 'no THREADS_TOKEN yet'})\n"
                           f"video: {threads_video_urls(v)[0]}\n{cap}\n")
        return None
    why = None if force else health_blocked("threads", posted)
    if why:
        summary.append(f"threads: skipped, {why}")
        return None
    if not token:
        print("::notice::THREADS_TOKEN is not set yet, so nothing went to Threads. See reels/README.md, Threads.")
        summary.append("threads: skipped, THREADS_TOKEN is not set yet")
        return None
    warning = None
    try:
        days = threads_days_left(token)
        if days is not None and days < 14:
            warning = (f"THREADS_TOKEN stops working in {days:.0f} days. Make a new one "
                       "(reels/README.md, Threads) and replace the secret.")
            print(f"::warning::{warning}")
    except GraphError as e:
        print(f"::warning::Could not check THREADS_TOKEN's expiry: {str(e)[:200]}")
    if not video:
        summary.append("threads: skipped, no new Instagram Reel in the last 24 hours to share")
        return warning
    entry = {"time": iso(now()), "platform": "threads", "slug": video["slug"], "repeat": False}
    try:
        since = now() - dt.timedelta(hours=24)
        lf = any(p["platform"] == "instagram" and p["slug"] == video["slug"] and p.get("list_free")
                 and p.get("status") == "posted" and parse_time(p["time"]) >= since for p in posted)
        cap = threads_caption(video)
        pr_id = next((p.get("promo") for p in posted if p["platform"] == "instagram"
                      and p["slug"] == video["slug"] and p.get("promo") and p.get("status") == "posted"
                      and parse_time(p["time"]) >= since), None)
        promo = next((pr for pr in active_promos("threads") if pr["id"] == pr_id), None)
        if promo and not lf:
            entry["promo"] = promo["id"]
            cap = promo_threads_caption(video, promo, promo_turn(posted, "threads", promo))
        if lf:
            entry["list_free"] = True
            cap = list_free_threads_caption(video, sum(1 for p in posted if p["platform"] == "threads"
                                                       and p.get("list_free") and p.get("status") == "posted"))
        me = threads_api("GET", "me", token, fields="id,username")
        mid, link = threads_publish(token, me["id"], video, cap)
        entry.update(status="posted", id=mid, url=link)
        summary.append(f"threads: posted {video['slug']} {link}")
    except (GraphError, KeyError) as e:
        entry.update(status="failed", error=str(e)[:500])
        summary.append(f"threads: FAILED {video['slug']}: {e}")
        print(f"::warning::threads failed: {str(e)[:300]}")
    posted.append(entry)
    return warning


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
            f.write(f"due={int(due)}\nat={iso(now())}\n")
    return 0


TAKEDOWN_PLATFORMS = ("instagram", "facebook")   # Stories expire by themselves; TikTok/YouTube have no delete


def takedown_queue(posted, platform, library):
    """Old Reels still up on the platform that Alan asked to swap out, in the order they come down:
    stock pictures first, then the held older clips that cropped the machine, oldest post first."""
    lib = {v["slug"]: v for v in library}

    def rank(p):
        v = lib.get(p["slug"])
        if v is None or not real_picture(v, REAL_PICTURES + ("ad",)):
            return 0          # stock or AI picture (or a clip no longer in the library)
        if v.get("hold") and v.get("cut") != "listing":
            return 1          # older Motion clip held for cropping the machine (Alan 11-26)
        return None           # a real clip still in rotation stays up
    rows = [(rank(p), parse_time(p["time"]), p) for p in posted
            if p["platform"] == platform and p.get("status") == "posted" and p.get("id") and not p.get("removed")
            and not p.get("takedown_skip")]
    return [p for r, t, p in sorted((x for x in rows if x[0] is not None), key=lambda x: (x[0], x[1]))]


def remove_post(token, platform, p, reason, by):
    """Delete one of our Instagram or Facebook Reels and mark its log row. Returns a summary line."""
    try:
        r = call("DELETE", f"{GRAPH}/{p['id']}?" + urllib.parse.urlencode({"access_token": token}))
        ok = r is True or (isinstance(r, dict) and (r.get("success") or r.get("deleted_id")))
        if not ok:
            raise GraphError(f"unexpected reply {str(r)[:200]}")
    except (GraphError, urllib.error.URLError) as e:
        msg = str(e)
        p.setdefault("takedown_errors", []).append(f"{iso(now())} {msg[:200]}")
        print(f"::warning::{platform} takedown of {p['slug']} ({p['id']}) failed: {msg[:300]}")
        if len(p["takedown_errors"]) >= 2:
            # Twice refused (deleted by hand already, or Meta will not delete this one): stop retrying it,
            # so the queue moves on; it stays listed for a person to check.
            p["takedown_skip"] = True
        return f"  {platform}: could not take down {p['slug']} {p.get('url', '')}: {msg[:160]}"
    p["removed"] = iso(now())
    p["removed_reason"] = reason
    p["replaced_by"] = by
    return f"  {platform}: took down {p['slug']} ({reason}) {p.get('url', '')}"


def takedown(token, posted, platform, video, library, entry):
    """After a new-look Reel went live: remove this platform's old-look Reels of the same clip, then one
    Reel from takedown_queue(). Never more than MAX_TAKEDOWNS a run, and a failure never fails the run."""
    if platform not in TAKEDOWN_PLATFORMS or os.environ.get("TAKEDOWN") == "0":
        return []
    lines, done = [], 0
    same = [p for p in posted if p is not entry and p["platform"] == platform and p["slug"] == video["slug"]
            and p.get("status") == "posted" and p.get("id") and not p.get("removed") and not p.get("takedown_skip")
            and p.get("look") != NEW_LOOK]
    for p in same[:MAX_TAKEDOWNS]:
        lines.append(remove_post(token, platform, p, "old look, new look posted", entry.get("id")))
        done += 1
    queue = takedown_queue(posted, platform, library)
    if queue and done < MAX_TAKEDOWNS + 1:
        p = queue[0]
        lines.append(remove_post(token, platform, p, "one down per new Reel up", entry.get("id")))
    return lines


MAX_TAKEDOWNS = 3


def main():
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    dry = os.environ.get("DRY_RUN") == "1"
    page_id = os.environ.get("FB_PAGE_ID") or "1291163214083476"
    ig_id = os.environ.get("IG_USER_ID") or "17841429324062623"
    platforms = [p.strip() for p in (os.environ.get("PLATFORMS") or "instagram,facebook,instagram_story,facebook_story,threads").split(",") if p.strip()]
    threads_token = os.environ.get("THREADS_TOKEN", "").strip()
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
    set_story_reshares(lib)
    videos = with_real_pictures(with_endcard(lib["videos"]))
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

    want_list_free = os.environ.get("LIST_FREE") == "1"
    want_promo = (os.environ.get("PROMO") or "").strip()
    promo_cfg = promos_config()
    for platform in reel_platforms:
        why = None if force else health_blocked(platform, posted)
        if why:
            summary.append(f"{platform}: skipped, {why}")
            continue
        list_free = want_list_free or (not force and list_free_due(posted, platform))
        video = None
        promo = None
        if not list_free:
            if want_promo:
                promo = next((pr for pr in promo_cfg.get("promos", []) if pr["id"] == want_promo), None)
            elif not force:
                promo = promo_now(posted, platform, cfg=promo_cfg)
        if promo and not force:
            video, repeat = promo_pick(videos, posted, platform, promo)
            if repeat and token:
                if scores is None:
                    scores = ig_scores(token, posted)
                video, repeat = promo_pick(videos, posted, platform, promo, scores)
            if not video:
                summary.append(f"{platform}: no clip fits the {promo['id']} promotion, posting a regular Reel")
                promo = None
        if list_free and not force:
            video, repeat = list_free_pick(videos, posted, platform)
            if repeat and token:
                if scores is None:
                    scores = ig_scores(token, posted)
                video, repeat = list_free_pick(videos, posted, platform, scores)
            if not video:
                list_free = False
                summary.append(f"{platform}: no clip fits the list-it-free post, posting a regular Reel")
        if video is None:
            video, repeat = pick(videos, posted, platform, force)
        if not list_free and not promo and repeat and not force and token:
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
        if list_free:
            lf_turn = sum(1 for p in posted if p["platform"] == platform and p.get("list_free")
                          and p.get("status") == "posted")
            caption = (list_free_ig_caption(video, lf_turn) if platform == "instagram"
                       else list_free_fb_caption(video, lf_turn))
        elif promo:
            pt = promo_turn(posted, platform, promo)
            caption = (promo_ig_caption(video, promo, pt) if platform == "instagram"
                       else promo_fb_caption(video, promo, pt))
        else:
            caption = ig_caption(video, turn) if platform == "instagram" else fb_caption(video)
        if dry:
            summary.append(f"{platform}: would post {video['slug']} (repeat={repeat}"
                           f"{', list it free' if list_free else ''}"
                           f"{', promotion ' + promo['id'] if promo else ''})\n{caption}\n")
            continue
        # GitHub can start a scheduled run hours late or drop it, so each slot
        # has backup crons. The first run in a slot window posts; the rest stop.
        if not force and slot_window(slot_now()) is None:
            summary.append(f"{platform}: skipped, outside the slot windows (" + slots_text() + " Central)")
            continue
        if not force and slot_done(posted, platform, slot_now()):
            summary.append(f"{platform}: skipped, this slot already posted (late or backup run)")
            continue
        if not force and ours_recent(posted, platform) >= max_ours_per_20h():
            summary.append(f"{platform}: skipped, already posted {max_ours_per_20h()} in the last 20 hours")
            continue
        entry = {"time": iso(now()), "platform": platform, "slug": video["slug"], "repeat": repeat}
        if is_new_look(video):
            entry["look"] = NEW_LOOK
        if force:
            entry["forced"] = True
        if list_free:
            entry["list_free"] = True
        if promo:
            entry["promo"] = promo["id"]
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
            summary.append(f"{platform}: posted {video['slug']}{' (list it free)' if list_free else ''}"
                           f"{' (promotion ' + promo['id'] + ')' if promo else ''} {link}")
        except GraphError as e:
            entry.update(status="failed", error=str(e)[:500])
            summary.append(f"{platform}: FAILED {video['slug']}: {e}")
            failed = True
        posted.append(entry)
        if entry.get("status") == "posted" and is_new_look(video):
            summary.extend(takedown(token, posted, platform, video, lib["videos"], entry))

    for platform in story_platforms:
        wait = None if force else story_reshare_wait(posted, platform)
        if wait:
            summary.append(f"{platform}: skipped, {wait}")
            continue
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
        if force:
            entry["forced"] = True
        if is_new_look(video):
            entry["look"] = NEW_LOOK
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

    threads_warning = None
    if "threads" in platforms:
        threads_warning = run_threads(threads_token, videos, posted, dry, summary, force)

    if not dry:
        with open(POSTED, "w", encoding="utf-8") as f:
            json.dump(posted, f, indent=1, ensure_ascii=False)
            f.write("\n")
    text = "\n".join(summary)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### Reels run\n\n```\n" + text + "\n```\n")
    for w in (renew_warning, threads_warning):
        if w:
            with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a", encoding="utf-8") as f:
                f.write(f"\n**{w}**\n")
    # Fail the run (GitHub emails the repo admin) once fewer than 7 days are left.
    if renew_warning and left is not None and left < 7:
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
