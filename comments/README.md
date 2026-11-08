# Daily comment replies

Every day, as the business, free. Set up 2026-11-08 (Alan: "Daily comments would be gold"); replaces the Wed/Fri/Sun Zapier sweep.

## How a day runs

1. **~9:50 am Central** (`.github/workflows/comments.yml`, mode `fetch`): `meta_comments.py` reads every Instagram post and Facebook Page post and Reel from the last 30 days with the Reels token and writes the comments nobody from YardSwaps has answered to `inbox.json` (plus follow-ups written after our last reply in a thread). Comments in `seen.json` are left out. No Zapier tasks.
2. **11:41 am Central**, the "YardSwaps daily comment replies" scheduled task (a Claude run):
   - reads `inbox.json`, and YouTube comments through Zapier (one read);
   - writes one reply per real comment (rules below);
   - Instagram and Facebook replies go to `outbox.json` when `inbox.json` `can_reply` says the token allows it; otherwise Instagram replies go out through Zapier's Instagram connection and Facebook replies go into the digest for Alan to paste;
   - YouTube replies go out through Zapier;
   - comments it decides not to answer (spam, bots, needs Alan) go into the outbox as `{"comment_id", "platform", "skip": true, "why"}` so they aren't offered again;
   - writes the day's digest to `/mnt/project-files/yardswaps-campaign/comments/DIGEST-YYYY-MM-DD.md` and logs every reply in `COMMENT-LOG.md`.
3. **On the push to main** (mode `post`): the workflow posts the outbox replies, records them in `seen.json` and empties the outbox. A refused reply is retried once the next day, then marked `failed`.

## Files

| File | Written by | What |
|---|---|---|
| `inbox.json` | workflow (fetch) | `fetched_at`, `can_reply` per platform, token `scopes`, `errors`, `items[]` with `platform`, `comment_id`, `reply_to`, `author`, `text`, `time`, `post`, `permalink`, optional `thread` |
| `outbox.json` | daily task | `[{"platform", "comment_id", "reply_to", "reply"}]` or `{"platform", "comment_id", "skip": true, "why"}` |
| `seen.json` | workflow (post) | every comment id we replied to, skipped or failed on |

## Platforms

| Platform | Read | Reply |
|---|---|---|
| Instagram | Reels token (free) | Reels token once it has `instagram_manage_comments`; until then Zapier (2 tasks a reply) |
| Facebook | Reels token (free) | Reels token once it has `pages_manage_engagement`; until then drafted in the digest |
| YouTube | Zapier, 1 read a day | Zapier |
| LinkedIn | Not possible: reading comments needs LinkedIn's Community Management API (refused on our connection, tested 11-08) | Alan, from the LinkedIn app; the digest has reply drafts for the questions people usually ask |
| TikTok | No API for our account (Buffer only posts) | Alan, from the TikTok app; same drafts |
| X | Free API can't read replies | Same |

## Reply rules

As the business. One or two short sentences, plain, no emoji, no hashtags. Answer what they asked first. Seller-first where it fits, and end with a short open question about their own gear when it fits naturally (not on every reply). Facts we may use: YardSwaps is a free US marketplace for used industrial and commercial equipment and parts; listing is free with no cut of the sale; add photos and AI fills in the listing; the first 4 listings in 14 days are boosted free; every deal is a local pickup and the buyer pays the seller directly after inspecting; iPhone, Android or yardswaps.com; questions to support@yardswaps.com. Never promise prices, views, buyers, sales, availability or shipping. Skip spam, bots, link drops and abuse. Complaints, legal or safety issues, private details or anything that needs Alan: no reply, it goes in the digest.

## Leads

A comment is a lead when someone says they have something to sell, want to buy or are looking for something specific, asks for a price, or is a dealer or rental yard. Leads get a normal public reply (pointing sellers to free listing and buyers to searching or saving a search), and also go at the top of the digest with a link to the comment, so Alan can follow up in a DM as the business. The run posts in the project only when there is a lead or something that needs Alan.
