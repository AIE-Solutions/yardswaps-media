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

## Build

```
cd ads/storefront-ad
bash build.sh clips out            # clips/a.mp4 b.mp4 c.mp4; leave the first argument empty for the stills
python3 wordsheet.py out/yardswaps-storefront-9x16.mp4 out/words-vs-screen.jpg
```

`MUSIC=` picks the bed (default `music/v2/yardswaps-music-road-124bpm.mp3`, licensed). Rebuild the app
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
