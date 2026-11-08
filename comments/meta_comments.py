#!/usr/bin/env python3
"""Daily comment inbox for Instagram and Facebook (comments.yml).

The daily comment-reply task (a Claude scheduled task) can't hold the Meta
token, so this script does the Meta side and the task does the writing:

  fetch  Read new viewer comments on our Instagram posts and Facebook Page
         posts and Reels, and write comments/inbox.json. A comment is "new"
         when nobody from YardSwaps has answered it and it isn't in
         comments/seen.json. Read-only.
  post   Post the replies the task wrote to comments/outbox.json, record each
         in comments/seen.json, and empty the outbox. A reply Meta refuses
         stays in the outbox with its error, so the task can fall back
         (Instagram through Zapier, Facebook to the digest).
  probe  Read-only check of what the token can do (scopes, one comment read
         per platform, whether Buffer's API has comments). Pull requests run
         this, so a test run changes nothing.

Standard library only. Env: META_PAGE_TOKEN (secret), FB_PAGE_ID,
IG_USER_ID, BUFFER_API_KEY (probe only), MODE.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com/v23.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "comments")
INBOX = os.path.join(DIR, "inbox.json")
OUTBOX = os.path.join(DIR, "outbox.json")
SEEN = os.path.join(DIR, "seen.json")
POSTED = os.path.join(ROOT, "reels", "posted.json")

OUR_IG_USERNAMES = {"yardswaps"}
LOOKBACK_DAYS = 30          # posts older than this aren't checked for new comments
MAX_REPLY_CHARS = 900       # Instagram allows 2,200, but a reply should be short anyway

# What a reply needs, per Meta's docs. Used to tell the task where it can post.
NEEDS = {
    "instagram": {"instagram_manage_comments"},
    "facebook": {"pages_manage_engagement"},
}


class GraphError(Exception):
    pass


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(s):
    s = (s or "").replace("Z", "+00:00")
    if len(s) > 5 and s[-5] in "+-" and s[-3] != ":":
        s = s[:-2] + ":" + s[-2:]
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def call(method, url, params=None, data=None, headers=None, timeout=60):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        raise GraphError(f"{method} {url.split('?')[0].replace(GRAPH, '')} -> {e.code}: {raw[:400]}")
    except urllib.error.URLError as e:
        raise GraphError(f"{method} {url.split('?')[0]} -> {e}")


def graph(method, path, token, **fields):
    if method == "GET":
        return call("GET", f"{GRAPH}/{path}", params={**fields, "access_token": token})
    return call("POST", f"{GRAPH}/{path}", data={**fields, "access_token": token})


def pages(first, token, limit=6):
    """Follow paging.next up to `limit` pages."""
    out, res = [], first
    for _ in range(limit):
        out += res.get("data", [])
        nxt = res.get("paging", {}).get("next")
        if not nxt:
            break
        res = call("GET", nxt)
    return out


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def first_line(s, n=90):
    s = (s or "").strip().splitlines()[0] if (s or "").strip() else ""
    return s[:n]


def scopes(token):
    try:
        d = graph("GET", "debug_token", token, input_token=token).get("data", {})
    except GraphError as e:
        return None, str(e)
    return set(d.get("scopes") or []), None


# ---------- Instagram ----------

def ig_items(token, ig_id, seen, since, errors):
    items = []
    try:
        media = pages(graph("GET", f"{ig_id}/media", token, limit="50",
                            fields="id,caption,timestamp,permalink,comments_count,media_product_type"), token, 2)
    except GraphError as e:
        errors.append(f"instagram media: {e}")
        return items
    for m in media:
        t = parse_time(m.get("timestamp"))
        if not m.get("comments_count") or (t and t < since):
            continue
        try:
            comments = pages(graph("GET", f"{m['id']}/comments", token, limit="50",
                                   fields="id,text,username,timestamp,like_count,replies{id,text,username,timestamp}"), token, 3)
        except GraphError as e:
            errors.append(f"instagram comments {m['id']}: {e}")
            continue
        post = {"media_id": m["id"], "permalink": m.get("permalink"),
                "post": first_line(m.get("caption")), "type": m.get("media_product_type")}
        for c in comments:
            replies = sorted((c.get("replies") or {}).get("data", []), key=lambda r: r.get("timestamp", ""))
            ours = [r for r in replies if (r.get("username") or "").lower() in OUR_IG_USERNAMES]
            last_ours = ours[-1]["timestamp"] if ours else ""
            if (c.get("username") or "").lower() not in OUR_IG_USERNAMES and not ours and c["id"] not in seen:
                items.append({"platform": "instagram", "comment_id": c["id"], "reply_to": c["id"],
                              "author": c.get("username"), "text": c.get("text"), "time": c.get("timestamp"),
                              "likes": c.get("like_count", 0), **post})
            # Follow-ups under a thread we already answered: someone wrote after our last reply.
            for r in replies:
                if (r.get("username") or "").lower() in OUR_IG_USERNAMES or r["id"] in seen:
                    continue
                if ours and r.get("timestamp", "") > last_ours:
                    items.append({"platform": "instagram", "comment_id": r["id"], "reply_to": c["id"],
                                  "author": r.get("username"), "text": r.get("text"), "time": r.get("timestamp"),
                                  "thread": [{"author": x.get("username"), "text": x.get("text")} for x in [c] + replies
                                             if x.get("timestamp", "") <= r.get("timestamp", "")],
                                  **post})
    return items


# ---------- Facebook ----------

def fb_objects(token, page_id, since, errors):
    """Page posts (Just listed cards, links) plus our Reels from posted.json."""
    objs = {}
    try:
        for p in pages(graph("GET", f"{page_id}/published_posts", token, limit="50",
                             fields="id,message,created_time,permalink_url"), token, 2):
            t = parse_time(p.get("created_time"))
            if t and t >= since:
                objs[p["id"]] = {"post": first_line(p.get("message")), "permalink": p.get("permalink_url"),
                                 "type": "POST"}
    except GraphError as e:
        errors.append(f"facebook posts: {e}")
    try:
        for p in pages(graph("GET", f"{page_id}/video_reels", token, limit="50",
                             fields="id,description,created_time,permalink_url"), token, 2):
            t = parse_time(p.get("created_time"))
            if t and t >= since:
                objs.setdefault(p["id"], {"post": first_line(p.get("description")),
                                          "permalink": "https://www.facebook.com" + p["permalink_url"]
                                          if (p.get("permalink_url") or "").startswith("/") else p.get("permalink_url"),
                                          "type": "REELS"})
    except GraphError as e:
        errors.append(f"facebook reels list: {str(e)[:200]}")
    for p in load(POSTED, []):
        if p.get("platform") != "facebook" or p.get("status") != "posted" or not p.get("id"):
            continue
        t = parse_time(p.get("time"))
        if t and t >= since:
            objs.setdefault(p["id"], {"post": p.get("slug"), "permalink": p.get("url"), "type": "REELS"})
    return objs


def fb_items(token, page_id, seen, since, errors):
    items = []
    refused = []  # one line for "missing permission" instead of one per post
    for oid, meta in fb_objects(token, page_id, since, errors).items():
        try:
            head = graph("GET", oid, token, fields="comments.summary(true).limit(0)")
            if not head.get("comments", {}).get("summary", {}).get("total_count"):
                continue
            comments = pages(graph("GET", f"{oid}/comments", token, limit="50", filter="toplevel",
                                   fields="id,message,from,created_time,like_count,comments{id,message,from,created_time}"), token, 3)
        except GraphError as e:
            if "(#10)" in str(e):
                refused.append(oid)
            else:
                errors.append(f"facebook comments {oid}: {str(e)[:300]}")
            continue
        for c in comments:
            frm = c.get("from") or {}
            replies = sorted((c.get("comments") or {}).get("data", []), key=lambda r: r.get("created_time", ""))
            ours = [r for r in replies if (r.get("from") or {}).get("id") == page_id]
            last_ours = ours[-1]["created_time"] if ours else ""
            if frm.get("id") != page_id and not ours and c["id"] not in seen:
                items.append({"platform": "facebook", "comment_id": c["id"], "reply_to": c["id"],
                              # `from` is empty without pages_read_user_content; the text still comes back.
                              "author": frm.get("name"), "text": c.get("message"), "time": c.get("created_time"),
                              "likes": c.get("like_count", 0), "media_id": oid, **meta})
            for r in replies:
                if (r.get("from") or {}).get("id") == page_id or r["id"] in seen:
                    continue
                if ours and r.get("created_time", "") > last_ours:
                    items.append({"platform": "facebook", "comment_id": r["id"], "reply_to": c["id"],
                                  "author": (r.get("from") or {}).get("name"), "text": r.get("message"),
                                  "time": r.get("created_time"), "media_id": oid, **meta,
                                  "thread": [{"author": (x.get("from") or {}).get("name"), "text": x.get("message")}
                                             for x in [c] + replies if x.get("created_time", "") <= r.get("created_time", "")]})
    if refused:
        errors.append(f"facebook: comments on {len(refused)} page posts not readable; the token needs "
                      "pages_read_user_content (Reels comments still read)")
    return items


# ---------- modes ----------

def do_fetch(token, page_id, ig_id):
    seen = load(SEEN, {})
    since = now() - dt.timedelta(days=LOOKBACK_DAYS)
    errors = []
    sc, sc_err = scopes(token)
    if sc_err:
        errors.append(f"debug_token: {sc_err}")
    items = ig_items(token, ig_id, seen, since, errors) + fb_items(token, page_id, seen, since, errors)
    items.sort(key=lambda x: x.get("time") or "")
    inbox = {
        "fetched_at": iso(now()),
        "can_reply": {p: (sc is not None and need <= sc) for p, need in NEEDS.items()},
        "scopes": sorted(sc or []),
        "errors": errors,
        "items": items,
    }
    save(INBOX, inbox)
    print(f"{len(items)} new comments (instagram {sum(i['platform'] == 'instagram' for i in items)}, "
          f"facebook {sum(i['platform'] == 'facebook' for i in items)}); can_reply {inbox['can_reply']}")
    for e in errors:
        print(f"::warning::{e[:300]}")


def do_post(token):
    out = load(OUTBOX, [])
    if not out:
        print("outbox empty")
        return
    seen = load(SEEN, {})
    keep = []
    for r in out:
        cid, text, plat = r.get("reply_to") or r.get("comment_id"), (r.get("reply") or "").strip(), r.get("platform")
        if r.get("skip"):  # the task decided not to answer (spam, needs Alan): just remember it
            seen[r["comment_id"]] = {"status": "skipped", "why": r.get("why", ""), "at": iso(now())}
            continue
        if not cid or not text or plat not in NEEDS:
            r["error"] = "missing comment id, reply text or platform"
            keep.append(r)
            continue
        try:
            if plat == "instagram":
                res = graph("POST", f"{cid}/replies", token, message=text[:MAX_REPLY_CHARS])
            else:
                res = graph("POST", f"{cid}/comments", token, message=text[:MAX_REPLY_CHARS])
            seen[r["comment_id"]] = {"status": "replied", "reply_id": res.get("id"), "at": iso(now()),
                                     "platform": plat, "reply": text}
            print(f"replied on {plat} to {r['comment_id']}")
        except GraphError as e:
            r["error"] = str(e)[:300]
            r["tries"] = r.get("tries", 0) + 1
            print(f"::warning::{plat} reply to {r['comment_id']} refused: {r['error']}")
            if r["tries"] < 2:
                keep.append(r)
            else:
                seen[r["comment_id"]] = {"status": "failed", "error": r["error"], "at": iso(now()),
                                         "platform": plat, "reply": text}
    save(SEEN, seen)
    save(OUTBOX, keep)


def do_probe(token, page_id, ig_id):
    sc, err = scopes(token)
    print("scopes:", sorted(sc) if sc is not None else err)
    for p, need in NEEDS.items():
        print(f"can reply on {p}: {sc is not None and need <= sc} (needs {', '.join(sorted(need))})")
    since = now() - dt.timedelta(days=LOOKBACK_DAYS)
    errors = []
    ig = ig_items(token, ig_id, {}, since, errors)
    fb = fb_items(token, page_id, {}, since, errors)
    print(f"read: instagram {len(ig)} unanswered, facebook {len(fb)} unanswered")
    fb_named = sum(1 for i in fb if i.get("author"))
    print(f"facebook comments with a commenter name: {fb_named} of {len(fb)}")
    for e in errors:
        print("error:", e[:300])
    key = os.environ.get("BUFFER_API_KEY")
    if key:
        try:
            res = call("POST", "https://api.buffer.com", data=json.dumps(
                {"query": "{ __schema { types { name } queryType { fields { name } } } }"}).encode(),
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            names = [t["name"] for t in res.get("data", {}).get("__schema", {}).get("types", [])]
            q = [f["name"] for f in res.get("data", {}).get("__schema", {}).get("queryType", {}).get("fields", [])]
            print("buffer comment types:", [n for n in names if "omment" in n or "ngage" in n] or "none")
            print("buffer query fields:", q)
        except Exception as e:  # noqa: BLE001 - probe only
            print("buffer probe:", str(e)[:300])


def main():
    mode = (os.environ.get("MODE") or "fetch").strip()
    token = os.environ.get("META_PAGE_TOKEN")
    if not token:
        print("::notice::META_PAGE_TOKEN not set; nothing to do")
        return 0
    page_id = os.environ.get("FB_PAGE_ID") or "1291163214083476"
    ig_id = os.environ.get("IG_USER_ID") or "17841429324062623"
    if mode == "fetch":
        do_fetch(token, page_id, ig_id)
    elif mode == "post":
        do_post(token)
    elif mode == "probe":
        do_probe(token, page_id, ig_id)
    else:
        print(f"unknown MODE {mode}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
