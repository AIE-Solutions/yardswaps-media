# Agent prompts (canonical copies)

The shared project folder (/mnt/project-files/yardswaps-campaign/growth-loop/) is at its storage cap and silently lost prompt edits on 2026-11-20. The prompts below are the canonical versions. If a project-file copy differs or looks cut off, this repo wins. Agents read these with the GitHub tools (AIE-Solutions/yardswaps-media, branch main).

| File | Agent | Schedule (Central) |
|---|---|---|
| ROSTER-KEEPER-PROMPT.md | Roster Keeper: checks every agent on roster.json ran, rebuilds the status page, routes problems | 6:53 am + 5:53 pm daily |
| PLATFORM-OPS-PROMPT.md | Platform Ops: daily health, safety and routing | 3:37 am daily |
| REPLY-HANDLER-ADMIN-STEPS.md | Reply Handler steps 9 to 11: admin follow-ups and the daily posting-rules review (steps 1 to 8 stay in the project file) | 12:17 + 5:17 pm daily |
| STOREFRONT-CARE-PROMPT.md | Storefront Care: address and logo nudges, one storefront welcome post a day | 1:13 pm daily |
| BILLING-WATCH-PROMPT.md | Billing Watch: founding discount on every storefront trial before its first charge, failed payments (read-only on Stripe) | 9:07 am daily |
| BLOG-WRITER-PROMPT.md | Blog writer: one article a day for yardswaps.com/blog through the agent blog API (our HeyCatch blog replacement) | 10:20 am daily |

Owner: Growth Lead thread. Edit here by PR; never put secrets or keys in these files.

Words (Alan 11-21, "consistency is key"): the paid plan is the "Storefront plan", never "Dealer plan"; its boosts are "Storefront boosts" and its trial is the "storefront trial". Say "storefront" for the product. Use "dealer" only for who it is for ("storefronts for dealers"), plus the buyer-facing "Dealer" chip and "Verified Dealer" badge, which keep their names. Links and ids stay as they are (/account/dealer?start=1, /dealers, dealer_monthly). Every new agent prompt carries this line.

Message (Alan 11-21, "a clear precise message"): every line a seller, dealer or buyer reads follows MESSAGING.md at the root of this repo (AIE-Solutions/yardswaps-media, main): the one-line pitch, what each audience hears, the offer word for word, the word list and the do/don't rules. Read it before writing any copy; it wins over older copy notes. Every new agent prompt carries this line too.

End card (Alan 11-25): every video we make or post ends on the YardSwaps end card in brand/endcard/ of this repo (blue card, wordmark, App Store and Google Play badges, link; about 2 seconds). Storefront clips use the storefront version, never the "Free to list" one. Run `python3 brand/endcard/endcard.py add IN.mp4 OUT.mp4 [seller|dealer]` on anything you cut; the Reels, TikTok and Shorts posters skip a clip without it. Every new agent prompt that makes or posts video carries this line.

Re-cuts (guard eval #37, 11-25): a re-cut of an existing ad gets its own words-vs-screen sheet and a fresh screen recording before it enters rotation. Log the sheet in motion/audit/ and record any app or site screen from the live page that day, so old labels (for example "Dealer plan", now "Storefront plan") never go back out.

## The workforce (Alan 11-25: "Build our agent workforce to take on all these new corporate tasks to keep everything flowing")

`roster.json` lists every agent that runs the company: what it does, when (Mountain time, Alan's), what runs it (a scheduled task, a GitHub workflow, app code or a paid tool), its prompt, its owner and how we know it worked. The Roster Keeper reads it twice a day and publishes the status page https://claude.ai/artifact/LqHZjy1HennvyA5GaA2L3r, built by `roster_status.py` from `roster.json` and `logs/roster-state.json`.

Every agent, old or new, keeps this contract:

1. **One row in roster.json**, added by PR in the same change that adds the agent. A new scheduled task puts its `trig_` id in `runner.ref`; a new workflow puts its file name. No row, no agent.
2. **A prompt file** here (or in the project growth-loop folder for the older agents) that starts with why it exists in Alan's words, its hard limits, and numbered steps ending in a log row.
3. **A heartbeat as its last call**: `POST https://www.yardswaps.com/api/agent/heartbeat` with header `X-Agent-Name: <its roster heartbeat name>` and body `{"status": "ok" | "did_work" | "needs_alan" | "failed" | "skipped", "summary": "<one line, no emails or phone numbers>", "runUrl": "<a claude.ai, github.com or yardswaps.com link, optional>"}`. The proxy adds the token; never handle or print one. `GET /api/agent/heartbeats?days=7` reads them back. Until the endpoint is live (app PR #536) a 404 is fine: carry on.
4. **Hard limits** (all agents): no spend, no investor contact, no deleting data or removing listings, no Stripe or console changes, no subscription cancellations, no bans (Alan's call). Copy follows MESSAGING.md; never Alan's personal name in anything users read; every video ends on the end card.

Where the Roster Keeper routes a problem (`mcp__hearthbot__message_thread`):

| Owner on the roster | Thread |
|---|---|
| Growth Lead thread, Dealer Loader thread, Comments thread, Ops Sweep, and any owner not listed below | cmsg_016mY3okhLzJ4WqTxD4bzJNbMNcmYogtEDPDsqtMUU7zB3 |
| Agent workforce thread, Billing Watch | cmsg_016mY3okhLzJ4WqTxD4bzJNbPi1XLUw2NjMNAMc4EaVSC1 |
| Studio thread | cmsg_016mY3okhLzJ4WqTxD4bzJNbYNdzGu8R4YbJRVjVaNpnMg |
| Storefront rollout thread | cmsg_016mY3okhLzJ4WqTxD4bzJNbDdeo8HKnP6r982expD9Krx |
| Paid tools (Soro, Zapier) | cmsg_016mY3okhLzJ4WqTxD4bzJNbFGJwfXo27DzyccMLW8yWTY |

Logs live in `logs/` (one markdown file per agent, newest row on top; `roster-state.json` is the Roster Keeper's last check). Paused on purpose (2026-11-25): the Wed/Fri/Sun comment sweep (duplicated the daily Comment replies) and the October weekly video pickup (it wiped this repo after each push). Don't turn them back on.

