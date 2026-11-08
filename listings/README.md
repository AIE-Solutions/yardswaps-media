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

## "Buyers are looking" cards (wanted.json)

Between listing cards, prep queues one seller-recruitment card from `wanted.json`: "Buyers are looking for generators", and so on, built from real 30-day search data (seller-growth/WANTED-POSTS.md).
- At most one every 3 days, the same one at most once in 30 days, and they don't take a listing slot.
- A post is skipped once its claim stops being true on the live site (for example a generator gets listed), and all of them stop once `as_of` is more than 30 days old. Refresh the numbers and `as_of` from the newest `[GrowthDigest]`.
- The Facebook caption links the category's seller page, `/sell-equipment/<slug>`, only once that page answers 200; until then it links `/sell-equipment`. Tag: `utm_campaign=post_wanted-<slug>`.
- Spanish versions wait for Alan or Emmanuel to proofread.

Review a wanted card like a listing card, plus: reject it if the caption promises views or sales, gives an exact search count below 10, or if the card's text is cut off.

## Run it by hand

Use Actions, then "Just listed posts", then "Run workflow":
- `mode=prep` queues cards now.
- `mode=post` with a `listing_id` posts that approved card now (logged `forced`).
