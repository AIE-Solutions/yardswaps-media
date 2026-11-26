# Machine rotation (added 2026-11-21)

Alan, 2026-11-21: "We keep reusing the same machines for our social media posts."
The audit behind this is `AUDIT-2026-11-21.md` in this folder.

## The rule
- A **machine** is the piece of equipment a post shows, not the clip. Two clips cut
  from the same opener photo are the same machine. Every `reels/library.json` entry
  carries a `machine` key (`forklift-yellow-warehouse`, `dozer`, `towable-generator`,
  ...). A clip made from a real listing uses `listing-<listing id>`. A Story backdrop
  uses `story-<machine slug>`.
- A machine's **run** starts the first time it posts on any channel. For the next
  36 hours (`RUN_HOURS`) the same clip may still cross-post to the other surfaces
  (Instagram, Facebook, both Stories, TikTok, YouTube). After that the machine is
  blocked on **every** channel until 14 days (`ROTATION_DAYS`) after the run started.
  If it was shown again after its run anyway (a hand post), it is blocked until 14
  days after that last showing.
- When nothing is free, a poster may use the machine shown longest ago, but never one
  shown in the last 7 days (`FLOOR_DAYS`). Past that it skips the slot. A skipped slot
  is better than a repeat.
- Category spread: among free clips, the categories of the last 2 posts on that
  channel go last.
- Real listings come first among new clips, newest listing first, one per seller per
  run, categories interleaved.

## Where the record lives
There is no central log to keep in sync. `rotation.py` merges, on every read, the
logs each poster already writes:

| Log | Written by |
|---|---|
| `reels/posted.json` | Reels, Stories, List it free post, promo post (`post_reels.py`) |
| `reels/tiktok-posted.json`, `reels/heycatch-tiktok.json` | TikTok poster |
| `youtube/posted.json` | YouTube Shorts poster (`youtube/post_shorts.py`, from 2026-11-23) |
| `reels/images-posted.json` | image posts |
| `listings/posted.json` + `listings/queue.json` | Just listed and Wanted cards |
| `stories/posted.json` | LIST IT FREE daily Story |
| `rotation/manual.json` | everything else, by hand (below) |

`rotation/used.json` is only a snapshot for people to read (`rotation.py log`).

## Posts made outside the posters: add a row to `manual.json`
YouTube long videos and Shorts posted outside `youtube/post_shorts.py`, Typefully / X, LinkedIn, Reddit, Motion test posts,
anything posted by hand, and any HeyCatch post that uses one of our clips or photos.
One row per post, committed to `main`:

```json
{"time": "2026-11-22T15:00:00Z", "channel": "youtube_short", "slug": "lift-still-bolted-down"}
{"time": "2026-11-22T14:00:00Z", "channel": "x", "machine": "towable-generator"}
{"time": "2026-11-22T20:15:00Z", "channel": "linkedin", "listing_id": "cmwm5nuh9005fql3ag390kwc7"}
```

`slug` (a library clip), `machine` or `listing_id`, whichever fits. A row with a future
time is a scheduled post and already counts.

## Command line
```
python3 rotation/rotation.py              # status: posts on record, machines blocked / free
python3 rotation/rotation.py check <slug or machine>   # may it post now? run start, free_from
python3 rotation/rotation.py free         # library clips free to post now, newest first
python3 rotation/rotation.py listings live.json        # live listings in posting order
python3 rotation/rotation.py log          # write rotation/used.json (30 days)
```

## Who follows it
- `reels/post_reels.py` (Reels, Stories, TikTok, List it free post, promo post):
  `pick()` keeps only clips whose machine is allowed. The 10-day per-platform rule
  still applies on top.
- `stories/make_bg.py`: picks the Story machine by rotation instead of by weekday.
- `youtube/post_shorts.py`: posts the first `youtube/queue.json` row whose machine is
  allowed, else the first not shown in the last 7 days, else skips the slot.
- `listings/listing_reels.py`: turns live listings into Reels in rotation order.
- Motion / weekly batch / YouTube tasks: check `rotation.py check` before cutting or
  posting, never reuse an opener photo under a new slug, and add a `machine` key to
  every new library entry.

## Adding a machine
A new clip with a new opener photo gets a new `machine` key. A recut of an old clip
keeps the old key. A new folder in `stories/bank/` adds a Story machine.
