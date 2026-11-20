# Meta ads: storefront founding offer (Nov 20 to Nov 30, 2026)

Paid Facebook + Instagram campaign promoting the dealer storefront. Alan asked 2026-11-19 ("Using meta business ads we need to make a promotional campaign", "I want to promote storefronts"). Nothing is spent or published until Alan sets the budget and presses Publish in Ads Manager himself.

## Files

Each ad has a 9:16 cut (Reels, Stories) and a 4:5 cut (Feeds, whole frame on a blurred copy, nothing cropped).

| Ad name | Opener (real listing photo) | Source Reel | Files |
|---|---|---|---|
| a1-whole-lot | enclosed cargo trailer | whole-lot-one-link | a1-whole-lot-founding-9x16.mp4, -4x5.mp4 |
| a2-import | towable generator | import-from-your-website | a2-import-founding-9x16.mp4, -4x5.mp4 |
| a3-stats | MIG welder | storefront-stats | a3-stats-founding-9x16.mp4, -4x5.mp4 |
| a4-socials | restaurant oven | socials-on-storefront | a4-socials-founding-9x16.mp4, -4x5.mp4 |

How they were cut: the source Reel up to its end card (frame where the blue card starts: 12.400 / 12.767 / 12.900 / 12.433 s), then the end card of storefront-founding-29 from 14.433 s ("Storefront: 30 days free. Then $29 a month for 3 months, then $49."), keeping the source Reel's music with a 0.8 s fade. The words-vs-screen check of both parts passed on 11-18 (reels/audit/WORDS-VS-SCREEN-2026-11-18.md).

Not used for paid: dealer-storefront, storefront-30-days-free and storefront-founding-29 (bulldozer opener, and the storefront screen shows a "Verified badge" chip, which a dealer only gets after the first payment).

## v2 (Nov 19): voiceover, captions, hook in the first second

Alan asked to improve the ads ("Improbe the adds", 11-19). The v2 set in `v2/` replaces v1 for the campaign; v1 stays as a fallback.

| Ad name | Hook (real listing photos) | What it shows | Length |
|---|---|---|---|
| b1-tour | grid: grapple truck, telehandler, condenser, pressure washer, tool chest, spray trailer | storefront page, socials, website import, stats, buyer demand | 40.5 s |
| b2-import | grid: box truck, boom mower, floor scrubber, micrometer set | website import, pick what goes live | 22.3 s |
| b3-stats | Hotsy pressure washer | views, saves and chats per unit, 30/90/180 days, CSV export | 24.0 s |
| b4-demand | Sky Trak telehandler | buyer demand report: searches and saved searches near you | 21.8 s |

- Voice: ElevenLabs "Justin Case" (eleven_v4), lines in `narration/meta-ads/lines.tsv`. Music: the licensed clean 120 bpm bed, ducked under the voice, -14 LUFS.
- Every app scene is a real screen recording from the storefront Reels, phone cropped, with the line it shows as a caption. The words match the screen: no "logo" line, because the recordings show an initials avatar, and the demand clip stops before the listing page (which shows a Verified badge).
- "Storefront free for 30 days" sticker from 0.3 s; end card: "Storefront: 30 days free. Then $29 a month for your first 3 paid months, then $49. First 100 storefronts. Open before Dec 1. Cancel before day 30 and pay nothing." plus yardswaps.com/dealers.
- 9:16 keeps text out of the top 14% and bottom 35% (Reels safe zone); 4:5 is for Feeds.
- `make_ad.py` rebuilds any file: `python3 make_ad.py b1-tour 9x16 narration/meta-ads out.mp4` (needs the Space Grotesk and Inter TTFs next to it).

## Offer facts (checked in AIE-Solutions/Marketplace main, 26c6c1e)

- First-time storefronts: 30 days free (DEALER_TRIAL_DAYS 30), card saved at checkout, then $49 a month.
- Founding: every first-time monthly checkout until 2026-12-01 06:00 UTC (midnight Central, FOUNDING_OPEN_UNTIL) gets FOUNDINGDEALER, $20 off for 3 paid months, max 100 redemptions. Proven by a logged redemption 11-18.
- The founding ads must stop by Nov 30, 11:59 pm Central. After that, switch to the Dec plan below.

## Link

Website URL: `https://www.yardswaps.com/dealers?offer=founding`

URL parameters (Ads Manager "URL parameters" field, same for every ad):
`utm_source=facebook&utm_medium=paid&utm_campaign=storefront_founding_nov&utm_content={{ad.name}}&utm_term={{site_source_name}}`

`facebook` is a tracked source (lib/attribution-cookies.ts); `medium=paid` keeps paid clicks apart from organic Facebook posts; `{{site_source_name}}` fills in fb, ig, msg or an. The attribution cookie is first touch for 30 days, so someone who already came in from an organic link keeps that source.

## Dec 1 onward (evergreen, not built yet)

Same structure with the original Reels (their end cards say "First 30 days free, then $49 a month"), link `https://www.yardswaps.com/dealers`, campaign `storefront_trial_dec`, and no founding sentence in the copy.

The full plan, copy and Ads Manager walkthrough: the "Storefront Ads Plan" artifact.
