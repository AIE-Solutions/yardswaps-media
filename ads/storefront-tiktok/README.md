# Storefront ad, TikTok-safe 9:16 (Nov 25)

Alan, Nov 25: "We should post our awesome storefront ads there" (TikTok). This is the storefront ad live on Meta
(big logo, phone scrolling to the listing cards, founding end card, 13 s, music and sound effects, no voiceover),
re-laid out for TikTok: TikTok draws its caption over the bottom of the frame and its like, comment and share
buttons down the right edge, so at 1080x1920 no text or call to action sits in the right 140 px or the bottom 400 px.

- Captions are redrawn with 140 px of clear space on their right, so they centre 70 px left of the frame centre.
- The phone shot, the /dealers screen and the founding end card are scaled to 0.84-0.86 and moved up and left on
  their flat backgrounds; `phone.json` and the phone mask follow.
- Same shots as the Meta cut. The original `clips-v4/` folder was never committed, so: y1 is the Gen-4.5 yard walk
  (Runway task 84a9bfd5-90a4-4b24-bc5c-f482b971da94), y2 is project files `storefront-ad/clips/y2.mp4`, and the three
  real-unit bands (grapple truck, telehandler, F-350) are cut from the live Meta video itself, where they sit clean
  below the captions: frames 75-105 and 105-135 at `crop=1080:810:0:640`, frames 135-165 at `crop=1080:758:0:666`,
  each padded with `tpad=stop_mode=clone:stop=3`.

Build (needs `ads/storefront-ad/` from the storefront branch, PR #73; copy `layout-tiktok.py` in there and run it,
which writes `vr-9x16-tiktok/`, also kept here):

    RATIO=9x16-tiktok SPEED_FULL=1.3 SPEED_BAND=1 REC=$PWD/rec/storefront-8s-neutral.mp4 REC_SS=2.5 REC_SPEED=1.8 \
      ENDCARD=endcard-founding.png BRAND=brand-big.png OUT=yardswaps-storefront-tiktok-9x16.mp4 \
      bash build-viral4.sh <clip dir> out-tiktok

Output: `reels/library/yardswaps-storefront-whole-yard-tiktok-9x16.mp4` (TikTok only, first in line through
`next_on`), and project files `yardswaps-campaign/assets/ads/storefront-tiktok/`. Loudness -15 LUFS.

## v2, Storefront plan (Nov 25)

Guard eval #37: the /dealers shot still said "Dealer plan" (renamed "Storefront plan" on 11-22). `dealers-card.py`
now reads `dealers-mobile-live-1125.png` (the live page re-recorded 11-25, cut at row 1334), and
`vr-9x16-tiktok/stage-dealers.png` is rebuilt from it. Same build command; then
`python3 brand/endcard/endcard.py add <out> reels/library/yardswaps-storefront-whole-yard-tiktok-9x16-v2.mp4 dealer`.
Only 8.5-10.0 s differs from v1. Check: `motion/audit/WORDS-VS-SCREEN-2026-11-25-storefront.md`.
