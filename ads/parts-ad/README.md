# "Snap the part" (9:16, 22 s)

The Runway ad Alan asked for on Nov 16 ("Let's get a runway ad going"). For organic Reels, Shorts and TikTok only. Not a paid ad; the Meta campaign stays off at $0. Music only, no voice.

| Time | Shot | Line on screen |
|---|---|---|
| 0.0-3.3 | Real listing photo: pallet of wrapped Eaton hydraulic cylinders, part labels on, idle | The pallet nobody touched all year. |
| 3.0-6.0 | Real listing photo: open wooden micrometer case on a bench | The mic set still in its case. |
| 5.7-8.7 | Real listing photo: spray trailer parked by a wall | The sprayer parked all season. |
| 8.4-17.7 | Real app recording listing those same cylinders (from motion/silent/yardswaps-surplus-parts-labels-9x16.mp4, 4.85-14.15 s): photo taken, AI fills title, category, condition and count, price set, "Your listing is live!" | Surplus pallet? Snap it, labels up. / AI fills it. Title. Category. / AI wrote it. Condition, count. / Tap once. Price set. / Published. Listed free. / One photo. No typing. Listed free. |
| 17.4-22.1 | Light end card: wordmark, "Snap the part. List it free.", store badges, yardswaps.com | What's the oldest part still on your shelf? |

Two versions of the openers:
- `yardswaps-snap-the-part-9x16.mp4` (this build): the real photos with a slow push (1.00 to 1.035, under the 1.04 cap), whole item in frame, over a blurred copy. No generation at all.
- Runway version: the same three photos animated with Gen-4 Turbo on Alan's own Runway account (free credits, nothing bought), locked-off camera, only light and dust move. Drop the clips in as `clips/a.mp4 b.mp4 c.mp4` and rebuild; everything else is identical.

Rules checked: idle gear only, nothing running or driving; the whole item is in frame in every opener (no cover crop, zoom under 1.04x); the item in the opener is the item in the app; real app recording, no redrawn screen; no faces, no plates, no dealer banners; no category count; every line matches what is on screen (`words-vs-screen.jpg`); no promise of views or sales. Instrumental from ElevenLabs Music v2.5 (transcribed: no words), normalized to -14 LUFS.

Known: the app segment passes the Publish screen, which shows the paid boost prices for a moment (the real app does).

Rebuild: `source/build.sh [clipdir] [outdir]` (captions `source/captions.py`, end card `source/endcard.py`, openers `source/opener.sh`, sheet `source/wordsheet.py`). Music `source/music-workshop-26s.mp3` (ElevenLabs flow NOvIfrGcbc3En5vOVJBF).
