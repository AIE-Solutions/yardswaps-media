# Live-app walkthroughs (approved 2026-11-26)

Alan, 2026-11-26: "we want this to be a live motion video of our application in action", then
"Yup perfect" on the espresso sample, with one change: "the final YardSwaps from older version is
what I want". This folder is how the eight clips in `reels/library/yardswaps-walkthrough-live-*-9x16.mp4`
were made. Paths that start with `WORK` are a scratch folder: point them at your own before a run.

## What a clip is
1080x1920, 30 fps, about 23 s.
1. Opener, 2.1 s: the real listing photo over its own blurred fill, a white hook pill
   ("POV: selling a ...") and the blue question pill.
2. The sell flow recorded in the real app (Expo web build of `apps/mobile` in the app repo,
   393x778 viewport at 3x), inside the phone frame, with a two-line caption per step:
   List it from your phone / Add a photo / AI fills in the rest / Add your price / Check the details /
   Tap Publish / Your listing is live. Free to list. No cut of the sale.
3. The ending from the earlier walkthroughs, unchanged: blue circle wipe, the YardSwaps wordmark
   bouncing in letter by letter, "<item type> sells too. One photo each.", "Free to list. No cut of
   the sale.", store badges, yardswaps.com and the clip's question in a white pill. 2.9 s.
   `end.html` is the `endCard` function lifted as it was from the earlier walkthrough source;
   `endrender.js` writes its frames. Do not swap in the static end card or a new one.

## Rules
- Real content only: each take uses one live listing's own photo and facts (`scan-<item>.json` is
  the listing's title, category, condition and details, typed from the public listing page).
  Never a made-up item, never a seller's or business's name, phone, address, plate or VIN.
- Nothing is published and nothing is spent: `mock.js` answers every `/api/` call locally and
  `lib.js` blocks every request that is not localhost. A real AI scan on the live site costs money
  and is the owner's call; do not switch the mocks off.
- No generated footage, hands or sound. Music is one of the beds in `music/v2/` at 0.35.
- The app refuses to publish without a location and without a category, so a listing with no public
  location or in the catch-all category cannot be recorded.

## Run
`app-up.sh` builds and serves the app on localhost:8081, `recall.sh <item> ...` records takes
(`reclive.js`), `buildall.sh` renders the endings and builds every clip with `live.py`
(`python3 live.py c-<item>.json out.mp4 [stills dir]`), `app-down.sh` stops the server.

## In the lineup
Library entries carry `"walkthrough": "live"`. `reels/post_reels.py` posts one walkthrough a day on
Instagram and Facebook: a live-app one when one may run, an earlier one (`earlier_look_ok`) only
when none may.
