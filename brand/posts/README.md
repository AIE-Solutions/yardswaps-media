# Post kit: one look for every post

Alan, 2026-11-26: "we need to improve quality of post and imagery and branding ... whatever we are sending to
the socials looks like ai slop." Until then each pipeline drew its own frame: a small photo on a blurred copy
of itself, an AI sunset behind the daily Story, small type, and no logo before the end card.

`kit.py` is the one place the look lives. Pillow only, so every workflow can import it.

## The look

- A real photo from a live listing, big and sharp. Never an AI, Canva or stock picture, never a blurred fill.
- The YardSwaps wordmark on a white tab, top left, on every frame.
- A bold uppercase Space Grotesk headline with one line on the blue bar (#2563EB).
- The words sit on a brand slate panel (#1A3353), never on a busy picture. The tip box and the feed bar use the
  deeper slate (#0E2240). These are the app's own tokens (`--accent`, `--slate-brand`, `--slate-deep`); no other
  colours.
- Feed posts end in the brand bar: wordmark, "Buy and sell used equipment", blue stripes.
- Stories and Reels keep the top 150 px and the bottom 340 px clear (the apps put their buttons there).
- No check marks, no decorative icons, no emoji.

## What uses it

| Post | Made by | Function |
|---|---|---|
| Listing Reel (every frame before the end card) | `listings/listing_reels.py` | `reel_frame` |
| Daily "Just listed" card | `listings/just_listed.py` `render_card` | `listing_post` |
| "Buyers are looking for" card | `listings/just_listed.py` `render_wanted_card` | `text_post` |
| Tip posts (feed 4:5 and Story 9:16) | `brand/posts/make_tips.py` from `tips.json` | `tip_post` |
| Studio POV clips (new ones) | `studio/make_pov.py` `still_frame` | `card` on the slate panel, wordmark tab on the overlay |
| Daily Story | `stories/render_story.js` | the same look drawn in HTML, because the Story job checks out only `stories/` |

`LOOK` in `kit.py` names the version. Bump it when the look changes: the listings job then re-makes older
listing Reels from the photos their review already approved (4 a run), keeps the old files, and points the
library entry at the new one.

## Tip posts

`tips.json` holds each tip: kicker, headline (a line starting with `*` gets the blue bar), body, tip, the photo
(`photos/<slug>.jpg`) and the live listing it came from. `python3 brand/posts/make_tips.py` renders
`out/<slug>-4x5.jpg` and `-9x16.jpg`. The "On YardSwaps now" chip prints the listing and its price only when the
listings API says it is still live that day, so run it again on the day a tip posts.

Tips are queued in `reels/images.json` (`picture: "real"`) and go out with the Reels workflow's `image_slug`
input. `post_image.py` refuses any entry that is not `picture: "real"`.

Rules for a new tip: plain advice a mechanic would agree with, nothing we can't back up, no promise of views or
sales, a real photo with no face or plate (blur serials and phone numbers), and a caption that ends with an open
question. Copy follows MESSAGING.md.
