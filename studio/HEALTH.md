# Account health, 2026-11-26T14:37:26Z

Policy: `pause` (studio/health-policy.json). Scores 0-10 from measurable facts; level sets the daily cap.

| Platform | Score | Level | Cap a day | Ours a day now | Paused until |
|---|---|---|---|---|---|
| Instagram | 4.0 | low | 2 | 7.3 |  |
| Facebook | 6.5 | regular | 7 | 6.1 |  |
| Threads | 6.0 | regular | 7 | 0.0 |  |
| TikTok | 6.0 | regular | 2 | 1.6 |  |
| YouTube | 6.0 | regular | 2 | 0.7 |  |

## Instagram
- followers 828 -> 804 in a week (-2.9%)
- likes+comments per post 1.9 -> 1.0 (0.55x)
- views a week, all posts 2396 -> 3404 (1.42x)
- views per post 70 -> 57 (0.81x)
- 51 of our posts in 7 days (7.3 a day), 1 failed

Fixes:
1. Followers are falling: post fewer, better clips here and answer every comment for a few days.
1. Each post gets less engagement than it did: repeat the best openers (metrics/rank.json boost) and retire the weakest.

## Facebook
- followers 14 -> 16 in a week (+14.3%)
- 43 of our posts in 7 days (6.1 a day), 0 failed

Fixes:
1. Profile fields that don't match profiles.json: description.

## Threads
- 0 of our posts in 7 days (0.0 a day), 0 failed

Fixes:
1. None of our posts went out here in 7 days: check the poster's token and that its slot fires.

## TikTok
- 11 of our posts in 7 days (1.6 a day), 2 failed

## YouTube
- 5 of our posts in 7 days (0.7 a day), 1 failed
