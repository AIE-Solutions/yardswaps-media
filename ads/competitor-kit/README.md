# Competitor-style ads kit

Built Nov 14, 2026 after Alan asked to "go see what competitor platforms do and make an ad and commercial kinda like it and same quality".
Two pieces use it: [didnt-leave](../didnt-leave/) (15 s ad) and [first-set](../first-set/) (30 s commercial).

## What the competitors do (official sources only)

| Competitor | Pattern we borrowed | Source |
|---|---|---|
| OfferUp | 15 s spot: one everyday moment, then a twist line; short double-negative beats ("skip this, skip that") | OfferUp official YouTube: https://www.youtube.com/watch?v=WU9pC5XGa4I, https://www.youtube.com/watch?v=SYimClX7fmg, https://www.youtube.com/watch?v=xpPjQY-rwxU |
| OfferUp | "Dreams Start Here" anthem: first tools, someone starting out, warm music, few words | https://www.youtube.com/watch?v=VlksqSgbWVg and https://about.offerup.com/letter-from-our-ceo-campaign-2025 |
| Mercari | "Pass It Forward" / goodbye-hello hand-off: one owner's old thing becomes another person's start | Rain (agency) official upload https://www.youtube.com/watch?v=1TXBujbzJ0U and Mercari's PR Newswire release |
| Ritchie Bros (RB Global) | Seller framing: equipment "sitting idle" is money tied up; plain, grounded yard shots | Ritchie Bros official Shorts https://www.youtube.com/shorts/vyLLcQGNjqs, https://www.youtube.com/shorts/wdkW00AUeqA, https://www.youtube.com/shorts/OeB7xGdYnNE and https://blog.ritchiebros.com |

Nothing is a shot-for-shot copy: the items, scripts, shots and music are all ours.

## How a cut is made

1. `python3 assets.py <spec.json> <assetsdir>` renders captions (Space Grotesk Bold, blue bar), the phone bezel, walkthrough captions and end cards (wordmark and store badges cut from the v2 end card), vertical and wide.
2. Walkthrough frames come from the real app at the latest main (e901930, Nov 13: free-boost counter, location field, Ask YardSwaps and batch entries) (Expo web) recorded with `recording/rec_item.js`. API answers are mocked (`recording/mock.js`, demo user, scan result from `SCANF`), the screens are the real app. Start with `recording/app-up.sh` + `expo-up.sh`, undo with `app-down.sh`. Example: `OUT=raw/cyl PHOTO=img/cylinders.jpg SCANF=part2-scan.json UPIMG=img/cylinders.jpg PUBY=90 node rec_item.js`.
   The walkthrough ends on the "Your listing is live" frame, because the screen under it lists paid boost prices and ads never show paid boosts.
3. `python3 build.py <spec.json> v|w <assetsdir> <clips> <frames> <music.mp3> <out.mp4> [vo.json]` cuts the shots (clips trimmed, stills get a slow 1.0 to 1.025 push), 0.3 s dissolves, the walkthrough, the end card, music from `music_start`, loudness to -14 LUFS.
   Wide (16:9) puts the vertical shot as a full panel on a blurred, dimmed copy of itself, so nothing is cropped.

## Generation

ElevenLabs flow `6WCgIdqxjW2UXiR6DUM9` (grant credits): Nano Banana Pro keyframes from the real listing photos in `../*/source/photos/`, Veo 3.1 clips (6 s, 9:16, locked-off tripod, nothing running), Eleven Music tracks.
The grant's image/video budget ran out on Nov 14 during this work (402 grant_budget_exceeded), so two shots (first-set "Their first one", didnt-leave "No auction date") are keyframe stills with a slow push, and the wide cuts use the panel layout instead of new 16:9 generations. Raw clips stay on the flow, not in git.
