# Runway instructions: storefront ad (Instagram, Facebook, TikTok, Shorts)

A 26-second vertical video for dealers and anyone selling a yard full of units: three idle machines in a
dealer yard (Runway Gen-4 Turbo clips made from our own listing photos), then the real app on a big phone
(the storefront page with the same three units at the top, then the Dealer plan card), then the light end
card. Organic post only, no ad spend, no credit purchases. Alan asked for it on Nov 20 ("can we make a add
for storefronts", "make sure we got the latest update of the phone app in"): the app screens are recordings
of main at #413 (Nov 20), with the Plans sheet from #408 and the storefront page from #402 to #405.

What the words say and what the screen shows is on `out/words-vs-screen.jpg`. The preview `out/yardswaps-
storefront-9x16.mp4` uses the stills with a slow push in place of the Runway clips; the clips replace them,
nothing else changes.

## The offer, as verified on Nov 20

- Dealer plan: first 30 days free for new dealers, then $49/mo (DEALER_TRIAL_DAYS 30 since PR #382; the app's
  Plans card says "First 30 days free for new dealers" and "Nothing charged for 30 days. Cancel anytime
  before."). Yearly $490.
- Founding price: $29/mo for the first 3 paid months, first 100 storefronts, every first-time monthly
  checkout until Dec 1 (proven live Nov 18, promo FOUNDINGDEALER). The video does not say it, so it stays
  usable after Dec 1; the caption says it until then.
- Featured in YardSwaps social posts: a storefront perk since Nov 19 (PR #408), on the Dealer card. Never
  promise views, sales or a schedule.
- Never: "free storefront" without the 30 days, a category count, "top of search", a Verified Dealer badge
  during the trial.

## What to do in Runway (app.runwayml.com, Alan's account)

Three generations, one take each. Do not buy credits and do not upgrade the plan. Gen-4 Turbo is 5 credits
per second, so each 5 s clip is 25 credits and the three together 75. If the balance is under 75, make
them in this order and stop when it runs out (a: grapple truck, b: telehandler, c: F-350); the preview's
stills cover the rest.

For each clip:

1. Generate video, model **Gen-4 Turbo**, mode **image to video**.
2. Upload the start image from `stills/` (the 4:3 versions, padded top and bottom so the whole machine
   stays in frame; Runway crops anything that does not fit the ratio):
   - a: `grapple-truck-4x3.jpg`, aspect ratio **4:3**
   - b: `skytrak-telehandler-4x3.jpg`, aspect ratio **4:3**
   - c: `f350-supercab-4x3.jpg`, aspect ratio **4:3**
3. Duration **5 s**. Leave the seed and other settings at default.
4. Paste the prompt for that clip (below). Generate once.
5. Download the clip as `clips/a.mp4`, `clips/b.mp4`, `clips/c.mp4`.
6. Check it against "Reject a clip when", then rebuild.

### Prompt a: Freightliner M2 grapple truck (4:3)

```
Locked-off tripod shot of this parked grapple truck in a gravel equipment yard, late afternoon. Very slow push in, almost still. The truck is switched off and does not move: no wheels turning, the grapple arm and the bed stay exactly where they are, no lights, no exhaust, no driver. Only a faint drift of dust in the air and the trees behind moving slightly in the wind. Keep the whole truck in frame, same framing as the photo. Real photograph look, natural daylight, fine film grain. No people, no text, no logos added.
```

### Prompt b: SkyTrak 6042 telehandler (4:3)

```
Locked-off tripod shot of this parked telehandler in a crowded equipment yard, overcast daylight. Very slow push in, almost still. The machine is switched off and does not move: the boom and forks stay raised exactly where they are, no wheels turning, no lights, no operator. Only the clouds drifting slowly and a faint shimmer of heat over the gravel. Keep the whole machine in frame, same framing as the photo. Real photograph look, natural daylight, fine film grain. No people, no text, no logos added.
```

### Prompt c: Ford F-350 SuperCab service truck (4:3)

```
Locked-off tripod shot of this parked white service truck on a concrete lot, soft daylight. Very slow push in, almost still. The truck is switched off and does not move: no wheels turning, no lights, no doors opening, no driver. Only the leaves of the trees behind moving a little in the wind. Keep the whole truck in frame, same framing as the photo. Real photograph look, natural daylight, fine film grain. No people, no text, no logos added.
```

### Reject a clip when

- the machine moves, drives, lifts, lowers or lights up;
- a person, a hand, a new object, text or a logo appears;
- the framing drifts off the photo's framing or zooms past about 4 percent (the push must stay subtle);
- the first frame does not match the still (the match cut depends on it).

A rejected clip is not regenerated on the free plan; the still stands in.

## Sizes (Alan, Nov 20: "This add will be running on meta for couple weeks")

| File | Size | For |
|---|---|---|
| `yardswaps-storefront-9x16.mp4` | 1080x1920 | organic Reels, Stories, Shorts, TikTok |
| `yardswaps-storefront-paid-9x16.mp4` | 1080x1920 | Meta paid Reels and Stories: the line is on screen from frame 0 and every word sits between 15 and 62 percent of the height (Meta's account row covers the top 14 percent and the CTA block the bottom 35 percent); the end card content sits 180 px higher |
| `yardswaps-storefront-paid-4x5.mp4` | 1080x1350 | Facebook and Instagram Feed |
| `yardswaps-storefront-paid-1x1.mp4` | 1080x1080 | square placements |

The video never says the $29 founding price, so the same files run past Dec 1; the Dec 1 line lives in the
primary text only. The openers are generated from our own photos, so the AI-generated toggle is on when the
ad is uploaded. `layout.py` makes each size's caption cards, phone stages, mask and end card (`r<size>/`).

## Build

```
cd ads/storefront-ad
python3 layout.py                                   # per-size assets (already committed)
for r in 9x16 9x16-paid 4x5 1x1; do RATIO=$r bash build.sh clips out; done   # clips/a.mp4 b.mp4 c.mp4; "" for the stills
python3 wordsheet.py out/yardswaps-storefront-9x16.mp4 out/words-vs-screen.jpg
python3 wordsheet.py out/yardswaps-storefront-paid-9x16.mp4 out/words-vs-screen-paid-9x16.jpg
```

`MUSIC=` picks the bed (default `music/v2/yardswaps-music-road-124bpm.mp3`, licensed). `clips/` is git-ignored; add the Runway clips with `git add -f`. Rebuild the app
part when the app changes: `rec/storefront-8s.mp4` and `rec/plans-dealer.png` come from the motion
recording kit (`assets/motion/source/recording/`, `MOCK=./mocksf REC=store node recsf.js`) against Expo
web on the current main.

## Posting plan (after Alan's OK)

- reels/library.json: slug `storefront-dealer-yard`, `audience: dealer`, `category: fleet`, priority 0,
  AI label on (the openers are generated from our photos).
- Instagram and TikTok caption: "A yard full of units, one page buyers can open. The YardSwaps storefront
  puts every unit you list in one place, with your hours and service area, and your new listings take
  turns in our daily posts. First 30 days free, then $49 a month. Before Dec 1, the first 100 storefronts
  pay $29 a month for their first 3 paid months. Listing is free on every plan. #usedequipment
  #equipmentdealer #fleettrucks #telehandler #yardswaps" then the question "What's sitting in your yard
  right now?"
- Facebook: the same with https://www.yardswaps.com/s (the storefront short link).
- YouTube Shorts title: "Your yard, on one page". Drop the Dec 1 sentence from Dec 1 on.

## Night version (Nov 20)

`stills-night/` holds the same three photos graded dark and moody (the After hours look: darker midtones, sky falling to night, slate shadows, warm highlights, vignette, grain) by `night.py`, which also blurs the dealer watermark and the unit number on the telehandler photo (the daylight `stills/` copy got the same blur). `STILLS=stills-night` makes `build.sh` use them; the outputs are named `yardswaps-storefront-night-9x16.mp4` and `yardswaps-storefront-night-paid-9x16.mp4` (`out-night/`). The app part and the end card are unchanged. Runway clips made from `stills-night/*-4x3.jpg` drop in the same way as the daylight ones (the clip dir wins over the stills).

## v3, the bright 13-second cut (Nov 20)

Alan rejected the night version ("It's all dark!") and asked for new
imagery and prompts. v3 is a new edit, not a re-skin: bright daylight,
motion from frame 0, one line, one CTA, built for sound-off Meta
placements (caption inside the 9:16 safe zone, wordmark on screen from
the first frame).

Shape: `build-v3.sh` (assets from `layout-v3.py`, sheet from
`wordsheet-v3.py`), sizes `9x16-paid` and `4x5`.

| t | Scene | Source | On screen |
|---|---|---|---|
| 0.0–3.0 s | Yard row, slow push in | `clips/y1.mp4` (Gen-4 Turbo from `gen/yard-row.jpg`) | "Your yard." + wordmark + "AI-generated scene" |
| 3.0–5.6 s | Loader, forklift, generator, slow dolly | `clips/y2.mp4` (Gen-4 Turbo from `gen/loader-forklift-2.jpg`) | "On one page." + wordmark + "AI-generated scene" |
| 5.6–11 s | Real storefront page on a phone | `rec/storefront-8s.mp4` (real app recording) | stage card: "Your storefront on YardSwaps" |
| 11–15 s | End card | `v3-*/endcard.png` | "30 days free, then $49/mo" + "yardswaps.com/dealers" |

The AI label stays on both generated scenes for their whole length. The
real-unit clips (`clips/a.mp4` grapple truck, `b.mp4` telehandler,
`c.mp4` F-350) are 4:3, so they went into the old 26-second layout
instead (`out-clips/`, "option B"), not into v3.

### Prompts that produced the scenes

Gen-4 image, 9:16, 1080p (8 credits each):

- `gen/yard-row.jpg`: "Vertical photograph, bright clear morning, a used
  commercial equipment dealer's gravel yard. A row of parked machines
  faces the camera at a slight angle, nearest first: a yellow mini
  excavator, a compact track loader, a green telehandler with its boom
  down, a white service pickup with a utility bed, and a flatbed trailer.
  Clean blue sky, crisp sunlight, long soft shadows on the gravel,
  chain-link fence and a grey steel warehouse behind. Everything switched
  off and still. Realistic photo, 35mm lens, sharp, natural colour, no
  people, no text, no logos, no license plates."
- `gen/loader-forklift-2.jpg` (second try; the first,
  `gen/loader-forklift.jpg`, carried made-up lettering on the generator
  and forklift): same scene with "Every machine has plain, unmarked
  painted panels: no lettering, no words, no badges, no decals, no
  stickers, no model numbers, no logos anywhere." Gen-4 still painted a
  small logo on the generator, so the still was patched with ffmpeg
  `delogo` boxes before animation (`gen/loader-forklift-2-raw.png` is the
  untouched output).
- `gen/trailer-load.jpg`: rejected, garbled fake text on the trailer
  rail. Not used.

Gen-4 Turbo image-to-video, 9:16, 5 s (25 credits each):

- y1: "Slow, steady forward glide at walking pace, camera low and level,
  moving toward the row of parked machines. Everything stays parked and
  switched off: no wheels turning, no arms or booms moving, no lights, no
  people. Only the light, a faint shimmer of heat over the gravel and a
  few leaves moving in the breeze. Keep the whole yard in frame, bright
  clean morning daylight, realistic photographic look, fine grain. No
  text, no logos added."
- y2: "Slow, steady sideways dolly to the right at walking pace, camera
  low and level, passing the parked wheel loader, forklift and generator.
  Everything stays parked and switched off: no wheels turning, no mast or
  bucket moving, no lights, no people. Only the light, a few small clouds
  drifting and a faint shimmer of heat over the gravel. Keep all three
  machines in frame, bright clean daylight, realistic photographic look,
  fine grain. No text, no logos added."

Lesson: Gen-4 puts brand-like lettering on machine panels even when the
prompt forbids it. Check every still at full size before animating, and
patch the still (not the video) when a badge slips through.

### Credits

All free credits on Alan's Personal · Pro plan, nothing bought: 573
before the session, 341 after (three 4:3 real-unit clips, four images,
three 9:16 clips, one of them the redo).

### How the files moved without Remote Control

Alan's Chrome, driven from the thread: images into Runway through the
hidden file input (bytes handed over by `postMessage` from a page we
control), results out through the "Clip relay" artifact
(https://claude.ai/artifact/Tb6ZgtrdH3Yu5ncy5RJpYt), which stores
whatever the Runway tab posts to it as assets we can read from the build
container. No keys, no downloads on Alan's PC.

### v3.1 (Nov 20, after Alan: "Man that new one is nice. Improvements?")

Same scenes, tighter: openers 2.4 s + 2.2 s so the real storefront is on
screen by about 4.3 s instead of 5.6 s, storefront scene 6.0 s (more of
the inventory scroll, the real units and prices show), end card 3.0 s.
12.7 s total. Adds the 1:1 size for the remaining feed placements.
`RATIO=<size> D1=2.4 D2=2.2 D3=6.0 D4=3.0 TAG=v3.1 build-v3.sh clips out-v3.1`,
sheet with `WS_TIMES=1,3.3,7,11.5`. v3 kept beside it for comparison.

Not done, Alan's call: re-record the demo storefront without the
Houston address (nationwide, no location rule; needs the recording kit
and about half an hour), and a real 5-second phone clip of a dealer yard
would replace the AI opener outright.

## Viral format (Nov 20, Alan: "Go by the viral format")

No format of that name existed in the project, so this follows the
short-form structure that travels: text hook on screen from the first
frame, hard cuts on the beat of the track (124 bpm, one cut every two
beats), big centred captions that pop in, a slow push on every shot, the
payoff (the real storefront) by 5 s, one call to action. 12.1 s.

`layout-viral.py` (captions, auto-shrunk to fit, and the logo pill; the
rest reused from `v3-<size>/`) and `build-viral.sh`, sizes 9x16-paid, 4x5, 1x1; sheet
`wordsheet-viral.py`.

| Beats | Shot | Source | Caption |
|---|---|---|---|
| 3 | yard row | `clips/y1.mp4` (AI, labelled) | Your whole yard. |
| 2 | loader, forklift, generator | `clips/y2.mp4` (AI, labelled) | One page. |
| 2 | grapple truck, 4:3 band on a blurred fill | `clips/a.mp4` (real unit) | Every unit. |
| 2 | telehandler | `clips/b.mp4` (real unit) | Your hours. |
| 2 | F-350 service truck | `clips/c.mp4` (real unit) | Your links. |
| 8 | real storefront on the phone | `rec/storefront-8s-neutral.mp4` | stage card |
| 6 | end card | `endcard-v3.png` crop | 30 days free, then $49 a month |

### Logo placement (Nov 20, Alan: "logo placement needs improvement")

The first viral cut carried the v3 wordmark: text rendered in Space
Grotesk, floating in the sky with a soft shadow, blue "Swaps" on blue
sky, and on the three real-unit shots in 9:16 it sat right under the
caption and the two overlapped. Now `layout-viral.py` builds the logo
as a lockup: the brand-kit wordmark (`broll/in/brand-kit/wordmark/
yardswaps-wordmark-on-light.png`, slate + blue, the same mark as the end
card) on a white pill with a soft shadow, 370x96 px, pinned top-left
(x 48) on every shot 1–5, same spot in all three sizes: 9:16 at y 290
(15 % down, under Meta's top overlay zone in Reels and Stories), 4:5 at
48, 1:1 at 40. The 9:16 real-unit band moved down 85 px (band top 640,
caption centre 500) so the caption clears the pill; the 1:1 band moved
15 px. The stage shot keeps its own title ("Your storefront on
YardSwaps.") and the end card its big wordmark, so no pill there.

### City-neutral recording

`rec/storefront-8s-neutral.mp4` is the same recording with the demo
dealer at "Anytown, USA", "Delivers within 150 miles" and every listing
card at Anytown (nationwide, no location on social). Mock
`mocksf-neutral.js` in the project-files recording kit
(`assets/motion/source/recording/`), recorded with `MOCK=./mocksf-neutral
REC=store node recsf.js` against Expo web on :8081, frames 0–239 at 30
fps scaled to 1178x2332. v3.1 was rebuilt with it too (`REC=` on
`build-v3.sh`); v3 keeps the Houston recording for comparison.

### Runway quality pass, viral2 (Nov 20, 04:50Z)
Alan: "I think runwayml can do better!". All five shots regenerated in Runway **Gen-4.5** (the best image-to-video model on the account), image-to-video from the same stills, prompts written to Runway's own prompting guide (describe the camera move, not the picture; "parked and completely motionless"; "Continuous, seamless shot"; "No people, no text, no logos").
- y1 yard: slow sweeping low arc over the parked equipment, golden light. y2 loader: low dolly push past the loader bucket, forklift and generator in frame. a/b/c grapple truck, telehandler, F-350: slow sweeping arc around the parked unit, whole unit in frame.
- Cost 60 credits per 5 s Gen-4.5 take (Gen-4 Turbo is 25). 341 -> 146 free credits left; nothing bought.
- Clips in clips-v2/ (not committed): grapple and F-350 cropped to 1104x740 (crop=1104:740:0:44) to drop the photo padding bars (gold strip under the F-350); build-viral.sh band() now sizes the band to the clip and centres it in the 810 slot.
- Build: `RATIO=<size> TAG=viral2 SPEED_FULL=1.3 SPEED_BAND=2 REC=$PWD/rec/storefront-8s-neutral.mp4 bash build-viral.sh $PWD/clips-v2 $PWD/out-viral2` (speed-ups put more camera travel into each sub-second beat cut). Same captions, logo pill, storefront recording and end card as viral.
- out-viral2/current-vs-upgraded-9x16.jpg compares the two cuts frame by frame.

### Final cut, viral3 (Nov 20, 05:05Z)
Alan at his PC: "just finish the ad". viral3 = viral2 with the grapple truck retaken in Gen-4.5 from a still with room around the truck (original photo at 1440x960 plus 120 px of extended sky on top, so 4:3 with the whole truck inside). Prompt asked for "a slow, gentle arc of about twenty degrees ... while pulling back a little" and keeps the truck whole from 3/4 to front view. A first retake with a wide sweep from a tight crop lost the cab out of frame and was dropped. clips-v3/ = clips-v2 with the new a.mp4. Same build line with TAG=viral3 and out-viral3. Credits 146 -> 26, all free.

## Upgrade pass, viral4 (2026-11-20)

Alan bought Runway credits and asked for the better models, fresh app screens and ElevenLabs sound.

- **Shots** (`clips-v4/`, not committed): y1 is a Gen-4.5 first-person walk into the yard (from `yard-row.jpg`); y2 and a are unchanged from viral3 (loader, grapple r2); b is a new Gen-4.5 telehandler arc; c is a new Gen-4.5 F-350 arc from a clean still (gold bar cut off, edges padded to 4:3), cropped `1044:732:30:60` to drop the padded edge. A Kling 4.0 loader take came out almost static, so the viral3 loader stays.
- **Live screen**: `rec/dealers-mobile-live-1120.png` is yardswaps.com/dealers captured signed out, light theme, 390x844 at 3x. `dealers-card.py` cuts it above the price row (the founding $29 stays in the caption only) and writes `vr-<size>/stage-dealers.png`; it plays as s6b after the storefront phone.
- **Sound** (`music/v4/`): ElevenLabs Music v2.5 bed at 120 bpm (instrumental, checked with speech-to-text), SFX for gravel steps under the opener, a whoosh before each yard cut and a tap when each screen appears. `vo-justin-case-timed.mp3` is the Justin Case read split at its pauses so each line lands on its caption.
- **Build**: `build-viral4.sh` (BT=0.5, s6 6 beats, s6b 3 beats, end card 6 beats = 13.0 s). Without VO: `RATIO=... SPEED_FULL=1.3 SPEED_BAND=2 REC=$PWD/rec/storefront-8s-neutral.mp4 bash build-viral4.sh $PWD/clips-v4 $PWD/out-viral4`. With VO add `OUT=...-vo-... VO=$PWD/../../music/v4/vo-justin-case-timed.mp3 VO_DELAY=0 VO_VOL=2.0 MUSIC_VOL=0.3`.
- Outputs: `out-viral4/` (9:16 at the top level, 4x5/ and 1x1/), each with and without voiceover, plus `before-vs-viral4-9x16.jpg`. Project files `assets/ads/storefront-ad/final-viral4/`.

- 11-20 05:28Z Alan: the end of the voiceover felt rushed. The last three lines are now a slower separate read (`vo-justin-case-end-slow.mp3`) placed one per screen: phone 5.75 s, /dealers 8.6 s, end card 10.4 s. Alan also said not to add the "AI-generated scene" text, so the build now overlays `blank.png` (set `AILABEL=ai` to bring the label back); Meta's AI-info toggle still applies.
