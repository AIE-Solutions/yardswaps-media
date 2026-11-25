# YouTube Shorts poster (added 2026-11-23)

Alan, 2026-11-23: build our own YouTube uploader so Shorts keep posting while
Zapier is out of tasks (until about Dec 4) and Metricool is at its November
limit (resets Dec 1). YouTube had nothing new since Nov 16.

`.github/workflows/youtube-shorts.yml` runs `post_shorts.py`, which posts two
Shorts a day from `queue.json`: one between 10:00 and 11:00 am Central and one
between 4:00 and 6:30 pm Central (SHORTS-CADENCE.md slots, 90+ minutes clear of
HeyCatch's :33 posts). Free: GitHub Actions on this public repo plus Buffer's
free plan. Nothing runs on anyone's computer and nothing needs a Claude task.

## Why Buffer and not the YouTube Data API
Google locks every video that an unaudited API project uploads (`videos.insert`)
to private, and the channel owner can't make it public afterwards: "All videos
uploaded via the videos.insert endpoint from unverified API projects created
after 28 July 2020 will be restricted to private viewing mode"
(developers.google.com/youtube/v3/docs/videos/insert). Lifting it takes Google's
API audit, which users report at days to months. Buffer is an approved YouTube
app, the YardSwaps channel is already connected in our Buffer account (checked
2026-11-23 with the TikTok workflow's `check` run), and the `BUFFER_API_KEY`
secret the TikTok poster uses covers it. So no Google Cloud project, no OAuth
consent and no new secret. The script hands Buffer at most 2 Shorts in 24 hours
(our cadence). HeyCatch also publishes to the channel through the same Buffer
account (3 on Nov 22), so only our own `posted.json` entries count toward that cap.

## What a run does
1. Finds the YouTube channel in Buffer and updates `posted.json`: scheduled
   posts become `posted` (with the YouTube link) or `failed` (with Buffer's
   reason); a post Buffer hasn't sent after 3 hours becomes `unconfirmed`.
2. If a slot is open and unused today, takes the first row of `queue.json` that
   - is not already on YouTube (`posted.json`, or a video with the same title in
     the channel's public feed),
   - has no `"skip": true` and is past its `not_before` (ISO time, optional),
   - passes the copy checks: title of 100 characters or less, no `<` or `>`
     (YouTube rejects them), description ending with the open question, no
     category count, none of #fyp #reels #explore #smallbusiness, and no "list it
     free" on a storefront clip (`"audience": "dealer"`),
   - is allowed by the machine rotation (`rotation/README.md`): a machine shown
     on any channel is blocked for 14 days after its 36-hour run. When no row is
     allowed, the first row whose machine wasn't shown in the last 7 days may go
     (`"pick": "fallback"` in the log), the same floor the Reels poster uses.
3. Hands it to Buffer to publish 5 minutes later: public, category 28, not made
   for kids, subscribers notified. A vertical video under 3 minutes is a Short.
4. Logs it in `posted.json`, which `rotation/rotation.py` reads, so Reels,
   Stories and TikTok see YouTube's posts too.

A run outside the windows, or in a slot already used, does nothing. A late run
never posts next to HeyCatch. `hold_slots` in `queue.json` lists slots another
service fills: Dec 1 to Dec 7 at 4 pm belong to the 7 "List it free" Shorts the
YouTube thread scheduled on Metricool, so the poster leaves those empty and
those 7 rows are marked `skip`.

## Adding Shorts (weekly batch, YouTube thread)

Every Short ends on the YardSwaps end card, about 2 s (Alan, 2026-11-25; `brand/endcard/`). A row
posts only once it carries `"endcard"` (set by `python3 brand/endcard/endcard.py fix`, which adds the
card where it's missing; rows pointing at library clips share the clip's mark).
Append rows to `queue.json` `shorts` (order = priority):

```json
{"slug": "griddle-from-the-closed-diner",
 "file": "reels/library/yardswaps-griddle-from-the-closed-diner-9x16.mp4",
 "title": "POV: the diner closed. The griddle is still on the line.",
 "description": "...seller text...\n\nFree to list. No cut of the sale. Free boosts.\nList it free: yardswaps.com/y (link in our channel profile). Get the app: search YardSwaps on the App Store or Google Play.\n\n#griddle #restaurantequipment #commercialkitchen #usedequipment #yardswaps\n\nWhat is still on the line in the kitchen you closed?"}
```

- `slug` is the `reels/library.json` slug, so the rotation knows the machine. A
  clip that isn't in the library sets `"machine"` (or `"library_slug"`).
- `file` is any path in this repo, under 19 MB (Buffer fetches it from jsDelivr
  at the run's commit; bigger files fall back to raw.githubusercontent.com).
- Copy follows `MESSAGING.md` and the Shorts title rules in YOUTUBE-UPLOAD-QUEUE.md;
  a storefront clip adds `"audience": "dealer"` and never says list it free.
- Optional: `not_before`, `skip` + `skip_reason`, `category_id` (default "28"),
  `lang` (a note only; Buffer can't set the video language).
- The run summary warns when fewer than 4 rows are left.

## Manual runs
Actions > "YouTube Shorts" > Run workflow.
- `dry_run` = 1: the queue with the reason each row can or can't post now, and
  the next pick with its link, title and description. Posts nothing.
- `check` = 1: the Buffer channels, the YouTube channel's recent Buffer posts
  (sent and failed) and the latest videos on the channel. Posts nothing.
- `slug` = a queue row: posts it right away (outside the slots, logged
  `forced`), still within the 2-a-day cap and the copy checks.

## If something goes wrong
- "No YouTube channel in Buffer": in Buffer (yardswaps@gmail.com), Channels >
  Connect > YouTube, pick the YardSwaps channel. Free plan, never enter a card.
- A `failed` row in `posted.json` shows Buffer's reason. The row stays in the
  queue, so the next open slot retries it unless it is fixed or skipped.

# Long YouTube videos (added 2026-11-25)

Alan, 2026-11-25: "Why don't we post long videos to YouTube any longer". The
last long video went out Nov 16 through Zapier, which ran out of tasks on
Nov 17. Buffer posts Shorts only (9:16 or 1:1, up to 3 minutes), and
Metricool's free December posts are taken. So long (16:9) videos get their own
uploader on the YouTube Data API: `.github/workflows/youtube-long.yml` runs
`post_long.py`, one video a day between 8:30 and 11:00 am Central, from
`long-queue.json`, logged in `long-posted.json`.

It is the YardSwaps, Inc. internal publishing client. It uploads only our own
finished videos to our own channel (YardSwaps, UCC_TtVN5pOfs4z9OruWUlhw) on the
channel owner's OAuth grant (`youtube.upload` + `youtube.readonly`), and reads
no one else's data. Per video: `channels.list` + `playlistItems.list` (so a
title already on the channel is never uploaded twice), `videos.insert`,
`thumbnails.set` (the brand card) and `captions.insert` (the narration's .srt),
about 550 quota units, well inside the default 10,000 a day.

## Why it waits for LIVE
Google keeps every upload from an unaudited API project private ("All videos
uploaded via the videos.insert endpoint from unverified API projects created
after 28 July 2020 will be restricted to private viewing mode",
developers.google.com/youtube/v3/docs/videos/insert). Alan approved the free
API audit on 2026-11-25. Until it passes:
- scheduled runs only print the next pick;
- a manual run with `mode` = `test` uploads the next pick as private and logs
  it as a test, so the flow can be shown working.
After the audit, set the repo variable `YT_LONG_LIVE` to `1` (Settings >
Secrets and variables > Actions > Variables) and scheduled runs post publicly.

Secrets (added by the channel owner, never pasted anywhere else):
`YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`. Without them a run only
checks the queue offline.

## Adding long videos
Append rows to `long-queue.json` (order = priority):

```json
{"slug": "weekly-7",
 "file": "week-2026-11-27/yardswaps-weekly-7-16x9-voice.mp4",
 "title": "...", "description": "...ends on the open question?\n\n#sellequipment #yardswaps",
 "tags": ["used equipment", "YardSwaps"], "category_id": "28", "language": "en",
 "thumbnail": "thumbnails/yardswaps-brand-card-youtube-16x9.jpg",
 "captions": "week-2026-11-27/yardswaps-weekly-7-16x9-voice.en.srt",
 "endcard": "seller-v1"}
```

- Spanish rows: `"language": "es"` and the Spanish brand card
  `thumbnails/yardswaps-brand-card-es-youtube-16x9.jpg`.
- A row posts only with `"endcard"` set, once the video ends on the blue
  YardSwaps card (`python3 brand/endcard/endcard.py check FILE` / `add`).
- Copy checks: title of 100 characters or less, no `<` or `>`, description
  under 5,000 characters ending on the open question, no category count.
- Optional: `skip`, `not_before` (ISO time). A row that failed twice stops
  until fixed. `kit_slot` is a note only (the Nov 25 phone kit's time).
- The 4 English rows were also in Alan's phone kit on Nov 25; if they're
  already on the channel, the same-title check skips them.

Manual runs: Actions > "YouTube long videos" > Run workflow, `mode` dry, test
or post, optional `slug`.
