#!/usr/bin/env python3
"""Daily "Just listed" posts: one live YardSwaps listing a day on Instagram
and Facebook, as a branded photo card.

Runs from .github/workflows/listings.yml in three steps:

  prep    Reads the public listings API, picks listings that haven't been
          featured (newest first, one waiting per seller), checks the photos
          (skips any photo with a face, blurs text that carries digits, such
          as phone numbers, plates and street numbers), renders a 1080x1350
          card into listings/cards/ and queues it as "pending".
  review  Not this script: a daily Claude task looks at each pending card and
          sets status "approved" or "rejected" (with a reason) in queue.json.
  post    Posts the oldest approved card to Instagram (feed image) and to the
          Facebook Page (photo post), then logs it in listings/posted.json.

Paying sellers first (Alan, 2026-11-16): prep reads /api/social-feature
before anything else. Each paying Pro or Dealer seller (then each storefront
in its trial days) not featured in the last PAID_GAP_DAYS gets one card marked
feature "paid" at the front of the queue, past the usual waiting cap, and post
posts an approved paid card before any other. Sellers who switched the
feature off in the app are skipped and their waiting cards withdrawn. Each
paid card is logged in listings/paid-features.json (queued, then posted).

Seller names, phone numbers and descriptions never go into a caption or a
card: only the title, price, year/hours/miles, city and category.

Env:
  MODE             prep | post
  META_PAGE_TOKEN  Page token (same secret as the Reels poster); post only
  DRY_RUN          "1" = render and print, write and post nothing
  LISTINGS_API     default https://www.yardswaps.com/api/listings
  FEATURE_API      default https://www.yardswaps.com/api/social-feature
  RAW_BASE         public base URL for cards (Instagram fetches the image)
"""
import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reels"))
from post_reels import (GraphError, graph, iso, load, now, parse_time,  # noqa: E402
                        CLEAR_MINUTES, POSTED as REELS_POSTED)

HERE = os.path.join(ROOT, "listings")
QUEUE = os.path.join(HERE, "queue.json")
PHOTOS = os.path.join(HERE, "photos")   # cleaned, uncropped photo per queued listing (Motion uses it as a Short opener)
POSTED = os.path.join(HERE, "posted.json")
WANTED = os.path.join(HERE, "wanted.json")
PAID_LOG = os.path.join(HERE, "paid-features.json")  # every paid feature: queued, posted
CARDS = os.path.join(HERE, "cards")
FONTS = os.path.join(HERE, "fonts")

SITE = "https://www.yardswaps.com"
API = os.environ.get("LISTINGS_API") or f"{SITE}/api/listings"
FEATURE_API = os.environ.get("FEATURE_API") or f"{SITE}/api/social-feature"
RAW_BASE = os.environ.get("RAW_BASE") or \
    "https://raw.githubusercontent.com/AIE-Solutions/yardswaps-media/main/listings/cards"
PAGE_ID = os.environ.get("FB_PAGE_ID") or "1291163214083476"
IG_ID = os.environ.get("IG_USER_ID") or "17841429324062623"
UA = "yardswaps-just-listed/1.0 (https://github.com/AIE-Solutions/yardswaps-media)"

WAITING_MAX = 3          # pending + approved cards kept ready
NEW_DAYS = 7             # "Just listed" label inside this many days, else "For sale"
REFEATURE_DAYS = 45      # a listing can be featured again after this
# Paying sellers (Pro, Dealer; then storefronts in their trial days) go first:
PAID_GAP_DAYS = 3        # one paid card per seller per this many days (about twice a week)
PAID_REFEATURE_DAYS = 14 # a paid seller's same listing can come back after this
PHOTOS_TRIED = 4         # photos checked per listing before giving up on it
# One post a day, 2:15 pm Central (20:15 UTC in winter): 100+ minutes after
# HeyCatch's 12:33 pm post and 95+ minutes before the 3:55 pm Reel.
POST_OPEN_UTC = (20, 15)
POST_CLOSE_UTC = 3       # a run GitHub starts after 03:00 UTC waits for tomorrow
# "Buyers are looking for X" cards (wanted.json) slot in between listing cards.
WANTED_GAP_DAYS = 3      # at most one wanted card queued or posted per this many days
WANTED_REPEAT_DAYS = 30  # the same wanted post never twice inside this
WANTED_MAX_AGE_DAYS = 30 # search numbers older than this are stale: queue none

# Colours from the design system (YardSwaps.css :root).
BG = (246, 246, 248)
SLATE = (26, 51, 83)
BLUE = (37, 99, 235)
GRAY = (84, 84, 86)

CATEGORY_TAGS = {
    "fleet": ["#FleetTrucks", "#WorkTrucks"], "trailers": ["#Trailers", "#EquipmentTrailer"],
    "generators": ["#Generators", "#BackupPower"], "pressure": ["#PressureWasher", "#PowerWashing"],
    "vacuum": ["#VacuumTruck", "#Hydrovac"], "pumps": ["#Pumps", "#IndustrialPumps"],
    "hydro": ["#HydroJetting", "#DrainCleaning"], "inspection": ["#PipeInspection", "#SewerCamera"],
    "compressors": ["#AirCompressor", "#Compressors"], "welding": ["#Welding", "#Welder"],
    "machining": ["#Machining", "#CNC"], "automotive": ["#AutoShop", "#ShopEquipment"],
    "tools": ["#PowerTools", "#Tools"], "excavators": ["#Excavator", "#HeavyEquipment"],
    "paving": ["#Paving", "#Compaction"], "forklifts": ["#Forklift", "#MaterialHandling"],
    "aerial": ["#AerialLift", "#BoomLift"], "cranes": ["#Crane", "#Rigging"],
    "concrete": ["#Concrete", "#Masonry"], "drilling": ["#Drilling", "#DrillRig"],
    "electrical": ["#Electrical", "#Electrician"], "environmental": ["#Environmental", "#Remediation"],
    "safety": ["#Safety", "#PPE"], "agriculture": ["#FarmEquipment", "#Tractor"],
    "landscaping": ["#Landscaping", "#Turf"], "restaurant": ["#RestaurantEquipment", "#CommercialKitchen"],
    "refrigeration": ["#CommercialRefrigeration", "#Refrigeration"], "cooking": ["#CommercialKitchen", "#Ovens"],
    "warehouse": ["#Warehouse", "#Racking"], "retail": ["#RetailFixtures", "#POS"],
    "office": ["#OfficeFurniture", "#Office"], "laundry": ["#CommercialLaundry", "#Laundromat"],
    "hvac": ["#HVAC", "#HVACLife"], "parts": ["#Parts", "#SpareParts"],
}
ROTATE_TAGS = ["#Jobsite", "#Tradespeople", "#IndustrialEquipment", "#EquipmentMarketplace"]
QUESTIONS = [
    "What would you put this to work on first?",
    "What's the one machine your yard can't run without?",
    "Buy it used or new: which way do you go on a machine like this?",
    "What do you check first when you look at a used one?",
]

PHONE_RE = re.compile(r"(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
CONTACT_RE = re.compile(r"@|https?://|www\.|\.com\b|call or text", re.I)


# ---------- helpers ----------

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


ACRONYMS = {"AC", "A/C", "HP", "4WD", "2WD", "AWD", "4X4", "CAT", "PTO", "ROPS", "FOPS", "GVWR",
            "CNC", "LED", "USA", "MIG", "TIG", "DEF", "DPF", "CDL", "BTU", "IOT", "HVAC", "LP", "CFM", "PSI",
            "GPM", "KW", "KVA", "V", "II", "III", "IV", "JD", "NH"}
SMALL = {"and", "with", "the", "for", "of", "in", "on", "or", "to", "a", "an"}


def nice_title(t):
    """Title case for shouting titles, keeping model codes like 289D3 and A/C."""
    t = re.sub(r"\s+", " ", (t or "").strip())
    letters = [c for c in t if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.7:
        words = []
        for i, w in enumerate(t.split(" ")):
            m = re.match(r"^([^A-Za-z0-9]*)(.*?)([^A-Za-z0-9/]*)$", w)
            pre, core, post = m.groups()
            up = core.upper()
            if up in ACRONYMS or (core.isalpha() and len(core) <= 3 and not set(up) & set("AEIOUY")):
                core = up
            elif any(ch.isdigit() for ch in core):
                core = "-".join(x.lower() if x.isalpha() and len(x) > 3 else x for x in core.split("-"))
            elif core.lower() in SMALL and i > 0:
                core = core.lower()
            elif core:
                parts = core.split("-")
                core = "-".join([parts[0].capitalize()] + [x.lower() for x in parts[1:]])
            words.append(pre + core + post)
        t = " ".join(words)
    t = t.replace(" — ", ", ").replace(" – ", ", ")
    return t[0].upper() + t[1:] if t else t


def price_text(p):
    return f"${p:,.0f}" if p and p > 0 else "Call for price"


def place(l):
    loc = (l.get("location") or "").strip()
    m = re.match(r"^([A-Za-z .'-]+),\s*([A-Z]{2})\b", loc)
    if m:
        return f"{m.group(1).strip()}, {m.group(2)}"
    return l.get("state") or ""


def facts(l):
    bits = [price_text(l.get("price"))]
    if l.get("year"):
        bits.append(str(l["year"]))
    if l.get("hours"):
        bits.append(f"{l['hours']:,} hours")
    if l.get("mileage"):
        bits.append(f"{l['mileage']:,} miles")
    if place(l):
        bits.append(place(l))
    return " · ".join(bits)


def safe_title(l):
    t = l.get("title") or ""
    return bool(t.strip()) and not PHONE_RE.search(t) and not CONTACT_RE.search(t)


def is_new(l):
    return now() - parse_time(l["createdAt"]) <= dt.timedelta(days=NEW_DAYS)


def listing_url(lid, source):
    return (f"{SITE}/listing/{lid}?utm_source={source}&utm_medium=social"
            f"&utm_campaign=just_listed")


def captions(l, turn):
    title = nice_title(l["title"])
    lead = "Just listed on YardSwaps" if is_new(l) else "For sale on YardSwaps"
    cat = CATEGORY_TAGS.get(l.get("category"), ["#Equipment", "#ForSale"])
    rot = (ROTATE_TAGS * 2)[(turn * 2) % len(ROTATE_TAGS):(turn * 2) % len(ROTATE_TAGS) + 2]
    q = QUESTIONS[turn % len(QUESTIONS)]
    ig = (f"{lead}: {title}\n\n{facts(l)}\n\n"
          "See it in the free YardSwaps app: yardswaps.com/i (link in bio). "
          "Got gear sitting idle? List it free in about a minute.\n\n"
          "Follow @yardswaps for a new listing every day.\n\n"
          f"{' '.join(cat + ['#UsedEquipment'] + rot)}\n\n{q}")
    fb = (f"{lead}: {title}\n\n{facts(l)}\n\n"
          f"See the photos and message the seller: {listing_url(l['id'], 'facebook')}\n\n"
          "Got gear sitting idle? List it free in about a minute.\n\n"
          f"{' '.join(cat + ['#YardSwaps', '#UsedEquipment'] + ROTATE_TAGS)}\n\n{q}")
    return ig, fb


# ---------- photo checks ----------

def faces_in(img_bgr):
    import cv2
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    scale = 1000 / max(h, w) if max(h, w) > 1000 else 1.0
    if scale != 1.0:
        gray = cv2.resize(gray, (int(w * scale), int(h * scale)))
    found = 0
    for name in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
        cc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, name))
        hits = cc.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8, minSize=(40, 40))
        found += len(hits)
    return found


def blur_digit_text(img_bgr):
    """Blur every OCR word that contains a digit (phones, plates, street numbers).
    Returns (image, blurred_count, ocr_ok)."""
    import cv2
    if not shutil.which("tesseract"):
        return img_bgr, 0, False
    import pytesseract
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT, config="--psm 11")
    out = img_bgr.copy()
    n = 0
    for i, word in enumerate(data["text"]):
        word = (word or "").strip()
        try:
            conf = float(data["conf"][i])
        except ValueError:
            conf = -1
        if conf < 40 or not word or not any(ch.isdigit() for ch in word):
            continue
        x, y, w, h = (data[k][i] for k in ("left", "top", "width", "height"))
        pad = max(6, h // 2)
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(out.shape[1], x + w + pad), min(out.shape[0], y + h + pad)
        roi = out[y0:y1, x0:x1]
        if roi.size:
            k = max(15, (max(roi.shape[:2]) // 2) * 2 + 1)
            out[y0:y1, x0:x1] = cv2.GaussianBlur(roi, (k, k), 0)
            n += 1
    return out, n, True


# ---------- card ----------

def font(name, size, weight):
    from PIL import ImageFont
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def wrap(draw, text, f, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while draw.textlength(lines[-1] + "…", font=f) > width and " " in lines[-1]:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1].rstrip(",;:-") + "…"
    return lines


def card_facts(l, with_place=True):
    """What a buyer asks first, for the card and the listing Reel: condition, year, hours, miles, then the
    city. Nothing the title already says, three items at most."""
    title = (l.get("title") or "").lower()
    bits = []
    cond = re.sub(r"\s*[—–-]\s*", " · ", (l.get("condition") or "").strip())
    if cond and cond.lower() not in title:
        bits.append(cond)
    if l.get("year") and not re.search(r"\b(19|20)\d\d\b", title):   # a year in the title is the seller's word
        bits.append(str(l["year"]))
    if l.get("hours") and "hour" not in title and "hrs" not in title:
        bits.append(f"{l['hours']:,} hours")
    if l.get("mileage") and "mile" not in title:
        bits.append(f"{l['mileage']:,} miles")
    bits = bits[:3]
    if with_place and place(l):
        bits = bits[:2] + [place(l)]
    return " · ".join(bits)


CUT_WORDS = (" with ", " on ", " w/ ")
DANGLING = {"with", "and", "on", "of", "for", "the", "a", "an", "in", "at", "to", "plus", "&", "+", "or", "by"}


def short_title(t):
    """The part of a seller's title that names the item. Sellers pack hours, condition and extras into the
    title ("... Leaf Vacuum, 400 hrs, Like New"); a post prints those as facts, so the title stops at the first
    clause break. Never an ellipsis: a cut title ends on a whole word."""
    t = re.sub(r"\s+", " ", (t or "").strip())
    t = re.sub(r"^sale pending\s*[—–,:-]\s*", "", t, flags=re.I)
    for sep in (" — ", " – ", " - ", " | ", " / ", ", ", " (", " PN:", " pn:"):
        head = t.split(sep, 1)[0].strip()
        if head != t and len(head) >= 10 and len(head.split()) >= 2:
            t = head
    t = re.sub(r"\s+for sale$", "", t, flags=re.I)
    if len(t) > 28:
        for w in CUT_WORDS:
            i = t.lower().find(w)
            if i >= 8:
                t = t[:i]
    words = t.split()
    while len(words) > 2 and words[-1].lower().strip(",;:") in DANGLING:
        words.pop()
    return " ".join(words).rstrip(" ,;:-")


def spec_title(l):
    """The short title a buyer scans. The seller's own words, cut to the part that names the item
    ("2008 Tennant M20 Ride-On Sweeper-Scrubber"), when the title opens with the year or the make. An ad-style
    title ("Zero-tail-swing Deere 50G with quick coupler") becomes year, make, model from the listing's own
    fields ("2016 John Deere 50G"). A part keeps its own name, never just the machine it fits."""
    title = nice_title(l.get("title") or "")
    short = short_title(title)
    make = (l.get("manufacturer") or "").strip()
    model = str((l.get("specs") or {}).get("Model") or l.get("model") or "").strip()
    low = title.lower()
    first = (short.split() or [""])[0].lower()
    opens_plain = bool(re.match(r"(19|20)\d\d$", first)) or (make and first == make.split()[0].lower())
    if (not opens_plain and l.get("year") and make and model and model.lower() in low
            and make.split()[-1].lower() in low):
        return " ".join([str(l["year"]), make, model])
    return short


def facts_lines(l):
    """The facts for the post kit, most asked first, each a short line: hours or miles with the town (state
    spelled out), then condition and year. Nothing the short title already says."""
    sys.path.insert(0, os.path.join(ROOT, "brand", "posts"))
    import kit
    title = spec_title(l).lower()
    first = []
    if l.get("hours"):
        first.append(f"{l['hours']:,} hrs")
    if l.get("mileage"):
        first.append(f"{l['mileage']:,} miles")
    where = kit.spell_state(place(l))
    second = []
    cond = re.sub(r"\s*[—–-]\s*", " · ", (l.get("condition") or "").strip())
    if cond:
        second.append(cond)
    if l.get("year") and not re.search(r"\b(19|20)\d\d\b", title):   # a year in the title is the seller's word
        second.append(str(l["year"]))
    if not first:
        first, second = second, []
    if where:
        first = first[:2] + [where]
    return [" · ".join(x) for x in (first, second) if x]


def render_card(photo_bgr, l, out_path):
    """The feed card in the post kit look (brand/posts/kit.py, k2): the real photo on top with nothing over it,
    the price in the blue tag, the short title and the facts on white."""
    import cv2
    from PIL import Image
    sys.path.insert(0, os.path.join(ROOT, "brand", "posts"))
    import kit
    photo = Image.fromarray(cv2.cvtColor(photo_bgr, cv2.COLOR_BGR2RGB))
    lines = facts_lines(l) + ["", ""]
    img = kit.listing_post(photo, spec_title(l), price_text(l.get("price")), lines[0], facts2=lines[1])
    img.save(out_path, "JPEG", quality=90, optimize=True)


# ---------- wanted cards ----------

def page_live(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def wanted_link(w, source):
    """The category's seller page once it exists (Marketplace PR #261), else /sell-equipment."""
    tag = f"utm_source={source}&utm_medium=social&utm_campaign=post_wanted-{w['slug'] or w['key']}"
    if w.get("link_path"):
        # A fixed app page, e.g. /sell?import=craigslist (Sell form with the Craigslist paste box open).
        sep = "&" if "?" in w["link_path"] else "?"
        return f"{SITE}{w['link_path']}{sep}{tag}"
    if w.get("slug") and page_live(f"{SITE}/sell-equipment/{w['slug']}"):
        return f"{SITE}/sell-equipment/{w['slug']}?{tag}"
    return f"{SITE}/sell-equipment?{tag}"


# Alan 2026-11-10: wanted copy states buyer interest only. Saying searches came up
# empty, or that none / zero / one are listed, reads as "the marketplace is empty".
EMPTY_CLAIM = re.compile(r"(?i)\b(none|nothing|zero)\b|found no\b|came up empty|\bone (\w+ )?(is |are )?listed|no \w+ listed")


def empty_claim(w):
    text = " ".join([w.get("body", ""), w.get("card_sub", ""), " ".join(w.get("card", []))])
    return EMPTY_CLAIM.search(text)


def claim_holds(w, listings, complete):
    """Optional live-count check (no post uses one since 2026-11-10); True when a post has none."""
    c = w.get("check")
    if not c:
        return True
    if not complete:
        return False
    if c.get("category"):
        n = sum(1 for l in listings if l.get("category") == c["category"])
    else:
        word = c["title_has"].lower()
        n = sum(1 for l in listings if word in (l.get("title") or "").lower())
    return c.get("min_live", 0) <= n <= c["max_live"]


def wanted_captions(w, turn):
    cat = CATEGORY_TAGS.get(w.get("category"), ["#Equipment", "#SellUsedEquipment"])
    rot = (ROTATE_TAGS * 2)[(turn * 2) % len(ROTATE_TAGS):(turn * 2) % len(ROTATE_TAGS) + 2]
    # Comment "list" fires the Meta comment-to-DM automation (a tappable /c
    # link to the sell page); see IG_COMMENT_CTA in reels/post_reels.py.
    ig = (f"{w['body']}\n\nComment \"list\" and we'll message you the free listing link, "
          "or tap yardswaps.com/i in our bio. No listing fee, no cut of the sale.\n\n"
          f"{' '.join(cat + ['#UsedEquipment'] + rot)}\n\n{w['question']}")
    fb = (f"{w['body']}\n\nList it free: {wanted_link(w, 'facebook')}\n"
          "No listing fee, no cut of the sale.\n\n"
          f"{' '.join(cat + ['#YardSwaps', '#UsedEquipment'] + ROTATE_TAGS)}\n\n{w['question']}")
    return ig, fb


def render_wanted_card(w, out_path):
    """Text card in the post kit look (k2): the headline, one line, the wordmark and the link."""
    sys.path.insert(0, os.path.join(ROOT, "brand", "posts"))
    import kit
    img = kit.text_post(list(w["card"][:-1]), w["card"][-1].rstrip(".?!"), w["card_sub"],
                        "yardswaps.com/sell-equipment")
    img.save(out_path, "JPEG", quality=90, optimize=True)


def prep_wanted(listings, complete, queue, posted, dry):
    """Queue at most one wanted card; returns the new queue."""
    try:
        data = load(WANTED, {})
    except Exception as e:
        print(f"::warning::wanted.json unreadable: {e}")
        return queue
    posts = data.get("posts", [])
    if not posts:
        return queue
    age = (now() - parse_time(data["as_of"] + "T00:00:00Z")).days
    if age > WANTED_MAX_AGE_DAYS:
        print(f"::notice::wanted.json numbers are {age} days old; refresh them from the newest "
              "[GrowthDigest] before any more wanted cards go out.")
        return queue
    wanted_ids = {f"wanted-{w['key']}" for w in posts}
    cutoff = now() - dt.timedelta(days=WANTED_GAP_DAYS)
    if any(q["listing_id"] in wanted_ids and q["status"] in ("pending", "approved") for q in queue):
        print("A wanted card is already waiting.")
        return queue
    if any(p["listing_id"] in wanted_ids and p.get("status") == "posted" and parse_time(p["time"]) > cutoff
           for p in posted):
        print(f"A wanted card went out inside {WANTED_GAP_DAYS} days.")
        return queue
    last = {}
    for p in posted:
        if p["listing_id"] in wanted_ids and p.get("status") == "posted":
            last[p["listing_id"]] = max(last.get(p["listing_id"], ""), p["time"])
    repeat_cut = iso(now() - dt.timedelta(days=WANTED_REPEAT_DAYS))
    rejected = {q["listing_id"] for q in queue if q["status"] == "rejected" and q["listing_id"] in wanted_ids
                and q.get("updated", "") >= data["as_of"]}
    # File order first, then the longest-ago posted.
    for i, w in sorted(enumerate(posts), key=lambda iw: (f"wanted-{iw[1]['key']}" in last,
                                                         last.get(f"wanted-{iw[1]['key']}", ""), iw[0])):
        wid = f"wanted-{w['key']}"
        if last.get(wid, "") > repeat_cut or wid in rejected:
            continue
        if empty_claim(w):
            print(f"::warning::skip {wid}: its copy says '{empty_claim(w).group(0)}'; wanted posts state buyer interest only")
            continue
        if not claim_holds(w, listings, complete):
            print(f"  skip {wid}: its claim no longer holds on the live site")
            continue
        card = os.path.join(CARDS, f"{wid}.jpg")
        render_wanted_card(w, card)
        ig, fb = wanted_captions(w, len(queue))
        entry = {"listing_id": wid, "kind": "wanted", "title": " ".join(w["card"]),
                 "category": w.get("category"), "card": f"listings/cards/{wid}.jpg",
                 "ig_caption": ig, "fb_caption": fb, "status": "pending",
                 "added": iso(now()), "updated": iso(now())}
        print(f"  queued {wid}")
        print("    FB caption:\n" + "\n".join("      " + s for s in fb.splitlines()))
        return [q for q in queue if q["listing_id"] != wid] + [entry]
    print("No wanted post is due.")
    return queue


# ---------- prep ----------

# ---------- paying sellers first ----------

def feature_list():
    """GET /api/social-feature; an empty list (and a warning) when the app can't answer, so prep still runs."""
    try:
        data = json.loads(fetch(FEATURE_API, timeout=30))
        print(f"Feature list: {len(data.get('sellers') or [])} paying/trial seller(s), "
              f"{len(data.get('optedOut') or [])} opted out (as of {data.get('asOf')}).")
        return data
    except Exception as e:
        print(f"::warning::social-feature list unavailable ({e}); no paid cards today, nobody withdrawn.")
        return {"sellers": [], "optedOut": []}


def paid_log(event, dry=False, **fields):
    if dry:
        return
    log = load(PAID_LOG, [])
    log.append({"event": event, "time": iso(now()), **fields})
    save(PAID_LOG, log)


def last_paid_feature(queue):
    """Seller id -> time of their newest paid card that was queued or posted (rejected ones don't count)."""
    last = {}
    for q in queue:
        if q.get("feature") == "paid" and q["status"] in ("pending", "approved", "posted"):
            t = q.get("paid_at") or q.get("added", "")
            last[q.get("seller")] = max(last.get(q.get("seller"), ""), t)
    return last


def prep_paid(cv2, np, feature, listings, queue, posted, opted_out, dry=False):
    """Withdraw opted-out sellers' cards, then queue one paid card per due seller at the front."""
    changed = False
    for q in queue:
        if q.get("seller") in opted_out and q.get("kind") != "wanted":
            if not q.get("opted_out"):
                q["opted_out"] = True  # pickreal.py and the Reels poster skip these
                changed = True
            if q["status"] in ("pending", "approved"):
                q["status"] = "withdrawn"
                q["reason"] = "seller turned off Feature my listings in YardSwaps social posts"
                q["updated"] = iso(now())
                print(f"  withdrew {q['listing_id']}: seller opted out")
    sellers = [s for s in (feature.get("sellers") or []) if s.get("sellerId") not in opted_out]
    if not sellers:
        return queue, changed
    by_id = {l["id"]: l for l in listings}
    last_seller = last_paid_feature(queue)
    last_listing = {}
    for p in posted:
        if p.get("status") == "posted":
            last_listing[p["listing_id"]] = max(last_listing.get(p["listing_id"], ""), p["time"])
    rejected_at = {q["listing_id"]: q.get("updated", "") for q in queue if q["status"] == "rejected"}
    gap = dt.timedelta(days=PAID_GAP_DAYS)
    # Paying before trial (rank), then whoever was featured longest ago (never first).
    sellers.sort(key=lambda s: (s.get("rank", 9), last_seller.get(s["sellerId"], ""), s.get("since", "")))
    front = []
    for s in sellers:
        sid = s["sellerId"]
        if any(q.get("seller") == sid and q.get("feature") == "paid" and q["status"] in ("pending", "approved")
               for q in queue):
            continue  # already waiting
        if sid in last_seller and now() - parse_time(last_seller[sid]) < gap:
            continue
        # A regular card of theirs already waiting becomes the paid card.
        mine = next((q for q in queue if q.get("seller") == sid and q.get("kind") != "wanted"
                     and q["status"] in ("pending", "approved")), None)
        if mine:
            mine.update({"feature": "paid", "rank": s.get("rank"), "paid_at": iso(now())})
            queue.remove(mine)
            front.append(mine)
            paid_log("queued", dry, seller=sid, listing_id=mine["listing_id"], rank=s.get("rank"), title=mine.get("title"))
            print(f"  paid feature: {mine['listing_id']} ({mine.get('title')}) moved to the front")
            changed = True
            continue
        ids = [i for i in (s.get("listingIds") or [])
               if not (i in last_listing and now() - parse_time(last_listing[i]) < dt.timedelta(days=PAID_REFEATURE_DAYS))]
        ids.sort(key=lambda i: (i in last_listing, last_listing.get(i, "")))  # never featured first, keeps newest-first ties
        for lid in ids:
            l = by_id.get(lid)
            if l is None:
                try:
                    l = json.loads(fetch(f"{API}/{lid}", timeout=30)).get("listing")
                except Exception as e:
                    print(f"  paid feature: listing {lid} unavailable ({e})")
                    continue
            if not l or l.get("status") != "active":
                continue
            if lid in rejected_at and l.get("updatedAt", "") <= rejected_at[lid]:
                continue
            entry = build_card(cv2, np, l, len(queue) + len(front))
            if not entry:
                continue
            entry.update({"feature": "paid", "rank": s.get("rank"), "paid_at": iso(now())})
            queue = [q for q in queue if q["listing_id"] != lid]
            front.append(entry)
            paid_log("queued", dry, seller=sid, listing_id=lid, rank=s.get("rank"), title=entry.get("title"))
            print(f"  paid feature: queued {lid} ({entry['title']}) at the front")
            changed = True
            break
        else:
            print(f"  paid feature: no usable listing for seller {sid} today")
    return front + queue, changed


def prep(dry):
    import cv2
    import numpy as np
    queue = load(QUEUE, [])
    posted = load(POSTED, [])
    os.makedirs(CARDS, exist_ok=True)
    data = json.loads(fetch(f"{API}?sort=newest&limit=200"))
    got = data.get("listings", [])
    listings = [l for l in got if l.get("status") == "active"]
    complete = data.get("total") is not None and len(got) >= data["total"]
    print(f"API: {len(listings)} active listings (total {data.get('total')}).")
    before = len(queue)
    queue = prep_wanted(listings, complete, queue, posted, dry)
    wanted_added = len(queue) - before
    feature = feature_list()
    opted_out = set(feature.get("optedOut") or [])
    queue, paid_changed = prep_paid(cv2, np, feature, listings, queue, posted, opted_out, dry)
    # Wanted cards don't take a listing slot; paid cards come on top of it.
    waiting = [q for q in queue if q["status"] in ("pending", "approved") and q.get("kind") != "wanted"]
    if len([q for q in waiting if q.get("feature") != "paid"]) >= WAITING_MAX:
        print(f"{len(waiting)} listing cards already waiting.")
        if (wanted_added or paid_changed) and not dry:
            save(QUEUE, queue)
        return 0
    recent = {p["listing_id"] for p in posted if p.get("status") == "posted"
              and now() - parse_time(p["time"]) < dt.timedelta(days=REFEATURE_DAYS)}
    waiting_ids = {q["listing_id"] for q in waiting}
    # A rejected listing stays out until its seller edits it.
    rejected_at = {q["listing_id"]: q.get("updated", "") for q in queue if q["status"] == "rejected"}
    sellers_waiting = {q.get("seller") for q in waiting}
    added = 0
    # Never-featured first (newest first), then the longest-ago featured.
    last_feature = {}
    for p in posted:
        if p.get("status") == "posted":
            last_feature[p["listing_id"]] = max(last_feature.get(p["listing_id"], ""), p["time"])
    order = sorted(listings, key=lambda l: (l["id"] in last_feature, last_feature.get(l["id"], ""),
                                            -parse_time(l["createdAt"]).timestamp()))
    free_waiting = len([q for q in waiting if q.get("feature") != "paid"])
    for l in order:
        if free_waiting + added >= WAITING_MAX:
            break
        lid = l["id"]
        if lid in recent:
            continue
        if lid in waiting_ids:
            continue
        if lid in rejected_at and l.get("updatedAt", "") <= rejected_at[lid]:
            continue
        if l.get("sellerId") in sellers_waiting or l.get("sellerId") in opted_out:
            continue
        entry = build_card(cv2, np, l, len(queue))
        if not entry:
            continue
        queue = [q for q in queue if q["listing_id"] != lid] + [entry]
        sellers_waiting.add(l.get("sellerId"))
        added += 1
    if (added or wanted_added or paid_changed) and not dry:
        save(QUEUE, queue)
    print(f"Queued {added} listing card(s) and {wanted_added} wanted card(s) for review.")
    return 0


def build_card(cv2, np, l, turn):
    """Photo checks + card + cleaned photo for one listing; the queue entry, or None when no photo passes."""
    lid = l["id"]
    if re.match(r"\s*sale pending", l.get("title") or "", flags=re.I):
        print(f"  skip {lid}: sale pending")
        return None
    if not l.get("photoUrls"):
        return None
    if not safe_title(l):
        print(f"  skip {lid}: title carries contact details")
        return None
    chosen = None
    for u in l["photoUrls"][:PHOTOS_TRIED]:
        url = u if u.startswith("http") else SITE + u
        try:
            raw = fetch(url)
        except Exception as e:
            print(f"  {lid}: photo fetch failed {url}: {e}")
            continue
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if img is None or min(img.shape[:2]) < 400:
            continue
        nf = faces_in(img)
        if nf:
            print(f"  {lid}: {u} has {nf} face(s), trying the next photo")
            continue
        img2, nblur, ocr = blur_digit_text(img)
        chosen = (u, img2, nblur, ocr)
        break
    if not chosen:
        print(f"  skip {lid}: no usable photo")
        return None
    u, img2, nblur, ocr = chosen
    card = os.path.join(CARDS, f"{lid}.jpg")
    render_card(img2, l, card)
    # Nov 16 (Alan: new users list new items most days, add them to the promotion mix): keep the cleaned,
    # uncropped photo too, so the Motion batch can open a 10 s Short on the real item (whole item fitted,
    # same photo in the app walkthrough). Long side 1600 px, same face/digit checks as the card.
    os.makedirs(PHOTOS, exist_ok=True)
    h, w = img2.shape[:2]
    sc = min(1.0, 1600 / max(h, w))
    small = cv2.resize(img2, (int(w * sc), int(h * sc)), interpolation=cv2.INTER_AREA) if sc < 1 else img2
    cv2.imwrite(os.path.join(PHOTOS, f"{lid}.jpg"), small, [cv2.IMWRITE_JPEG_QUALITY, 88])
    # turn = every card ever queued: rotates the question and hashtags
    ig, fb = captions(l, turn)
    entry = {"listing_id": lid, "seller": l.get("sellerId"), "title": nice_title(l["title"]),
             "category": l.get("category"), "photo": u, "card": f"listings/cards/{lid}.jpg",
             "blurred_words": nblur, "ocr": ocr, "new": is_new(l),
             "photo_file": f"listings/photos/{lid}.jpg", "price": l.get("price"), "condition": l.get("condition"),
             "year": l.get("year"), "place": place(l), "created": l.get("createdAt"),
             "ig_caption": ig, "fb_caption": fb, "status": "pending",
             "added": iso(now()), "updated": iso(now())}
    print(f"  queued {lid}: {entry['title']} (photo {u}, blurred {nblur}, ocr {ocr})")
    print("    IG caption:\n" + "\n".join("      " + s for s in ig.splitlines()))
    return entry


# ---------- post ----------

def other_post_recent(token):
    """Minutes since the last post on IG/FB that isn't one of our Reels or listing posts."""
    ours = {(p.get("platform"), p.get("id")) for p in load(REELS_POSTED, []) + load(POSTED, [])}
    r = graph("GET", f"{IG_ID}/media", token, fields="id,timestamp", limit="3")
    for m in r.get("data", []):
        if ("instagram", m["id"]) not in ours:
            return (now() - parse_time(m["timestamp"])).total_seconds() / 60
    return None


def in_window(t):
    hm = (t.hour, t.minute)
    return hm >= POST_OPEN_UTC or t.hour < POST_CLOSE_UTC


def posted_today(posted):
    t = now()
    start = t.replace(hour=POST_OPEN_UTC[0], minute=0, second=0, microsecond=0)
    if t.hour < POST_CLOSE_UTC:
        start -= dt.timedelta(days=1)
    return any(p.get("status") == "posted" and not p.get("forced") and parse_time(p["time"]) >= start
               for p in posted)


def post(dry, force):
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    if not token:
        print("::notice::META_PAGE_TOKEN not set; nothing posted.")
        return 0
    queue = load(QUEUE, [])
    posted = load(POSTED, [])
    if not force:
        if not in_window(now()):
            print("Outside the 2:15 pm Central window; waiting.")
            return 0
        if posted_today(posted):
            print("Today's listing post is done.")
            return 0
    ready = [q for q in queue if q["status"] == "approved" and (not force or q["listing_id"] == force)]
    # Paying sellers' approved cards go first (Alan, 2026-11-16), then the oldest approved.
    pick = next((q for q in ready if q.get("feature") == "paid"), None) or (ready[0] if ready else None)
    if not pick:
        print("No approved card waiting.")
        return 0
    mins = other_post_recent(token)
    if not force and mins is not None and mins < CLEAR_MINUTES:
        print(f"Something else went up {mins:.0f} minutes ago; waiting for a later run.")
        return 0
    image_url = f"{RAW_BASE}/{pick['listing_id']}.jpg"
    print(f"Posting {pick['listing_id']}: {pick['title']}\n  image {image_url}")
    if dry:
        print(pick["ig_caption"])
        return 0
    try:
        fetch(image_url, timeout=30)
    except Exception as e:
        print(f"::warning::card not public yet at {image_url}: {e}")
        return 0
    results = []
    try:
        c = graph("POST", f"{IG_ID}/media", token, image_url=image_url, caption=pick["ig_caption"])
        for _ in range(12):
            st = graph("GET", c["id"], token, fields="status_code")
            if st.get("status_code") in ("FINISHED", None):
                break
            time.sleep(5)
        mid = graph("POST", f"{IG_ID}/media_publish", token, creation_id=c["id"])["id"]
        link = graph("GET", mid, token, fields="permalink").get("permalink", "")
        results.append({"platform": "instagram", "id": mid, "link": link, "status": "posted"})
        print(f"  Instagram: {link}")
    except GraphError as e:
        results.append({"platform": "instagram", "status": "failed", "error": str(e)[:400]})
        print(f"::warning::Instagram failed: {e}")
    try:
        r = graph("POST", f"{PAGE_ID}/photos", token, url=image_url, caption=pick["fb_caption"], published="true")
        pid = r.get("post_id") or r.get("id")
        results.append({"platform": "facebook", "id": pid, "link": f"https://www.facebook.com/{pid}", "status": "posted"})
        print(f"  Facebook: https://www.facebook.com/{pid}")
    except GraphError as e:
        results.append({"platform": "facebook", "status": "failed", "error": str(e)[:400]})
        print(f"::warning::Facebook failed: {e}")
    t = iso(now())
    for r in results:
        posted.append({"listing_id": pick["listing_id"], "time": t, "forced": bool(force), **r})
    if any(r["status"] == "posted" for r in results):
        pick["status"] = "posted"
        pick["updated"] = t
    save(POSTED, posted)
    save(QUEUE, queue)
    if pick.get("feature") == "paid" and any(r["status"] == "posted" for r in results):
        paid_log("posted", seller=pick.get("seller"), listing_id=pick["listing_id"], rank=pick.get("rank"),
                 title=pick.get("title"), links=[r.get("link") for r in results if r["status"] == "posted"])
    return 0 if any(r["status"] == "posted" for r in results) else 1


def main():
    mode = (os.environ.get("MODE") or "prep").strip()
    dry = os.environ.get("DRY_RUN") == "1"
    if mode == "prep":
        return prep(dry)
    if mode == "post":
        return post(dry, (os.environ.get("LISTING_ID") or "").strip() or None)
    print(f"unknown MODE {mode}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
