# LIST IT FREE daily Story

Alan approved (2026-11-08) one Instagram Story a day, ~9:30 am Central, with a
fixed template. Only the machine changes by weekday:
Mon generator, Tue conveyor oven, Wed dump trailer, Thu walk-in cooler,
Fri ice machine, Sat zero-turn mower, Sun scissor lift.

Template (character-for-character, see `render_story.js`):
- Headline: `LIST IT FREE`
- Body: `That {machine} in the yard is worth money. Snap a photo — AI drafts the listing.`
- Link line (printed, not tappable; Alan's pick 2026-11-08 because the Graph API
  cannot add link stickers): `List yours free on YardSwaps` with
  `yardswaps.com/sell-equipment` under it, lower third
- Footer: `No commission · Local pickup · yardswaps.com`

## How it runs
- A Claude scheduled task dispatches `.github/workflows/story.yml` with
  `publish=true` at ~9:30 am Central (cron at 14:30 and 15:30 UTC; the task only
  dispatches when Central time is 9:15-9:45, so DST needs no edits).
- `publish_story.py check` stops quietly if `stories/posted.json` already has
  an entry for today (Central). The API can't read Story text, so the log is the
  record of what we posted.
- `make_bg.py`: today's machine and a 9:16 AI backdrop (reuses today's file,
  else BG_URL, else Runway gen4_image 1080:1920, about 8 credits). Illustrative
  only, never a real listing. No people, text or logos.
- `render_story.js` -> `stories/out/<date>-<machine>-story.jpg`, committed, then
  published from its raw.githubusercontent URL (pinned to the commit) as an
  Instagram Story only. One attempt per day; failures are logged, not retried.
- After publishing, the script confirms the media id is in the account's active
  Stories and logs `expires` (24 h later).
