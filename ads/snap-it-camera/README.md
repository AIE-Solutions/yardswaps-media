# "Snap it, camera" (9:16 and 1:1, 15.6 s)

Alan, Nov 21: "How can we build a live motion ad that shows someone taking a picture of equipment. No AI slop please."
Not posted, not boosted. Waiting on Alan's review. Seller audience (MESSAGING.md: "Equipment sitting idle? List it free.").

Nothing in it is generated. No Runway, no Sora, no AI image or video. Every pixel is a real photo, the real app, or drawn shapes and text.

| Time | Shot | Words on screen |
|---|---|---|
| 0.0-2.9 | Full-screen phone camera. The viewfinder shows a real YardSwaps listing photo (a Hotsy hot-water pressure washer, `source/photos/hotsy-pressure-washer.jpg`, whole machine in frame). The photo drifts like a handheld phone (max 1.035x, under the 1.04 cap). It starts soft, then a focus tap at 0.9 s sharpens it. Shutter at 2.3 s: black blink, flash, the thumbnail fills. | Equipment sitting idle? / Snap one photo. |
| 2.9-4.5 | Pull back: the camera screen turns out to be the screen of the phone, then dissolves into the app. | (none) |
| 4.5-12.3 | The real sell-flow recording of that same photo (`motion/silent/yardswaps-pressure-washer-replaced-*.mp4`, 5.8-13.9 s). The AI fills the title "Hot Water Pressure Washer, 3,000 psi...", the category, condition and PSI. Use price is tapped, then "Your listing is live!". | AI fills it. Title. Category. / AI wrote it. Condition, PSI. / Tap once. Price set. / Published. Listed free. / One photo. No typing. Listed free. |
| 12.3-15.6 | Light end card: the wordmark, store badges and yardswaps.com. | Equipment sitting idle? List it free. / Snap a photo. The AI writes the listing. / What's sitting idle in your yard? |

Audio: a music bed (`yardswaps-music-punch-124bpm`) plus the kit SFX: tap, camera shutter, swipe, tap, tap, listing published. Mixed to -14 LUFS with a true peak of -1.4 dB. No voice, per the Oct 11 audio standard. Silent copies (`*-silent.mp4`) are included for platforms that add their own sound.

The camera screen is a generic camera, not a copy of the iPhone Camera app: an amber focus square, a white shutter ring, a thumbnail, a flip icon and a 1x chip.

## Checks
- Same item throughout: the photo in the viewfinder is the photo the app lists (Nov 9 rule).
- Whole item in every frame of the opener. In the 1:1 cut the whole viewfinder fits the frame height, with the phone's bezel at the sides.
- cropaudit: 9:16 returns 0 flags. 1:1 flags 3.25-3.5 s, the middle of the pull-back, where the phone is still larger than the frame by design. This is the same kind of false positive as the match cut in MOTION.md.
- Words match the screen: `words-vs-screen.jpg`.
- No faces, no plates, no seller details, no category count, and no promise of views or sales. Seller copy only, nothing aimed at dealers.

## The truly live version
`SHOT-LIST.md` covers 10 minutes at a yard with two phones: real hands, a real shutter tap, and a screen recording of the real app listing that photo. Those clips replace the 0-4.5 s camera screen. The rest of the ad stays as it is.

## Rebuild
`source/build.sh [outdir]` renders both sizes. It needs the project-files motion library and the ElevenLabs kit. The pieces are `render.py` (opener, pull-back and app part; `RATIO=1x1` for square), `endcard.py`, `assemble.sh` (end card, music, SFX, loudness) and `wordsheet.py`.
