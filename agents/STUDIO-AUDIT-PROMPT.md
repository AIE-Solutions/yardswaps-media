# Studio audit: weekly scored check of the site, SEO and GEO, and the app listings

Our version of HeyCatch's "Marketing fixes", "Technical SEO and GEO" and "App Store listing" audits (Alan
2026-11-25: "End to end a clone of heychat"). The script scores the site out of 100 and ranks each fix by the
points it wins back, with a prompt to paste into a coding agent. Results land in `studio/audits/` in this repo,
and yardswaps.com/admin/studio shows them. It only reads public pages and files. It costs nothing, and it never
changes the site.

## Each run

1. Make shallow, sparse clones of both repos:
   - AIE-Solutions/Marketplace (main): `scripts/`, `apps/web/lib/data/copy-rules.json`,
     `apps/mobile/asc-runbook/paste/`, `apps/mobile/play-console-runbook/paste/` and `apps/mobile/store/screenshots/`.
   - AIE-Solutions/yardswaps-media (main): `studio/audits/` and `MESSAGING.md`.
2. **Competitors (optional).** If a Firecrawl scrape tool is available and has credits, save the raw HTML of
   https://www.machinerytrader.com/ and https://www.equipmenttrader.com/ to `/tmp/competitors/machinery-trader.html`
   and `/tmp/competitors/equipment-trader.html`. Use one call each and never retry. If there is no Firecrawl,
   skip this step: the audit marks the competitors as not reachable.
3. In the Marketplace clone, run
   `NODE_USE_ENV_PROXY=1 node scripts/studio-audit.mjs --out <media clone>/studio/audits --competitors-dir /tmp/competitors`.
   It takes a few minutes, because it crawls every sitemap page. It prints one summary line.
4. Commit `studio/audits/audit-<date>.json`, `studio/audits/latest.json` and `studio/audits/AUDIT.md` to main of yardswaps-media with the
   message `Studio audit <date>: <summary line>`. Push, and if the push is rejected, retry after `git pull --rebase`
   up to 3 times. Change no other file.
5. **Route the fixes.** Send the coordinator one message with `mcp__hearthbot__message_coordinator`. It holds
   the summary line, the change since the last audit, and the top 5 fixes from AUDIT.md, each with its points
   and prompt. Ask the coordinator to give each fix to the thread that owns the area:
   - site pages and SEO go to the website thread
   - store listing fields go to the app release thread
   - article rules go to the Studio blog writer prompt
   Never change the site, a listing or a prompt yourself in this run.
6. **Heartbeat, always the last call**, also on a run that stopped early:
   `POST https://www.yardswaps.com/api/agent/heartbeat` with header `X-Agent-Name: studio-audit` and JSON
   `{"status": "did_work" | "failed", "summary": "<the summary line, or why it stopped>", "runUrl": "<this session's link if you have one>"}`.

## Rules
- Read only. No posting, no form submits, no spend, no contact with anyone.
- The proxy adds the agent token for www.yardswaps.com. Never handle, print or write a token.
- If the crawl fails (the site is down, or more than half the pages error), commit nothing, tell the coordinator,
  and send a `failed` heartbeat.
