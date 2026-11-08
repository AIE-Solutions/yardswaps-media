#!/usr/bin/env python3
"""Pick today's machine and get a 9:16 background for the LIST IT FREE Story.

Runs in GitHub Actions (story.yml). Writes stories/out/<date>-<machine>-bg.<ext>
and prints KEY=VALUE lines for $GITHUB_OUTPUT (date, machine, bg).

Background: BG_URL (an https image made elsewhere, e.g. ElevenLabs) if given,
otherwise one Runway gen4_image text-to-image at 1080:1920 (about 8 credits).
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


def main():
    now = datetime.now(ZoneInfo("America/Chicago"))
    machine = (os.environ.get("MACHINE") or "").strip().lower() or MACHINES[now.weekday()]
    if machine not in MACHINES:
        rw.die(f"machine {machine!r} is not on the approved list {MACHINES}")
    date = now.strftime("%Y-%m-%d")
    slug = machine.replace(" ", "-")
    os.makedirs("stories/out", exist_ok=True)
    bg_url = (os.environ.get("BG_URL") or "").strip()
    if bg_url:
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
