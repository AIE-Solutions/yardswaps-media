"""Keep the YardSwaps Facebook Page and Instagram profile in line with profiles.json.

MODE=check  reads both profiles and reports any field that differs (no writes).
MODE=apply  also re-applies the Facebook Page intro, description and website.
            Instagram's bio, name and link cannot be set through the Graph API,
            so Instagram drift is reported only.

Writes profiles/status.json and a table to the job summary. Exits 0 even on
drift, so the weekly run never blocks other work; read status.json instead.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reels"))
from post_reels import GraphError, graph, iso, now  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_ID = "1291163214083476"
IG_ID = "17841429324062623"


def urls(s):
    return sorted(u.rstrip("/").lower() for u in re.findall(r"https?://[^\s,]+", s or ""))


def same(field, live, want):
    if field == "website":
        return urls(live) == urls(want)
    return norm(live) == norm(want)


def norm(s):
    return " ".join((s or "").replace("\r", "").split()).rstrip("/").lower()


def main():
    token = os.environ.get("META_PAGE_TOKEN", "")
    mode = os.environ.get("MODE", "check")
    if not token:
        sys.exit("META_PAGE_TOKEN is not set")
    want = json.load(open(os.path.join(HERE, "profiles.json"), encoding="utf-8"))
    fb_want = want["platforms"]["facebook"]
    ig_want = want["platforms"]["instagram"]
    fb_target = {
        "about": fb_want["intro"],
        "description": want["long_about"] + fb_want["link"],
        # The Page keeps several websites; the short link goes first, then both stores.
        "website": " ".join([fb_want["link"], want["app_links"]["ios"], want["app_links"]["android"]]),
    }
    rows, status = [], {"checked": iso(now()), "mode": mode, "facebook": {}, "instagram": {}}

    fb = graph("GET", PAGE_ID, token, fields="name,username,about,description,website,emails,link,picture{url}")
    fixes = {}
    for k, v in fb_target.items():
        ok = same(k, fb.get(k), v)
        status["facebook"][k] = {"ok": ok, "live": fb.get(k)}
        if not ok:
            fixes[k] = v
    status["facebook"]["name"] = {"ok": fb.get("name") == want["name"], "live": fb.get("name")}
    status["facebook"]["username"] = {"ok": bool(fb.get("username")), "live": fb.get("username")}
    status["facebook"]["picture"] = (fb.get("picture") or {}).get("data", {}).get("url")
    if fixes and mode == "apply":
        try:
            r = graph("POST", PAGE_ID, token, **fixes)
            for k in fixes:
                status["facebook"][k]["applied"] = bool(r.get("success", True))
        except GraphError as e:
            status["facebook"]["apply_error"] = str(e)[:400]
            print(f"::warning::Facebook Page update refused: {e}")

    ig = graph("GET", IG_ID, token, fields="username,name,biography,website,profile_picture_url")
    for k, v in (("name", ig_want["display_name"]), ("biography", ig_want["bio"]), ("website", ig_want["link"])):
        status["instagram"][k] = {"ok": same(k, ig.get(k), v), "live": ig.get(k)}
    status["instagram"]["username"] = ig.get("username")
    status["instagram"]["picture"] = ig.get("profile_picture_url")

    for net in ("facebook", "instagram"):
        for k, v in status[net].items():
            if isinstance(v, dict):
                mark = "fixed" if v.get("applied") else ("ok" if v["ok"] else "DIFFERS")
                live = (v.get("live") or "(empty)").replace("\n", " / ")[:90]
                rows.append(f"| {net} | {k} | {mark} | {live} |")
    table = "| Platform | Field | State | Live value |\n|---|---|---|---|\n" + "\n".join(rows)
    if status["facebook"].get("apply_error"):
        table += f"\n\nFacebook refused the update: {status['facebook']['apply_error']}"
    print(table)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Profile check\n\n" + table + "\n")
    with open(os.path.join(HERE, "status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
