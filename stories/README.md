# LIST IT FREE daily Story

Alan approved (2026-11-08) one Instagram Story a day, ~9:30 am Central, with a
fixed template. Only the machine changes by weekday:
Mon generator, Tue conveyor oven, Wed dump trailer, Thu walk-in cooler,
Fri ice machine, Sat zero-turn mower, Sun scissor lift.

Template (character-for-character, see `render_story.js`):
- Headline: `LIST IT FREE`
- Body: `That {machine} in the yard is worth money. Snap a photo — AI drafts the listing.`
- Link sticker (tappable, lower third): `List yours free on YardSwaps` -> https://www.yardswaps.com/sell-equipment
- Footer: `No commission · Local pickup · yardswaps.com`

## What's built
- `make_bg.py`: today's machine (America/Chicago weekday) and a 9:16 AI
  backdrop (Runway gen4_image text-to-image, or a given BG_URL). Illustrative
  only, never a real listing. No people, text or logos.
- `render_story.js`: renders `*-story.png` (what gets published, no drawn
  sticker) and `*-preview.png` (dashed mock showing where the sticker goes).
- `.github/workflows/story.yml`: runs both and commits to `stories/out/`.
  It never publishes.

## Why it does not publish yet
The Instagram Graph API publishes Stories (`media_type=STORIES`) but cannot
add link stickers or any sticker; Buffer and Metricool say the same for
auto-published Stories. The template requires a tappable sticker, so per
Alan's rule 6 nothing is posted until he picks a route.
