# Metrics: the weekly scorecard and what it changes

One loop, free, no weekly action from anyone:

1. **Daily 12:10 UTC** (`.github/workflows/metrics.yml`): `collect_meta.py` snapshots Instagram and Facebook with the Reels token (`META_PAGE_TOKEN`): follower counts, and every IG post of the last 45 days (ours and HeyCatch's) with likes, comments and the Reel insights the token allows; our Facebook Reels likes/comments. Saved to `meta/YYYY-MM-DD.json`.
2. **Every Monday morning** the "YardSwaps Monday YouTube report" run writes `inputs/YYYY-MM-DD/`:
   - `growth.json`: the app's newest `[GrowthDigest]` line from the Railway logs (Marketplace service, filter `GrowthDigest`): signups by source, campaign and "heard about us", zero-result searches and terms, category coverage, outreach by segment and step.
   - `ops.json`: the newest `[OpsDigest]` line.
   - `youtube.json`: `{"channel": {"subscribers", "views"}, "videos": [{"id", "title", "views", "subscribersGained", "ours", "slug"}]}` from Metricool / the Zapier Get Report it already pulls.
   - `metricool.json` (optional): any other per-network numbers it pulled.
   The push triggers the workflow again.
3. `scorecard.py` builds `scorecard.json`, `SCORECARD.md`, `history.csv` and `rank.json`.

## What it changes on its own
- **Reels and TikTok repeats** (`reels/post_reels.py`, and `post_tiktok.py` through the same `pick`): `rank.json` `boost` pushes the 3 best settled Reels up the repeat order; `retire` stops repeating a Reel that scored under 0.4x the median over 2+ settled Instagram posts (at most 3 per run, never below 12 usable videos, never one that brought a signup). While `rank.json` is fresh (under 8 days old) the hand-set `boost` numbers in `reels/library.json` are ignored, unless the entry has `"boost_keep": true`.
- **Monday batch** reads `scorecard.json` `actions.buildNext` (winning opener shapes and topics, the categories buyers search for and find empty, shapes to stop making) and `youtube.bestTitleShape` for titles and the order of the week; retired slugs go back to Motion to be rebuilt.

## Scoring
Points per post = follows x10 + shares x4 + saves x3 + comments x3 + likes x1 + views/100, plus 25 per app signup from that Reel's tagged Facebook link (`utm_campaign=reels_<slug>`). A post is judged after 48 hours. Formats (`formats.json`: hook = opener shape, angle = topic, category = app category id) get a verdict after 3 settled posts: winner at 1.3x the median, loser at 0.6x. Every new slug gets a `formats.json` row in the Monday batch's push.

## Limits
- Store installs (App Store Connect, Play Console) are not read; app signups on iOS/Android are the proxy.
- Follows/shares/saves per Reel need `instagram_manage_insights` on the token (added at the Dec renewal). Until then the snapshot's `insights.refused` lists what Meta refused and the score runs on likes, comments and views.
- TikTok numbers are not readable (Metricool's TikTok link is stale).
