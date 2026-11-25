# YardSwaps Studio

Our own short-video maker, built on 2026-11-25 to replace the HeyCatch video posts (Alan: "build us the
same functionality Heychat provides so we don't have to pay for it"). HeyCatch keeps running until Alan
cancels it; the two run side by side until Studio has posted on every platform for a while.

## What it makes
A 7.5 s vertical clip: 5.5 s of real equipment with a meme-format hook at the top, then the 2 s blue
YardSwaps end card. Formats are the ones HeyCatch uses and that work now: "POV: ...", "Me when ...",
"Nobody: / Me: ...", "Things that just make sense: ...". The hooks live in `hooks.json`; `{thing}` becomes
the item's short name, taken from the listing's own title ("Caterpillar 140H V-Plow" becomes
"caterpillar v-plow") so the joke never names the wrong machine.

Footage, in this order:
1. A live listing's photo that the daily listing review already approved (the Just listed card photo, or an
   approved row of `listings/reel-queue.json`), with a slow push-in and the price pill. Faces refused and
   digits blurred, the same checks as every listing clip. Sellers who turned off social features are skipped.
2. A text-free stock photo from `stock/` (Canva stock from our HeyCatch background pack; no AI images, no
   people). A stock clip never says the item is listed.
3. A library clip marked `"clean": true` (no words burned in). None yet.

We make our own memes and never use movie or TV stills or other people's photos (copyright strikes).

## Where it goes
`make_pov.py` runs at the end of `listings/listing_reels.py` (listings workflow, 9:10 am Central), up to 3
clips a run and never more than 9 waiting to post. Each clip goes into `reels/library.json` with
`"cut": "pov"`, `"studio": true` and its hook as `title`. The posters we already run take it from there:
Instagram, Facebook, Threads and Stories (`reels/post_reels.py`), TikTok (`reels/post_tiktok.py`) and
YouTube Shorts (`youtube/post_shorts.py`, which turns studio clips into queue rows after the hand-made ones;
title = the hook). Machine rotation, caps, hold and the end card check all apply as usual.

## Copy
Seller voice from `MESSAGING.md`: free to list, the AI writes the listing, no selling fee. Never a promise of
views, buyers or a sale, never a category count, never "free storefront". `make_pov.py` refuses a clip whose
words break those rules, and every caption ends with an open question.

## Run it by hand
    DRY_RUN=1 python3 studio/make_pov.py          # renders into /tmp, saves nothing
    STUDIO_PER_RUN=1 python3 studio/make_pov.py   # one real clip into the library

Needs ffmpeg, Pillow, NumPy and OpenCV (and tesseract for the digit blur), as the listings workflow installs.

## Retiring a hook
Add it to `"retired"` in `hooks.json` (the weekly scorecard or a person can). New hooks go in `"hooks"`,
under 90 characters, seller voice only.
