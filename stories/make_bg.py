#!/usr/bin/env python3
"""Pick today's machine and get a 9:16 background for the LIST IT FREE Story.

Runs in GitHub Actions (story.yml). Writes stories/out/<date>-<machine>-bg.<ext>
and prints KEY=VALUE lines for $GITHUB_OUTPUT (date, machine, bg).

Background: today's existing stories/out/<date>-<machine>-bg.png if present,
else the oldest unused image in stories/bank/<machine>/, else BG_URL (an https image made elsewhere, e.g. ElevenLabs) if given, else one Runway gen4_image text-to-image at 1080:1920 (about 8 credits).
The image is an illustrative backdrop only, never a real listing.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "broll"))
import runway_clip as rw  # noqa: E402  (req / wait / download helpers)

# Approved by Alan 2026-11-08: one machine per weekday (Monday = 0).
MACHINES = ["generator", "conveyor oven", "dump trailer", "walk-in cooler",
            "ice machine", "zero-turn mower", "scissor lift"]

PROMPT = (
    "Vertical photorealistic photo of a used commercial equipment yard at golden hour. "
    "Prominently in the center foreground: a used {machine}, with normal wear, parked on gravel. "
    "Behind it, softly out of focus, a few other used machines and pallets along a chain-link fence. "
    "Warm low sun, long shadows. The top third of the frame is clean open sky, darker deep blue, "
    "empty, left for text. No people, no text, no letters, no logos, no brand names, no signs, "
    "no license plates. Natural 35mm camera photo, shallow depth of field."
)


def rotation_pick(now):
    """Nov 21 (Alan: "We keep reusing the same machines"): instead of the fixed weekday machine, take the
    bank machine that no channel has shown longest (rotation/rotation.py reads every posting log), skipping
    machines and categories shown in the last 14 days when another choice exists. A new folder in
    stories/bank/<machine-slug>/ adds that machine to the rotation. Falls back to the weekday machine."""
    weekday = MACHINES[now.weekday()]
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rotation"))
        import rotation as rot
    except ImportError:
        return weekday
    bank = os.path.join(os.path.dirname(__file__), "bank")
    have = sorted(d for d in os.listdir(bank) if os.path.isdir(os.path.join(bank, d))
                  and any(f.endswith(".png") for f in os.listdir(os.path.join(bank, d)))) if os.path.isdir(bank) else []
    if not have:
        return weekday
    hist = rot.uses()
    cutoff = rot.now() - rot.dt.timedelta(days=rot.ROTATION_DAYS)
    last_m, last_c = {}, {}
    for u in hist:
        last_m[u["machine"]] = u["time"]
        if u["category"]:
            last_c[u["category"]] = u["time"]
    old = rot.now() - rot.dt.timedelta(days=3650)

    def key(slug):
        lm = last_m.get("story-" + slug, old)
        lc = last_c.get(rot.STORY_CATEGORY.get(slug, ""), old)
        return (lm >= cutoff, lc >= cutoff, lm, lc)
    pick = sorted(have, key=key)[0]
    print(f"rotation picked {pick} for the Story (bank: {', '.join(have)})")
    return pick.replace("-", " ")


def main():
    now = datetime.now(ZoneInfo("America/Chicago"))
    machine = (os.environ.get("MACHINE") or "").strip().lower() or rotation_pick(now)
    bank_slugs = os.listdir(os.path.join(os.path.dirname(__file__), "bank")) \
        if os.path.isdir(os.path.join(os.path.dirname(__file__), "bank")) else []
    if machine not in MACHINES and machine.replace(" ", "-") not in bank_slugs:
        rw.die(f"machine {machine!r} is not on the approved list {MACHINES} and has no bank folder")
    date = now.strftime("%Y-%m-%d")
    slug = machine.replace(" ", "-")
    os.makedirs("stories/out", exist_ok=True)
    bg_url = (os.environ.get("BG_URL") or "").strip()
    existing = f"stories/out/{date}-{slug}-bg.png"
    bank_dir = f"stories/bank/{slug}"
    bank = sorted(f for f in os.listdir(bank_dir) if f.endswith(".png")) if os.path.isdir(bank_dir) else []
    if os.path.isfile(existing) and not bg_url:
        print(f"reusing today's background {existing}")
        out = existing
    elif bank and not bg_url:
        # Pre-made backdrops (ElevenLabs, see README): each is used once, then
        # moved out of the bank, so every Story still gets an unused image.
        src = os.path.join(bank_dir, bank[0])
        out = existing
        os.replace(src, out)
        print(f"using bank image {src} ({len(bank) - 1} left for {machine})")
    elif bg_url:
        if not bg_url.startswith("https://"):
            rw.die("BG_URL must be https")
        out = f"stories/out/{date}-{slug}-bg.png"
        rw.download(bg_url, out)
    else:
        key = os.environ.get("RUNWAYML_API_SECRET", "").strip()
        if not key:
            rw.die("RUNWAYML_API_SECRET not set and no BG_URL given")
        body = {"model": "gen4_image", "promptText": PROMPT.format(machine=machine),
                "ratio": "1080:1920"}
        task = rw.req("POST", "/v1/text_to_image", key, body)
        print(f"text_to_image task {task.get('id')} for {machine}")
        done = rw.wait(task["id"], key)
        out = f"stories/out/{date}-{slug}-bg.png"
        rw.download(done["output"][0], out)
    print(f"date={date}")
    print(f"machine={machine}")
    print(f"slug={slug}")
    print(f"bg={out}")
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f:
            f.write(f"date={date}\nmachine={machine}\nslug={slug}\nbg={out}\n")


if __name__ == "__main__":
    main()
