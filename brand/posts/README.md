# Post kit: one look for every post

Alan, 2026-11-26: "we need to improve quality of post and imagery and branding ... whatever we are sending to
the socials looks like ai slop." Later that day, on the first redesign: "The white and blue is much cleaner than
the blue in blue." Three outside critics rated the old posts and a second hard critic checked the new frames.

`kit.py` is the one place the look lives (`LOOK = "k2"`). Pillow only, so every workflow can import it.
The review page with every frame, before and after: https://claude.ai/artifact/69DpQECUAyXdk91BViJCaw

## The look (k2: white and blue)

- **White ground.** Words never sit on a photo and never on a dark panel.
- **A real photo from a live listing, on top, with nothing over it.** Never an AI, Canva or stock picture, never
  a blurred fill. The whole item stays in frame: a photo is cropped only when that trims 6% or less off a side;
  otherwise the whole photo sits on the light panel (#EEF2F8).
- **One blue tag** (#2563EB, white Space Grotesk Bold, corner radius 10) holding the one key fact: the price,
  the hours, "30 DAYS FREE". One tag per frame. Never the blue tag on slate or navy.
- **A slate title** (#1A3353, uppercase Space Grotesk Bold) on one line; a long one steps down in size, then
  takes two balanced lines. Never an ellipsis: `just_listed.short_title` cuts a seller's title at the first
  clause break, so "…Leaf Vacuum, 400 hrs, Like New" prints as the item and the rest prints as facts.
- **Facts in grey** (Inter, #4A5568): hours or miles, town and state spelled out, then condition and year.
- **The wordmark once per frame**, "Yard" slate and "Swaps" blue as in the app, with one small line on the
  right (the link, or the listing shown).
- No pills, shadows, gradients, stripes, check marks, icons, emoji or "POV:" hooks. Hard cuts, no fades.
  Only real data from the listing.
- Videos still end on the blue end card (`brand/endcard/`).

## The numbers (1080 wide)

| Thing | Value |
|---|---|
| Margin | 64 |
| Photo | y 0 to 720 (a 3:2 photo shows whole) |
| Tag | top 748, 162 tall, 118 px type |
| Title | baseline 1011, 86 px, down to 64 px; two lines start 19 px higher |
| Facts | 50 px, then a quieter second line at 40 px (the tall frame drops it under a two-line title) |
| Wordmark | 46 px; baseline 1205 on 9:16, 1283 on 4:5 |
| 9:16 | words only between y 269 and 1248; from 1240 down a second photo of the same listing, or the light panel |
| Story | everything 200 px lower (`STORY_OFF`), so Instagram's header sits on a light strip, not on the photo |

## What uses it

| Post | Made by | Function |
|---|---|---|
| Listing Reel (every shot before the end card) | `listings/listing_reels.py` | `reel_shots` |
| Daily "Just listed" card | `listings/just_listed.py` `render_card` | `listing_post` |
| "Buyers are looking for" card | `listings/just_listed.py` `render_wanted_card` | `text_post` |
| Tip posts (feed 4:5 and 9:16) | `brand/posts/make_tips.py` from `tips.json` | `tip_post` |
| Daily Story | `stories/render_story.js` | `story`, drawn again in HTML because the Story job checks out only `stories/` |

A listing Reel shows one shot per photo, joined with hard cuts, and has two layouts in the one look
(`reel_layout` picks):

- **Stack**, when the first photo is wide and there are two or more wide photos: the top photo, the detail under
  it and the facts line all change with the shot. One wide photo alone keeps a white foot, never a grey panel.
- **Upright**, when the first photo is upright or square (about half of all listings, phone photos): the
  wordmark as a masthead at the top of the safe area (baseline 315), then the same tag (top 345), title and facts,
  and one photo a shot from 40 px under the last line of text to the foot of the frame, flush with the text's
  left edge. An upright 3:4 photo fills the 952 px column (at most a 6% trim); anything else is shown whole on
  the white. Never a narrow photo between pale side bars (the first k2 pass did that and failed its review).

The link is on the end card, not on a Reel frame. Titles come in fixed sizes, never one in between: 86 px on
one line, else 64 px on one or two lines, and 56 px on two lines only when words would otherwise be dropped.
Capitals are set with no negative tracking. "Used · Good" reads "Good condition", and a bare "Used" is left out
when there is anything else to say.

Photos that show the same view are shown once (`distinct`). The blue end card holds 2.5 s on listing Reels so
it lands on a short clip that loops.

`LOOK` in `kit.py` names the version. When it changes, the listings job re-makes older listing Reels from the
photos their review already approved (4 a run), keeps the old files, and points the library entry at the new
one (`-k2.mp4`).

Not on the kit yet: Studio's clips (`studio/make_pov.py`), Shorts, YouTube thumbnails and the ads. Their k2
frames are on the review page; they are rebuilt in the ads home thread.

## Tip posts

A tip's photo has to PROVE the tip (the hour meter, the data plate, the wear), the tag holds the fact in the
photo ("12,402 HRS"), the headline is one plain instruction and the body one line that says the same thing.
`tips.json` holds each tip: `tag`, `headline`, `body`, `photo` (`photos/<slug>.jpg`), the live listing it came
from and its `credit`. `python3 brand/posts/make_tips.py` renders `out/<slug>-4x5.jpg` and `-9x16.jpg`. The
credit line prints only when the listings API says the listing is still live that day, so run it again on the
day a tip posts. A tip marked `"held": true` is not rendered: the four from the first pass are held because
their photos do not show the tip.

No tip posts until Alan says go. `post_image.py` refuses any entry in `reels/images.json` that is not
`picture: "real"`.

Rules for a new tip: plain advice a mechanic would agree with, nothing we can't back up, no promise of views or
sales, a real photo with no face or plate (blur serials and phone numbers), and a caption that ends with an open
question. Copy follows MESSAGING.md.
