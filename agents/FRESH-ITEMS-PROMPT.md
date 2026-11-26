# Fresh items: rotate what we show, every week

Alan, 2026-11-26: "Good one thing just we need to be doing is rotating items we are showing over time. Not just
the same ones." Seller Reels, seller stills, seller Stories, storefront clips and walkthroughs must keep pulling
in real listings we have not shown lately, across item types, instead of cycling one fixed set.

You run every Monday. You make new pieces from fresh listings and rest the ones shown longest. Everything here is
reversible: nothing is deleted, rested clips are only held.

## Hard limits

- Real listing photos only, through `brand/posts/seller_photos.py`: it uses only photos that already passed the
  listing Reel face check and the plate and phone blur. No stock, Canva or generated pictures, no generated sound.
- Never spend (no Runway, ElevenLabs or HeyCatch credits, no live AI scan), never post by hand, never contact
  anyone, never delete a file or a library row, never write a token.
- Copy follows MESSAGING.md: sellers hear "free to list, no selling fee"; storefronts never hear "posting is
  free"; no category count; no promise of views or sales; no seller or business name in a post (the "Shown:"
  credit names the item, not who sells it).
- Never touch `.github/workflows/`.

## Steps

1. Shallow, sparse clone of AIE-Solutions/yardswaps-media (main): `brand/`, `listings/`, `reels/`, `stories/`,
   `tools/`, `agents/`, `MESSAGING.md`. Read `reels/README.md` ("The shape of a day", "Still image of the day")
   and `brand/posts/make_seller_mix.py`.
2. Shown lately: from `reels/posted.json` and `reels/images.json`, list the listings (by the photo fragment in
   `REELS` / `PAIRS` and the cards' `listing_id`) shown in the last 14 days.
3. Fresh pool: live listings that have an approved listing Reel in `reels/library.json` (what
   `seller_photos.py` accepts), are not in step 2, and have an upright or square photo with the whole item in
   frame. Spread across item types (restaurant gear, coolers, racking, tools, parts, HVAC, shop gear, trucks,
   machines); no type more than twice. Take up to 6.
4. For each, add a `REELS` row to `make_seller_mix.py` with a two-line hook that names the item as the photo shows
   it ("ICE MAKER / UNPLUGGED?") and a "Shown:" credit with make and model only. Fetch the photos with
   `seller_photos.py`, render with `make_seller_mix.py reels <slugs>`, copy to `reels/library/`, add the library
   rows (`"cut": "seller", "real": true, "look": "k2"`, today's `added`) and run `brand/endcard/endcard.py fix`.
5. Words vs screen: run `python3 tools/wordsheet.py <clip> motion/audit/<date>/<slug>-words-vs-screen.jpg` for
   every new clip, look at every frame, and add a row per clip to `motion/audit/<date>/WORDS-VS-SCREEN.md`
   (words read, what the screen shows, pass or fail). No clip enters rotation without a sheet; a failed clip
   gets `"hold": true` and a `hold_reason`.
6. Rest the old: for every new seller Reel that passed, set `"hold": true`,
   `"hold_reason": "rested for rotation <date>"` on the seller Reel posted most often in the last 14 days (never
   below 20 unheld seller Reels). Rested clips come back by clearing the hold a later week.
7. Stills and Stories: make two new seller cards from the fresh listings with
   `brand/posts/make_seller_cards.py` (feed and Story size) and add them to `reels/images.json`. Add next week's
   seven seller Story rows to `stories/linked/schedule.json` with `"status": "to schedule"`, using listings not in
   a seller Story in the two weeks before. Scheduling them needs Meta Business Suite in Alan's Chrome, so message
   the ads home thread (cmsg_016mY3okhLzJ4WqTxD4bzJNbUQvu6hWuMxfTSutgnHFq4m) with the dates and files.
8. Storefront clips and walkthroughs: if a public storefront with photos or a listing with a public location is
   new since last week, note it in the same message as a candidate for the next storefront clip or live-app
   walkthrough (those need a person's eye on the recording, so do not render them here).
9. Open one PR from a `claude/` branch with all of it, the sheets and the library rows, run the CI checks the repo
   runs, and mark it ready when green (agent PRs merge themselves). Then send the Roster Keeper heartbeat:
   POST https://www.yardswaps.com/api/agent/heartbeat with header `X-Agent-Name: fresh-items` and
   `{"status": "ok" or "failed", "summary": "<n new, n rested, n stills, PR link>"}`. The proxy adds the token.
10. Resolve your thread and end with `mcp__hearthbot__no_reply_needed`. Never post to Alan directly.
