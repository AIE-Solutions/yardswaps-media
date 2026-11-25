"""Apply the Studio deck decisions (yardswaps.com/admin/studio) to reels/library.json.

Our version of HeyCatch's daily swipe deck. make_pov.py adds every new clip with
"review": "pending" and "hold": true, so no poster takes it. An admin approves,
skips or edits it on /admin/studio; this script, run by the "Studio deck sync"
scheduled task, reads those decisions (GET https://www.yardswaps.com/api/agent/studio,
saved to a file by the task) and applies them:

  approved  -> hold off, review "approved", caption / question edits applied.
               A changed on-screen line sets "rerender_hook": the next make_pov.py
               run makes the video again with it and only then lets it post.
  skipped   -> hold on, review "skipped": never posts.
  no answer -> once AUTO_APPROVE_HOURS have passed since the clip was made, review
               "auto" and hold off, so posting never stalls while the owner is busy.

Only clips with "studio": true are touched, and a clip that already posted keeps
its post (a skip after that only stops repeats).

    python3 studio/sync_deck.py decisions.json           # apply and save
    DRY_RUN=1 python3 studio/sync_deck.py decisions.json # print what would change

Prints one summary line (approved, skipped, auto, edited, re-render) for the
task's heartbeat. Writes studio/deck-state.json with the time of the last sync.
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIBRARY = os.path.join(ROOT, "reels", "library.json")
STATE = os.path.join(HERE, "deck-state.json")
AUTO_APPROVE_HOURS = 24


def now():
    return dt.datetime.now(dt.timezone.utc)


def made_at(v):
    raw = v.get("made") or (f"{v['added']}T12:00:00+00:00" if v.get("added") else "")
    try:
        d = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def apply(videos, decisions, at=None, auto_hours=AUTO_APPROVE_HOURS):
    """Mutates videos in place; returns the counts."""
    at = at or now()
    counts = {"approved": 0, "skipped": 0, "auto": 0, "edited": 0, "rerender": 0}
    by_slug = {d["slug"]: d for d in decisions if isinstance(d, dict) and d.get("slug")}
    for v in videos:
        if not v.get("studio"):
            continue
        d = by_slug.get(v["slug"])
        if d and d.get("decision") == "skipped":
            if v.get("review") != "skipped" or not v.get("hold"):
                counts["skipped"] += 1
            v["review"], v["hold"] = "skipped", True
            v.pop("rerender_hook", None)
            continue
        if d and d.get("decision") == "approved":
            changed = v.get("review") not in ("approved",)
            for key, field in (("caption", "body"), ("question", "question")):
                if d.get(key) and d[key] != v.get(field):
                    v[field] = d[key]
                    counts["edited"] += 1
                    changed = True
            hook = (d.get("hook") or "").strip()
            if hook and hook != v.get("title") and hook != v.get("rerender_hook"):
                v["rerender_hook"] = hook
                counts["rerender"] += 1
                changed = True
            v["review"] = "approved"
            # a clip waiting for its new on-screen line stays held until make_pov.py re-renders it
            v["hold"] = bool(v.get("rerender_hook"))
            if changed:
                counts["approved"] += 1
            continue
        if v.get("review") == "pending":
            made = made_at(v)
            if made and at - made >= dt.timedelta(hours=auto_hours):
                v["review"], v["hold"] = "auto", False
                counts["auto"] += 1
    return counts


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: sync_deck.py decisions.json")
    data = json.load(open(sys.argv[1]))
    decisions = data.get("decisions", []) if isinstance(data, dict) else data
    hours = int((data.get("autoApproveHours") if isinstance(data, dict) else None) or AUTO_APPROVE_HOURS)
    lib = json.load(open(LIBRARY))
    counts = apply(lib["videos"], decisions, auto_hours=hours)
    pending = sum(1 for v in lib["videos"] if v.get("studio") and v.get("review") == "pending")
    line = (f"studio deck: {counts['approved']} approved, {counts['skipped']} skipped, {counts['auto']} auto-approved, "
            f"{counts['edited']} caption edit(s), {counts['rerender']} to re-render, {pending} waiting for review")
    print(line)
    if os.environ.get("DRY_RUN") == "1":
        return
    with open(LIBRARY, "w") as f:
        json.dump(lib, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(STATE, "w") as f:
        json.dump({"lastSync": now().strftime("%Y-%m-%dT%H:%M:%SZ"), "decisionsSeen": len(decisions), "summary": line}, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
