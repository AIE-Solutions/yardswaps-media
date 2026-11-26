# Just listed posts

One live YardSwaps listing a day goes to Instagram (feed photo) and the Facebook Page (photo post) as a branded card. Alan approved this on 2026-11-05. It runs by itself; nobody has to click anything.

## How it works

1. **prep** (`.github/workflows/listings.yml`, 9:10 am Central). `just_listed.py` reads the public listings API, sorted newest first. Listings never featured go first, then the ones featured longest ago, with at most one card waiting per seller. It checks up to 4 photos per listing:
   - It skips any photo where OpenCV finds a face.
   - It blurs every word that tesseract reads with a digit in it, such as phone numbers, plates and street numbers.
   - It renders a 1080x1350 card into `cards/<listing id>.jpg`.
   - It queues the card in `queue.json` as `pending`.
   - It keeps up to 3 cards waiting.
2. **review** (a Claude scheduled task, about 11:30 am Central). The task looks at every `pending` card and sets `approved`, or `rejected` with a `reason`. See "Review rules" below.
3. **post** (2:15 pm Central, with backups until 9 pm). The workflow posts the oldest `approved` card:
   - It is posted once a day.
   - It goes up only if nothing else, such as HeyCatch, posted in the last 90 minutes.
   - It is logged in `posted.json`.
   - The Reels poster and the metrics snapshot both count these posts as ours.

A listing can be featured again after 45 days. A rejected listing comes back only after its seller edits it.

## What a post shows

The card and the captions show only:
- title
- price
- year, hours or miles
- city and state
- category hashtags

They never include the seller's name, phone number, description or storefront.

The two captions differ in the link:
- The Instagram caption points to yardswaps.com/i, the link in the bio.
- The Facebook caption links the listing with `utm_source=facebook&utm_medium=social&utm_campaign=just_listed`.

Both captions end with an open question.

## Review rules (for the Claude review task)

Reject the card if any of these is visible:
- a person or face, even partly
- a readable personal or business name, logo, storefront sign or dealer watermark
- a phone number, licence plate, street address or house number that the blur missed
- a photo that does not match the title
- an unsafe or offensive image

Also reject a listing that is plainly not equipment, or a duplicate of a card that is already waiting.

Approve everything else. A rejection needs a one-line `reason`.

### Listing Reels (listings/reel-queue.json)
Each pending row in `listings/reel-queue.json` is a 12-second Reel cut from a live
listing's photos (`listings/listing_reels.py`). Open its `preview` contact sheet
(`listings/reel-previews/<listing id>.jpg`, every photo used plus the end card) and
apply the same rules as the cards above, plus: the whole item is in frame, no plate or
number the blur missed, and the title and price boxes match the photos. Set `status` to
`approved` or `rejected` (with a one-line `reason`), plus `updated` (ISO time) and
`reviewed_by`. Commit `reel-queue.json`. The next prep run clears the hold on approved
clips and removes rejected ones. Clips built from an already approved card photo skip
this queue.
When a rejection names only some photos ("photo 2 is cut off"), the next run rebuilds the
listing's clip without those photos and puts it back in this queue as a new pending row
(Nov 26: real listing photos are now the only pictures the Reels use, so a clip is worth
saving). A reason about every photo, a watermark, the title or a non-equipment item still
drops the listing.

## "Buyers are looking" cards (wanted.json)

Between listing cards, prep queues one seller-recruitment card from `wanted.json`: "Buyers are looking for generators", and so on, built from real 30-day search data (seller-growth/WANTED-POSTS.md).
- At most one every 3 days, the same one at most once in 30 days, and they don't take a listing slot.
- Copy states buyer interest only (Alan, 2026-11-10): never that searches came up empty, buyers found nothing, or that none, zero or one are listed, because to a seller that reads as "the marketplace is empty". prep skips any post whose copy says so. All of them stop once `as_of` is more than 30 days old. Refresh the numbers and `as_of` from the newest `[GrowthDigest]`.
- The Facebook caption links the category's seller page, `/sell-equipment/<slug>`, only once that page answers 200; until then it links `/sell-equipment` (those pages went live with Marketplace PR #261 on 2026-11-09). A post with `link_path` links that page instead: the Craigslist card opens `/sell?import=craigslist`, the Sell form with the paste box open. Tag: `utm_campaign=post_wanted-<slug>` (or `-<key>`).
- Spanish versions wait for Alan or Emmanuel to proofread.

Review a wanted card like a listing card, plus: reject it if the caption promises views or sales, gives an exact search count below 10, or if the card's text is cut off.

## Run it by hand

Use Actions, then "Just listed posts", then "Run workflow":
- `mode=prep` queues cards now.
- `mode=post` with a `listing_id` posts that approved card now (logged `forced`).

## New listings into the Shorts mix (Nov 16)

Alan, Nov 16: new users list new items most days, so they go into the promotion mix. The prep step now also saves the
cleaned, uncropped photo of every queued listing to `listings/photos/<id>.jpg` (same face check and digit blur as the
card) and records `photo_file`, `price`, `condition`, `year`, `place` and `created` on the queue entry. The Motion
runs (Monday, Wednesday, Friday) pick up to two listings that passed the review gate (`approved` or `posted`), not yet
in `listings/motion-used.json`, one per seller, and cut a 10 s Short on the real photo (pickreal.py in the campaign
folder). Those library entries carry `listing_id` and `real: true`; `post_reels.py` holds such a Short on any day the
same listing's Just-listed card went out, so one new item is never posted twice the same day.

## Paying sellers go first (Nov 16)

Alan, Nov 16: when someone pays for Pro or a Dealer storefront, their listings go to the top of the posting queue,
with nobody doing it by hand. Storefronts in their free trial days are featured too, after every paying seller
(his pick on the decision card).

- The trigger is the subscription itself. The Stripe webhook already saves it in the app, and
  `https://www.yardswaps.com/api/social-feature` lists every paying seller (rank 1) and trial storefront
  (rank 2) with their newest live listings, plus the sellers who switched the feature off (Marketplace PR #363).
- Every prep run reads that list first. Each seller on it who hasn't had a paid card in the last 3 days gets one
  card marked `"feature": "paid"` at the front of `queue.json`. Payers go first, then whoever was featured longest
  ago. This happens even when 3 regular cards are already waiting. A regular card of theirs that is already waiting
  is moved up instead. The same listing comes back after 14 days at the earliest (45 for free listings).
- The review gate is unchanged: a paid card is approved or rejected under the same rules as every card.
- The post step posts an approved paid card before any other. It is still one post a day, at 2:15 pm Central.
- `paid-features.json` logs every paid card twice: `queued`, then `posted` with the Instagram and Facebook links.
  That file is how to see that it fired.
- Opt-out: a seller who turns off "Feature my listings in YardSwaps social posts" (web Privacy & data, app
  Settings) has every waiting card withdrawn and every queue entry marked `opted_out`. pickreal.py and the Reels
  poster then skip them.
- If the list can't be read, prep logs a warning and runs as before.
- Copy rules are unchanged: item and category only, never the seller's name, business or phone.

## Listing Reels (Nov 21)
After prep, `listing_reels.py` turns up to `REELS_PER_RUN` (6) live listings a day into
Reels for the Reels, Stories and TikTok rotation: newest listings first, one per seller,
categories mixed, skipping any listing already shown in the last 14 days
(`rotation/README.md`). Each clip shows up to 3 cleaned photos fitted whole (faces
skipped, numbers blurred), "JUST LISTED ON YARDSWAPS", the title and price, an open
question and the brand end card; no seller name, description or town. The caption ends
on the free listing line. A clip waits for the review above unless its card photo was
already approved. When a listing sells or its seller turns off social features, the
clip is put on hold.
