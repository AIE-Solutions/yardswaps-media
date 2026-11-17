# After-hours photo posts

Single-photo Instagram/Facebook feed posts in the look Alan pointed at on
2026-11-17 (a ready-mix company's post: one real machine, dark and moody, no
text on the image, a one-line caption). Organic posts only.

- `build.py` grades real live-site listing photos from
  `broll/in/brand-kit/site-listings/` (dark midtones, top of frame falls to
  night, slate shadows, warm highlights, vignette, fine grain) and fits the
  whole item on the canvas: 1080x1350 for upright photos, 1080x1080 for wide
  ones, with the gap fading to night from the photo's own edge colours. No
  stretched copies, no added lights, no text, no logo.
- Blur boxes in `POSTS` cover plates, door numbers and dealer watermarks.
- `posts.json` holds the IG and FB captions. Status `awaiting_alan` until he
  OKs them; after that each one can go into `listings/queue.json` as an
  `approved` card so the daily feed poster picks it up.

Run: `python3 ads/after-hours/build.py ads/after-hours/out`
