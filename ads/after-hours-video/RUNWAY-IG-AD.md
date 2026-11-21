# Runway instructions: "After hours" Instagram ad

A short vertical Instagram Reel in the look Alan picked on Nov 17 (the ready-mix
company's sponsored post): one real machine per shot, dark and moody, nothing
moving, no text on the picture. Organic post only, no ad spend, no credit
purchases. Three Runway clips made from our own graded listing photos, then the
light YardSwaps end card. About 17 seconds.

The same three photos already carry the still posts in media PR #72
(`ads/after-hours/out/`). A preview cut built from the stills is in `out/`
(`yardswaps-after-hours-9x16.mp4`, plus a `-captions` variant with three
lower-left lines). The Runway clips replace the stills; nothing else changes.

## What to do in Runway (app.runwayml.com, Alan's account)

Three generations, one take each. Do not buy credits and do not upgrade the plan.
Runway's own pages (Nov 2026) list Gen-4 Turbo at 5 credits per second of video,
so each 5 s clip is 25 credits and the three together 75. If the balance shown
in the app is under 75, make the clips in this order and stop when it runs out
(a: truck, b: engine, c: micrometer set); the preview still covers the rest.

For each clip:

1. Generate video, model **Gen-4 Turbo**, mode **image to video**.
2. Upload the start image from `stills/` (same files as the PR #72 posts):
   - a: `after-hours-peterbilt-379-1x1.jpg`, aspect ratio **1:1**
   - b: `after-hours-komatsu-engine-4x5.jpg`, aspect ratio **3:4**
   - c: `after-hours-micrometer-set-4x5.jpg`, aspect ratio **3:4**
   (Runway has no 4:5; 3:4 is the closest and the build pads the rest.)
3. Duration **5 s**. Leave the seed and other settings at default.
4. Paste the prompt for that clip (below). Generate once.
5. Download the clip as `clips/a.mp4`, `clips/b.mp4`, `clips/c.mp4`.
6. Check it against the list under "Reject a clip when", then rebuild.

### Prompt a: Peterbilt 379 (1:1)

```
Locked-off tripod shot of this parked semi truck at dusk in a gravel yard. Very slow push in, almost still. The truck is switched off and does not move: no wheels turning, no lights coming on, no exhaust, no driver. Only a faint drift of dust in the air and the sky darkening a little. Keep the whole truck in frame, same framing as the photo. Real photograph look, dark and moody, natural light, fine film grain. No people, no text, no logos added.
```

### Prompt b: Komatsu engine on a stand (3:4)

```
Locked-off tripod shot of this diesel engine sitting on a steel stand in a parts warehouse after hours. Very slow push in, almost still. The engine does not move and nothing turns. The overhead fluorescent lights hum and flicker very slightly; a little dust floats in the light. Keep the whole engine and stand in frame, same framing as the photo. Real photograph look, dark and moody, fine film grain. No people, no text, no logos added.
```

### Prompt c: micrometer set in its case (3:4)

```
Locked-off tripod shot of this open wooden micrometer case on a workbench under one lamp, after hours. Very slow push in, almost still. Nothing in the case moves. The lamp light breathes very slightly and dust floats in it. Keep the whole case in frame, same framing as the photo. Real photograph look, dark and moody, fine film grain. No hands, no people, no text, no logos added.
```

### Reject a clip when

- the machine moves, drives, turns, lights up or runs (idle gear only)
- a person, hand or vehicle appears
- Runway adds text, a logo, a badge or a different brand name to the machine
- the item leaves the frame or gets cropped (whole item rule, zoom at most 1.04x)
- the camera cuts or swings; it should feel like a phone on a tripod
- the picture turns cartoon-like, over-sharpened or plastic

Generate again only for a rejected clip, and only while credits last.

## Build the Reel

On the PC (`C:\Github\yardswaps-media`) or any machine with ffmpeg and Python 3 with Pillow:

```
bash ads/after-hours-video/build.sh ads/after-hours-video/clips ads/after-hours-video/out
python3 ads/after-hours-video/wordsheet.py ads/after-hours-video/out/yardswaps-after-hours-9x16.mp4 ads/after-hours-video/out/words-vs-screen.jpg
```

`CAPTIONS=1` before `build.sh` adds the three lower-left lines (Parked for the
night. / Waiting on its next machine. / Every size in the box.). The reference
look has no text on the picture, so the default is no lines.

Each clip plays 4.4 to 4.6 s inside a full-width band over a blurred, darkened
copy of itself (the same opener treatment as "Snap the part"), 0.3 s dissolves,
then the end card: "Lights off? List it free." / "The app writes the listing.
No cut of the sale." / blue pill "What stays after the lights go off?" /
wordmark, store badges, yardswaps.com. Music: the workshop bed from
"Snap the part" (ElevenLabs, licensed), -14 LUFS.

## Posting

- Alan reviews the finished cut before it goes into rotation.
- Instagram and Facebook: add it to `reels/library.json` (slug `after-hours`,
  category `fleet`, `added` = the day it is approved, `priority` 0) and the
  Reels poster takes the next free slot. TikTok picks it up from the same
  library. Turn on the platform's AI-generated label, because the clips are
  generated from the photos.
- Caption (Instagram, 5 tags): "Lights off. Nothing moving. A truck parked for
  the night, an engine on a stand, a micrometer set still in its box. The
  YardSwaps app writes the listing from one photo. Free to list, no cut of the
  sale. #usedequipment #fleettrucks #machineshop #smallbusiness #yardswaps"
  Closing question: "What stays after the lights go off?"
- Facebook: same text with the link https://www.yardswaps.com/f and no tags.

## Files

- `stills/` the three graded photos (from `ads/after-hours/out/`, PR #72)
- `clips/` where the Runway clips go (`a.mp4`, `b.mp4`, `c.mp4`; not in git until they exist)
- `build.sh`, `captions.py`, `endcard.py`, `wordsheet.py`, `c1-3.png`, `endcard.png`
- `out/` the preview cuts and their words-vs-screen sheets
