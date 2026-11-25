# Studio deck sync: apply approve / skip from yardswaps.com/admin/studio

Our version of HeyCatch's daily swipe deck (Alan 2026-11-25: "End to end a clone of heychat"). New Studio
clips wait in reels/library.json with `"review": "pending"` and `"hold": true` until an admin approves or skips
them on yardswaps.com/admin/studio. This run copies those decisions into the library so the posters act on
them. It costs nothing and sends nothing to anyone.

## Each run

1. `git pull` on main of AIE-Solutions/yardswaps-media.
2. `curl -sS -H "X-Agent-Name: studio-deck" https://www.yardswaps.com/api/agent/studio -o /tmp/decisions.json -w "%{http_code}"`
   (the proxy adds the agent token; never handle or print a token). **If the answer is not 200, stop here**:
   do not run the sync, because without the decisions it could auto-approve a clip the owner skipped. Send the
   heartbeat with status `failed` and the HTTP code.
3. `python3 studio/sync_deck.py /tmp/decisions.json`. It prints one summary line.
4. If `git status` shows reels/library.json or studio/deck-state.json changed, commit them to main with the
   message `Studio deck sync <UTC time>: <summary line>` and push (retry a rejected push after `git pull --rebase`,
   up to 3 times). Change no other file.
5. **Morning run only (the 7:35 am Mountain run): account health.** Read Instagram views from Metricool
   (brand 7684598, Instagram evolution metrics IGEV23 reels views and IGEV22 reels count, by day, Central): last 7
   full days and the 21 days before. Write them to `studio/health-inputs.json` in the same shape it has now
   (`views7d`, `viewsBeforePerWeek`, `viewsPerPost7d`, `viewsPerPostBefore`) with `readAt` set to now in UTC. If
   Metricool is not reachable, leave the file alone (health.py ignores numbers older than 4 days). Then run
   `python3 studio/health.py` and commit `studio/HEALTH.md`, `studio/health.json` (the Social tab of /admin/studio reads it) and `studio/health-inputs.json` with the message
   `Account health <UTC date>: <one line per platform score>`. Never edit `studio/health-policy.json`: how
   strictly health limits posting is the owner's choice.
6. **Heartbeat, always the last call**, also on a run that stopped early:
   `POST https://www.yardswaps.com/api/agent/heartbeat` with header `X-Agent-Name: studio-deck` and JSON
   `{"status": "did_work" | "ok" | "failed", "summary": "<the summary line, or why it stopped>", "runUrl": "<this session's link if you have one>"}`.
   `did_work` when something changed, `ok` when nothing did.

## Rules
- Only `studio/sync_deck.py` edits the library in this run. Never edit captions, hooks or holds by hand.
- Never post, delete a clip file, or touch another repo or service. Metricool is read only.
- If the summary says a clip is waiting for review for more than a day, that is normal: the sync auto-approves
  it on the run after its 24 hours are up.
