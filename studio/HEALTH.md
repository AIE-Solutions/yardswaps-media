# Account health, 2026-11-28T14:37:40Z

Policy: `pause` (studio/health-policy.json). Scores 0-10 from measurable facts; level sets the daily cap.

| Platform | Score | Level | Cap a day | Ours a day now | Paused until |
|---|---|---|---|---|---|
| Instagram | 6.0 | regular | 7 | 7.7 |  |
| Facebook | 6.5 | regular | 7 | 6.9 |  |
| Threads | 6.0 | regular | 7 | 0.0 |  |
| TikTok | 4.0 | low | 0 | 1.1 | 2026-11-29T14:44:33Z |
| YouTube | 6.0 | regular | 2 | 1.1 |  |

## Instagram
- followers 809 -> 798 in a week (-1.4%)
- likes+comments per post 1.7 -> 2.0 (1.21x)
- views a week, all posts 2576 -> 3777 (1.47x)
- views per post 65 -> 63 (0.97x)
- 54 of our posts in 7 days (7.7 a day), 2 failed
- platform warning cleared by a later post: POST https://graph.facebook.com/v23.0/17841429324062623/medi

Fixes:
1. Followers are falling: post fewer, better clips here and answer every comment for a few days.

## Facebook
- followers 14 -> 18 in a week (+28.6%)
- 48 of our posts in 7 days (6.9 a day), 0 failed

Fixes:
1. Profile fields that don't match profiles.json: description.

## Threads
- 0 of our posts in 7 days (0.0 a day), 0 failed

Fixes:
1. None of our posts went out here in 7 days: check the poster's token and that its slot fires.

## TikTok
- 8 of our posts in 7 days (1.1 a day), 2 failed
- platform warning: TikTok flagged this post as potential spam and blocked it from publishing. Pleas

## YouTube
- 8 of our posts in 7 days (1.1 a day), 1 failed
