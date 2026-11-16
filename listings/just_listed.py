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

Seller names, phone numbers and descriptions never go into a caption or a
card: only the title, price, year/hours/miles, city and category.

Env:
  MODE             prep | post
  META_PAGE_TOKEN  Page token (same secret as the Reels poster); post only
  DRY_RUN          "1" = render and print, write and post nothing
  LISTINGS_API     default https://www.yardswaps.com/api/listings
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
POSTED = os.path.join(HERE, "posted.json")
WANTED = os.path.join(HERE, "wanted.json")
CARDS = os.path.join(HERE, "cards")
FONTS = os.path.join(HERE, "fonts")

SITE = "https://www.yardswaps.com"
API = os.environ.get("LISTINGS_API") or f"{SITE}/api/listings"
RAW_BASE = os.environ.get("RAW_BASE") or \
    "https://raw.githubusercontent.com/AIE-Solutions/yardswaps-media/main/listings/cards"
PAGE_ID = os.environ.get("FB_PAGE_ID") or "1291163214083476"
IG_ID = os.environ.get("IG_USER_ID") or "17841429324062623"
UA = "yardswaps-just-listed/1.0 (https://github.com/AIE-Solutions/yardswaps-media)"

WAITING_MAX = 3          # pending + approved cards kept ready
NEW_DAYS = 7             # "Just listed" label inside this many days, else "For sale"
REFEATURE_DAYS = 45      # a listing can be featured again after this
PHOTOS_TRIED = 4         # photos checked per listing before giving up on it
# One post a day, 2:15 pm Central (20:15 UTC in winter): 100+ minutes after
# HeyCatch's 12:33 pm post and 2+ hours before the 4:30 pm Reel.
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


def render_card(photo_bgr, l, out_path):
    import cv2
    from PIL import Image, ImageDraw
    W, H, PH = 1080, 1350, 1000
    img = Image.new("RGB", (W, H), BG)
    rgb = cv2.cvtColor(photo_bgr, cv2.COLOR_BGR2RGB)
    ph = Image.fromarray(rgb)
    # Cover-crop the photo into the top 1080x1000.
    s = max(W / ph.width, PH / ph.height)
    ph = ph.resize((int(ph.width * s + 0.5), int(ph.height * s + 0.5)), Image.LANCZOS)
    left, top = (ph.width - W) // 2, (ph.height - PH) // 2
    img.paste(ph.crop((left, top, left + W, top + PH)), (0, 0))
    d = ImageDraw.Draw(img)
    pad = 56
    label = "JUST LISTED" if is_new(l) else "FOR SALE ON YARDSWAPS"
    lf = font("SpaceGrotesk.ttf", 30, b"Bold")
    # Label pill on the photo, top-left.
    tw = d.textlength(label, font=lf)
    d.rounded_rectangle((pad - 4, 44, pad + tw + 40, 44 + 58), radius=29, fill=BLUE)
    d.text((pad + 18, 44 + 12), label, font=lf, fill=(255, 255, 255))
    tf = font("SpaceGrotesk.ttf", 50, b"Bold")
    lines = wrap(d, nice_title(l["title"]), tf, W - 2 * pad, 2)
    y = PH + 40
    for line in lines:
        d.text((pad, y), line, font=tf, fill=SLATE)
        y += 62
    y += 14
    pf = font("SpaceGrotesk.ttf", 44, b"Bold")
    pt = price_text(l.get("price"))
    d.text((pad, y), pt, font=pf, fill=BLUE)
    rest = " · ".join(facts(l).split(" · ")[1:])
    if rest:
        rf = font("Inter.ttf", 32, b"Medium")
        x = pad + d.textlength(pt, font=pf) + 24
        rest_lines = wrap(d, rest, rf, W - pad - x, 1)
        d.text((x, y + 8), rest_lines[0], font=rf, fill=GRAY)
    ff = font("Inter.ttf", 28, b"Medium")
    foot = "Free to list. Free to browse. yardswaps.com"
    d.text((pad, H - 64), foot, font=ff, fill=GRAY)
    img.save(out_path, "JPEG", quality=88, optimize=True)


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
    from PIL import Image, ImageDraw
    W, H, pad = 1080, 1350, 72
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    lf = font("SpaceGrotesk.ttf", 30, b"Bold")
    label = "WANTED ON YARDSWAPS"
    tw = d.textlength(label, font=lf)
    d.rounded_rectangle((pad - 4, 96, pad + tw + 40, 96 + 58), radius=29, fill=BLUE)
    d.text((pad + 18, 96 + 12), label, font=lf, fill=(255, 255, 255))
    hf = font("SpaceGrotesk.ttf", 104, b"Bold")
    sf = font("Inter.ttf", 44, b"Medium")
    sub = wrap(d, w["card_sub"], sf, W - 2 * pad, 3)
    block = 124 * len(w["card"]) + 40 + 60 * len(sub)
    y = 154 + (H - 210 - 154 - block) // 2  # centred between the label and the footer rule
    for i, line in enumerate(w["card"]):
        d.text((pad, y), line, font=hf, fill=BLUE if i == len(w["card"]) - 1 else SLATE)
        y += 124
    y += 40
    for line in sub:
        d.text((pad, y), line, font=sf, fill=GRAY)
        y += 60
    d.rectangle((pad, H - 210, W - pad, H - 206), fill=(216, 216, 218))
    ff = font("SpaceGrotesk.ttf", 40, b"Bold")
    d.text((pad, H - 170), "Free to list. Local pickup.", font=ff, fill=SLATE)
    d.text((pad, H - 110), "yardswaps.com", font=ff, fill=BLUE)
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
    # Wanted cards don't take a listing slot.
    waiting = [q for q in queue if q["status"] in ("pending", "approved") and q.get("kind") != "wanted"]
    if len(waiting) >= WAITING_MAX:
        print(f"{len(waiting)} listing cards already waiting.")
        if wanted_added and not dry:
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
    for l in order:
        if len(waiting) + added >= WAITING_MAX:
            break
        lid = l["id"]
        if lid in recent:
            continue
        if lid in waiting_ids:
            continue
        if lid in rejected_at and l.get("updatedAt", "") <= rejected_at[lid]:
            continue
        if l.get("sellerId") in sellers_waiting:
            continue
        if not l.get("photoUrls"):
            continue
        if not safe_title(l):
            print(f"  skip {lid}: title carries contact details")
            continue
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
            continue
        u, img2, nblur, ocr = chosen
        card = os.path.join(CARDS, f"{lid}.jpg")
        render_card(img2, l, card)
        turn = len(queue)  # every card ever queued: rotates the question and hashtags
        ig, fb = captions(l, turn)
        entry = {"listing_id": lid, "seller": l.get("sellerId"), "title": nice_title(l["title"]),
                 "category": l.get("category"), "photo": u, "card": f"listings/cards/{lid}.jpg",
                 "blurred_words": nblur, "ocr": ocr, "new": is_new(l),
                 "ig_caption": ig, "fb_caption": fb, "status": "pending",
                 "added": iso(now()), "updated": iso(now())}
        print(f"  queued {lid}: {entry['title']} (photo {u}, blurred {nblur}, ocr {ocr})")
        print("    IG caption:\n" + "\n".join("      " + s for s in ig.splitlines()))
        queue = [q for q in queue if q["listing_id"] != lid] + [entry]
        sellers_waiting.add(l.get("sellerId"))
        added += 1
    if (added or wanted_added) and not dry:
        save(QUEUE, queue)
    print(f"Queued {added} listing card(s) and {wanted_added} wanted card(s) for review.")
    return 0


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
    pick = next((q for q in queue if q["status"] == "approved" and (not force or q["listing_id"] == force)), None)
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
