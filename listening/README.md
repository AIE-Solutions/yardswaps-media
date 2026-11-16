# Weekly listening list

Item 7 of the agency playbook (2026-11-08): every week, a list of people asking in public to buy or sell used work equipment, each with a draft reply. Free. Nothing is posted automatically; a person replies by hand, as the business, only where the place's rules allow it.

## How a week runs

1. **Every day at 6:15 am Central**, `.github/workflows/listening.yml` runs `listen.py`. It reads the public feeds in `sources.json`: one Reddit search across 20 trade subreddits (Reddit refuses a second anonymous search from GitHub within minutes, so buyers and sellers share one query) and nine trade-forum RSS feeds. It keeps posts that show buy or sell intent and name equipment, maps each to a YardSwaps category, and adds them to a rolling 8-day pool. The forum feeds only hold a day or two, which is why it runs daily.
   - `latest.json`: the pool, sellers first, with each source's status on the last run;
   - `LIST.md`: the same as a reading list with a draft reply under each post.
2. On Mondays the report points to `LIST.md` with the count, so the week's list is in one place.
3. Alan (or whoever has the time) opens each post, checks the place's rules, and pastes or adapts the draft.

A post counts when the intent is in its title ("WTB", "for sale", "where to sell", "looking for a used"), or when the body shows intent and the title names the equipment. Intent words deep in a long thread are mostly noise.

Pull requests that touch `listening/` run in probe mode: the job summary shows what every source returned and nothing is committed.

## Reply rules

Same as the daily comment replies (`comments/README.md`): as the business, plain, no emoji, answer their question first, say we run YardSwaps, never promise prices, views, buyers, sales, availability or shipping. Sellers come first (supply is the bottleneck). Buyer replies say plainly that it's early and there may not be one near them yet.

Links: most subreddits and trade forums remove self-promotion, so the default draft has no link. A link version (tagged per `UTM-LINKS.md`, campaign `listening_<category>`) appears only for sources marked `links_ok` in `sources.json`. Never DM people to promote, and don't reply to the same person twice.

## Adding a source

Add a subreddit name to `reddit_subs`, or a forum feed to `forums` (XenForo forums: `/forums/-/index.rss`; Discourse: `/latest.rss`). Open a PR: the probe run shows whether the feed answers from GitHub Actions.

Not covered: Facebook groups (no public feed; most of this talk happens there, so they stay manual), Craigslist wanted ads (no feed since 2024), X and Bluesky (search needs a paid or signed-in API; Bluesky's public search refused GitHub's runners, tested 11-08).
