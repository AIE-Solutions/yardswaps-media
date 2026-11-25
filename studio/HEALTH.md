# Account health, 2026-11-25T13:58:26Z

Policy: `pause` (studio/health-policy.json). Scores 0-10 from measurable facts; level sets the daily cap.

| Platform | Score | Level | Cap a day | Ours a day now | Paused until |
|---|---|---|---|---|---|
| Instagram | 3.0 | low | 2 | 7.0 |  |
| Facebook | 6.5 | regular | 7 | 6.0 |  |
| Threads | 6.0 | regular | 7 | 0.0 |  |
| TikTok | 6.0 | regular | 2 | 1.6 |  |
| YouTube | 6.0 | regular | 2 | 0.4 |  |

## Instagram
- followers 826 -> 809 in a week (-2.1%)
- likes+comments per post 2.0 -> 0.9 (0.46x)
- views a week, all posts 2295 -> 3273 (1.43x)
- views per post 71 -> 57 (0.80x)
- 49 of our posts in 7 days (7.0 a day), 0 failed

Fixes:
1. Followers are falling: post fewer, better clips here and answer every comment for a few days.
1. Each post gets less engagement than it did: repeat the best openers (metrics/rank.json boost) and retire the weakest.

## Facebook
- followers 14 -> 15 in a week (+7.1%)
- 42 of our posts in 7 days (6.0 a day), 0 failed

Fixes:
1. Profile fields that don't match profiles.json: description.

## Threads
- 0 of our posts in 7 days (0.0 a day), 0 failed

Fixes:
1. None of our posts went out here in 7 days: check the poster's token and that its slot fires.

## TikTok
- 11 of our posts in 7 days (1.6 a day), 1 failed

## YouTube
- 3 of our posts in 7 days (0.4 a day), 1 failed
