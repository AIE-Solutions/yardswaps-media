#!/usr/bin/env python3
"""The real-app moment at the end of a listing Reel (test from 2026-11-28).

Alan asked whether our posts should show the platform more. Our own Instagram numbers (Nov 14-27, Metricool)
said platform-first Reels reach far fewer people (median 17) than listing Reels (median 95), so instead of
more platform posts we put the platform inside the posts that already get reach: a 3-second piece of the
live-app walkthrough ("Add a photo. AI reads it." then "AI fills in the rest.", the real Expo build of the
app, studio/walkthrough/live) goes between a listing Reel's last photo and the end card.

It runs as a test: half of the listing Reels built or restyled from today get the tail (chosen by the
listing id, so a clip keeps its group when it is rebuilt), and the library entry says which:
"app_tail": "<walkthrough item>" or "app_tail": "none". metrics/README.md has how to read it.

`python3 listings/app_tail.py` cuts the tails into reels/app-tails/ from the walkthrough clips.
"""
import hashlib
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAILS = os.path.join(ROOT, "reels", "app-tails")
START, SECONDS = 5.0, 3.0   # the scan step sits at 6.0-9.1 s in all eight walkthroughs; start 1 s before it
TEST_FROM = "2026-11-28"
ITEMS = ["generator", "espresso", "cooler", "boxtruck", "trailer", "racking", "mower", "toolcabinet"]
# The walkthrough whose item is closest to the listing's category, so the phone shows a like item.
BY_CATEGORY = {
    "generators": "generator", "electrical": "generator", "compressors": "generator",
    "restaurant": "espresso", "cooking": "espresso", "retail": "espresso", "laundry": "espresso",
    "refrigeration": "cooler", "hvac": "cooler",
    "fleet": "boxtruck", "vacuum": "boxtruck",
    "trailers": "trailer", "paving": "trailer", "concrete": "trailer", "excavators": "trailer",
    "warehouse": "racking", "forklifts": "racking", "office": "racking", "aerial": "racking", "cranes": "racking",
    "landscaping": "mower", "agriculture": "mower",
    "machining": "toolcabinet", "tools": "toolcabinet", "automotive": "toolcabinet", "welding": "toolcabinet",
    "parts": "toolcabinet", "pumps": "toolcabinet", "pressure": "toolcabinet", "hydro": "toolcabinet",
    "inspection": "toolcabinet", "drilling": "toolcabinet", "safety": "toolcabinet", "environmental": "toolcabinet",
}


def source(item):
    return os.path.join(ROOT, "reels", "library", f"yardswaps-walkthrough-live-{item}-9x16.mp4")


def path(item):
    return os.path.join(TAILS, f"scan-{item}.mp4")


def in_test(listing_id):
    """True for the half of listings that get the tail (stable per listing)."""
    return int(hashlib.sha1(listing_id.encode()).hexdigest(), 16) % 2 == 0


def pick(listing):
    """The walkthrough item for this listing's tail, or None when it is in the control half."""
    if not in_test(listing["id"]):
        return None
    item = BY_CATEGORY.get(listing.get("category"))
    if not item:
        item = ITEMS[int(hashlib.sha1(listing["id"].encode()).hexdigest(), 16) // 2 % len(ITEMS)]
    return item if os.path.exists(path(item)) else None


def frames(item, w, h, fps):
    """The tail's frames as raw rgb24 bytes, one per frame."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path(item), "-vf", f"scale={w}:{h},fps={fps}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    size = w * h * 3
    return [raw[i:i + size] for i in range(0, len(raw) - size + 1, size)]


def build():
    os.makedirs(TAILS, exist_ok=True)
    for item in ITEMS:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(START), "-t", str(SECONDS), "-i", source(item),
                        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-r", "30", "-movflags", "+faststart", path(item)], check=True)
        print(f"{path(item)} {os.path.getsize(path(item)) // 1024} KB")


if __name__ == "__main__":
    build()
