# Words vs screen, Nov 25: storefront ad, Storefront plan re-cut

Why: Guard eval #37. The storefront ad (TikTok cut `storefront-whole-yard-tiktok` and the live Meta ad
r1-yard-biglogo) showed the /dealers page from 11-20, with a "DEALER PLAN / 30 days free" card. The site has said
"Storefront plan" since 11-22.

Fix: /dealers re-recorded from the live page on 11-25 (yardswaps.com/dealers, 390x844 at 3x, signed out, light theme,
optional cookies declined): `ads/storefront-tiktok/dealers-mobile-live-1125.png`, made into the screen card by
`ads/storefront-tiktok/dealers-card.py` (cut above the price row, CUT 1334). Only the /dealers shot (8.5 to 10.0 s)
changed; a frame-by-frame diff against the earlier cuts is zero everywhere else. Every cut then ends on the blue
storefront end card (`brand/endcard/endcard.py add ... dealer`, 2 s).

Sheets (12 time-stamped frames each, eye-checked): `storefront-whole-yard-tiktok-v2-words-vs-screen.jpg`,
`storefront-meta-storefrontplan-{9x16,4x5,1x1}-words-vs-screen.jpg`.

| Time | Words on screen | What the screen shows | Result |
|---|---|---|---|
| 0-1.5 s | "Your whole yard." | Equipment yard, rows of machines | Pass |
| 1.5-2.5 s | "One page." | Loader, forklift, generator in a yard | Pass |
| 2.5-5.5 s | "Every unit." / "Your hours." / "Your links." | Real listed units: grapple truck, telehandler, F-350 service truck | Pass |
| 5.5-8.5 s | "Your storefront on YardSwaps." | Storefront on a phone: Follow, About, "Mon to Sat, 7 am to 5 pm", link icons, inventory cards with prices | Pass (recording from 11-20; no plan name or price label on it) |
| 8.5-10 s | (no caption) | Live /dealers: "Home / Storefronts", "Your own storefront on YardSwaps", **STOREFRONT PLAN / 30 days free** | Pass, matches the live page 11-25 |
| 10-12 s | End card: "Open your storefront." / "30 days free, then the founding price." / yardswaps.com/s, store badges | Blue YardSwaps end card, storefront version | Pass. No "Free to list" on a storefront clip (MESSAGING.md) |

Files:
- TikTok: `reels/library/yardswaps-storefront-whole-yard-tiktok-9x16-v2.mp4` (12.0 s). Back in rotation, not first in
  line (it already posted once on 11-25). v1 kept.
- Meta (ready, not swapped; the console change waits on Alan's go): project files
  `yardswaps-campaign/assets/ads/storefront-ad/final-viral4-storefrontplan-endcard/`
  `yardswaps-storefront-viral4-cards-biglogo-storefrontplan-endcard-{9x16,4x5,1x1}.mp4` (12.0 s each). These are the
  live r1-yard-biglogo cut with the new /dealers shot spliced in and the blue end card in place of the founding card;
  the music and sound are the live cut's own.
