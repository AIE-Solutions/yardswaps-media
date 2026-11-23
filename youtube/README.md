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
consent and no new secret. Buffer's free plan allows 2 YouTube posts per channel
per 24 hours, which is exactly our cadence; the script never asks for a third.

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
