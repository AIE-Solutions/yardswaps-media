> **Nov 28 (Alan, of a Story with a tappable link sticker: "Make sure all still images have this"): this
> automatic Story is OFF.** The Graph API cannot add a link sticker, so it could only post with no link.
> `publish_story.py check` now always skips (`AUTO_STORY = False`). Every still Story is a linked one from
> `stories/linked/schedule.json`, scheduled by hand in Meta Business Suite with the sticker on. A week with no
> linked Stories scheduled has no still Stories at all, so schedule the next week before the current one ends.

# LIST IT FREE daily Story

> **Nov 26 (Alan: our posts "look like ai slop"): the Story now sits on a real photo from a live listing.**
> `make_bg.py` picks an approved "Just listed" photo (`listings/queue.json`, never shown in a Story first, newest
> first, only listings still live) and `render_story.js` draws it in the post kit look (`brand/posts/README.md`):
> white and blue (look k2): a light strip, the photo with nothing over it, then on white the blue tag "LIST IT FREE",
> the headline "Sitting idle?", the body "Snap a photo and the AI writes the listing. No selling fee. Local pickup.",
> the wordmark with `yardswaps.com/sell-equipment`, and a small "Shown: listing · price" line. No AI backdrops, no Runway, no bank: with no approved
> photo there is no Story that day. The bank and template notes below describe how it worked before.

Alan approved (2026-11-08) one Instagram Story a day, ~9:30 am Central, with a
fixed template. Only the machine changes. Until 2026-11-21 it changed by weekday
(Mon generator, Tue conveyor oven, Wed dump trailer, Thu walk-in cooler,
Fri ice machine, Sat zero-turn mower, Sun scissor lift). Since 2026-11-21
`make_bg.py` picks it by the machine rotation (`rotation/README.md`): among the
`stories/bank/<machine>/` folders that still hold images, the one shown longest ago,
preferring a machine and category not posted anywhere in 14 days. The weekday
machine is only the fallback. A new bank folder (any approved machine slug) adds a
machine to the rotation, so refills should add new machines, not only top up these 7.

Template (character-for-character, see `render_story.js`):
- Headline: `LIST IT FREE`
- Body: `That {machine} in the yard is worth money. Snap a photo — AI drafts the listing.`
- Link line (printed, not tappable; Alan's pick 2026-11-08 because the Graph API
  cannot add link stickers): `List yours free on YardSwaps` with
  `yardswaps.com/sell-equipment` under it, lower third
- Footer: `No commission · Local pickup · yardswaps.com`

## How it runs
- A Claude scheduled task dispatches `.github/workflows/story.yml` with
  `publish=true` at ~9:27 am Central (cron at 14:30 and 15:30 UTC; the task only
  dispatches when Central time is 9:15-9:45, so DST needs no edits).
- Backup (since 2026-11-23, after the task's dispatch was refused on 11-22 and
  11-23): the workflow's own GitHub schedule runs every 10 minutes from 14:07 to
  17:57 UTC. A cheap `gate` job reads `stories/posted.json` and stops the run
  when today's Story is already handled. Schedule runs always publish, but
  `check` skips any run outside 9:20 am-noon Central (`WINDOW_CT`), so a late
  GitHub cron never posts in the afternoon. Each run checks out the branch tip,
  so a run queued behind another sees the Story that one just logged.
- `publish_story.py check` stops quietly if `stories/posted.json` already has
  an entry for today (Central). The API can't read Story text, so the log is the
  record of what we posted.
- `make_bg.py`: today's machine and a 9:16 AI backdrop: today's file if it
  exists, else the oldest unused image in `stories/bank/<machine>/` (each used
  once, then moved to `stories/out/`), else BG_URL, else Runway gen4_image
  1080:1920 (8 credits; only 27 left on 11-08).
- Bank refill: make 9:16 2K images with ElevenLabs (gpt-image-2.5-sunburst),
  then run `story-bank.yml` with lines of `<machine-slug> <url>` within a few
  hours (the signed URLs expire). Illustrative
  only, never a real listing. No people, text or logos.
- `render_story.js` -> `stories/out/<date>-<machine>-story.jpg`, committed, then
  published from its raw.githubusercontent URL (pinned to the commit) as an
  Instagram Story only. One attempt per day; failures are logged, not retried.
- After publishing, the script confirms the media id is in the account's active
  Stories and logs `expires` (24 h later).
