#!/usr/bin/env python3
"""One-off IMAGE post to Instagram + Facebook (feed) and both Stories.

Not the Reels queue: reels.yml dispatches this when image_slug is set. The
entry comes from reels/images.json; images are served from the public repo at
raw.githubusercontent.com pinned to GITHUB_SHA (the Graph API fetches by URL).
Log: reels/images-posted.json. One attempt per platform; a failure on one
platform does not stop the others.

Env: META_PAGE_TOKEN (required), IMAGE_SLUG, PLATFORMS (default
instagram,facebook,instagram_story,facebook_story), DRY_RUN=1 prints only,
FB_PAGE_ID / IG_USER_ID defaults as in post_reels.py.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com/v23.0"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG = os.path.join(HERE, "images-posted.json")


class GraphError(Exception):
    pass


def call(method, url, params=None, data=None, timeout=120):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data
    req = urllib.request.Request(url, data=body, method=method)
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


def raw_url(path):
    repo = os.environ.get("GITHUB_REPOSITORY") or "AIE-Solutions/yardswaps-media"
    sha = os.environ.get("GITHUB_SHA") or "main"
    return f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"


def wait_container(token, cid):
    for _ in range(30):
        st = graph("GET", cid, token, fields="status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise GraphError(f"Instagram container failed: {st}")
        time.sleep(5)
    raise GraphError("Instagram container still processing after 150 s")


def ig_feed(token, ig_id, url, caption):
    cid = graph("POST", f"{ig_id}/media", token, image_url=url, caption=caption)["id"]
    wait_container(token, cid)
    mid = graph("POST", f"{ig_id}/media_publish", token, creation_id=cid)["id"]
    link = ""
    try:
        link = graph("GET", mid, token, fields="permalink").get("permalink", "")
    except GraphError:
        pass
    return mid, link


def ig_story(token, ig_id, url):
    cid = graph("POST", f"{ig_id}/media", token, media_type="STORIES", image_url=url)["id"]
    wait_container(token, cid)
    return graph("POST", f"{ig_id}/media_publish", token, creation_id=cid)["id"], ""


def fb_feed(token, page_id, url, caption):
    r = graph("POST", f"{page_id}/photos", token, url=url, message=caption)
    pid = r.get("post_id") or r.get("id")
    return pid, f"https://www.facebook.com/{pid}" if pid else ""


def fb_story(token, page_id, url):
    photo = graph("POST", f"{page_id}/photos", token, url=url, published="false")["id"]
    r = graph("POST", f"{page_id}/photo_stories", token, photo_id=photo)
    return r.get("post_id") or r.get("id") or photo, ""


def main():
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    slug = (os.environ.get("IMAGE_SLUG") or "").strip()
    dry = os.environ.get("DRY_RUN") == "1"
    page_id = os.environ.get("FB_PAGE_ID") or "1291163214083476"
    ig_id = os.environ.get("IG_USER_ID") or "17841429324062623"
    platforms = [p.strip() for p in (os.environ.get("PLATFORMS") or "instagram,facebook,instagram_story,facebook_story").split(",") if p.strip()]
    platforms = [p for p in platforms if p != "threads"]
    if not slug:
        sys.exit("IMAGE_SLUG is empty")
    entries = json.load(open(os.path.join(HERE, "images.json"), encoding="utf-8"))["images"]
    e = next((x for x in entries if x["slug"] == slug), None)
    if not e:
        sys.exit(f"no image entry {slug!r} in reels/images.json")
    for k in ("feed", "story"):
        if not os.path.exists(os.path.join(ROOT, e[k])):
            sys.exit(f"missing file {e[k]}")
    feed_url, story_url = raw_url(e["feed"]), raw_url(e["story"])
    log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
    done = {r["platform"] for r in log if r.get("slug") == slug and r.get("ok")}
    print(f"image {slug}: feed {feed_url}\n  story {story_url}\n  platforms {platforms}\n  already posted: {sorted(done) or 'none'}")
    if dry:
        print("IG caption:\n" + e["ig_caption"] + "\n\nFB caption:\n" + e["fb_caption"])
        return
    if not token:
        sys.exit("META_PAGE_TOKEN missing")
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    results = []
    for p in platforms:
        if p in done:
            print(f"  {p}: already posted, skipping")
            continue
        try:
            if p == "instagram":
                mid, link = ig_feed(token, ig_id, feed_url, e["ig_caption"])
            elif p == "facebook":
                mid, link = fb_feed(token, page_id, feed_url, e["fb_caption"])
            elif p == "instagram_story":
                mid, link = ig_story(token, ig_id, story_url)
            elif p == "facebook_story":
                mid, link = fb_story(token, page_id, story_url)
            else:
                print(f"  {p}: unknown platform, skipping")
                continue
            print(f"  {p}: posted {mid} {link}")
            log.append({"slug": slug, "platform": p, "ok": True, "id": mid, "link": link, "time": now})
            results.append(f"{p}: ok {link}".strip())
        except GraphError as ex:
            print(f"  {p}: FAILED {ex}")
            log.append({"slug": slug, "platform": p, "ok": False, "error": str(ex)[:400], "time": now})
            results.append(f"{p}: FAILED")
    json.dump(log, open(LOG, "w", encoding="utf-8"), indent=1)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"## Image post {slug}\n" + "\n".join(f"- {r}" for r in results) + "\n")
    if any(r.endswith("FAILED") for r in results) and not any("ok" in r for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
