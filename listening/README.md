# Weekly listening list

Item 7 of the agency playbook (2026-11-08): every week, a list of people asking in public to buy or sell used work equipment, each with a draft reply. Free. Nothing is posted automatically; a person replies by hand, as the business, only where the place's rules allow it.

## How a week runs

1. **Monday 6:15 am Central**, `.github/workflows/listening.yml` runs `listen.py`. It reads the public feeds in `sources.json` (subreddit RSS, Reddit search RSS, trade-forum RSS, Bluesky's public search), keeps posts from the last 8 days that show buy or sell intent and name equipment, maps each to a YardSwaps category, and writes:
   - `latest.json`: every kept post, sellers first, with source status;
   - `YYYY-MM-DD.md`: the reading list with a draft reply under each post.
2. The Monday report picks up the count and the file; a copy goes to the project files as `yardswaps-campaign/listening/LISTENING-YYYY-MM-DD.md`.
3. Alan (or whoever has the time) opens each post, checks the place's rules, and pastes or adapts the draft.

Pull requests that touch `listening/` run in probe mode: the job summary shows what every source returned and nothing is committed.

## Reply rules

Same as the daily comment replies (`comments/README.md`): as the business, plain, no emoji, answer their question first, say we run YardSwaps, never promise prices, views, buyers, sales, availability or shipping. Sellers come first (supply is the bottleneck). Buyer replies say plainly that it's early and there may not be one near them yet.

Links: most subreddits and trade forums remove self-promotion, so the default draft has no link. A link version (tagged per `UTM-LINKS.md`, campaign `listening_<category>`) appears only for sources marked `links_ok` in `sources.json`. Never DM people to promote, and don't reply to the same person twice.

## Adding a source

Add a subreddit name to `reddit_subs`, a forum feed to `forums` (XenForo forums: `/forums/-/index.rss`; Discourse: `/latest.rss`), or a phrase to `bluesky_queries`. Open a PR: the probe run shows whether the feed answers from GitHub Actions.

Facebook groups, where most of this talk happens, have no public feed; they stay manual.
