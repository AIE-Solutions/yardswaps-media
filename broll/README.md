# Runway b-roll

Short Runway clips made from our own photos, for the 2-second opener of a Short and for cutaways inside the long YouTube videos. Why and what it costs: `RUNWAY.md` in the campaign folder.

- `in/`: the photo a clip starts from (a real listing photo or Canva stock, equipment only, no people, plates blurred). Keep each under 16 MB and between 1:2 and 2:1.
- `<slug>-<ratio>.mp4`: the clip as Runway returned it (first frame = the photo).
- `<slug>-<ratio>-rev.mp4`: the same clip played backwards, so it ends on the photo. The opener uses this one and the match cut still lands on the listing photo.
- `<slug>-<ratio>.png`: a photo edit (people removed, lettering removed) from `gen4_image`.
- `log.json`: every generation with its prompt, seed and credits spent. The Monday report reads it.

## Clean covers from a real photo (seedream5.5_layers, Runway Nov 12 2026)
Runway's Seedream 5.5 Layers splits one photo into a base image and transparent layers. We use it only for the item's outline: `cutout_card.py` checks the item layer against the real photo inside that outline (if the model redrew colours or shape, the run refuses and nothing is made), then takes the **real photo's pixels** through the outline and puts the whole item on the slate brand background with the title, price and wordmark.

Run: Actions > "Runway clip" > `model: seedream5.5_layers`, `photo` (a real listing photo, repo path or https), `slug`, `title` (the listing title as written), `price` (or blank), `max_images` 4. Cost at 1k: 2 credits per returned image + 1 for the source, so about 9 credits. Outputs in `cutouts/<slug>/`: `item.png` (transparent, for video edits), `cover-9x16.jpg` (Reels, Shorts, TikTok cover, Story), `card-4x5.jpg` (feed card, storefront promo), `check.jpg` + `check.json` (photo | outline | cover, and the numbers). Raw layers stay in `layers/<slug>/`. Same review rules as the Just Listed cards before anything posts.

Via the Runway connector in a Claude thread (uses the web-app credits, not the API balance): upload the photo, run `seedream-5.5-layers` with `maxImages` 4 at 1K (9 credits), save the outputs as `layers/<slug>/00.png` (base), `01.png` (item) plus a `layers.json`, then run `cutout_card.py --layers`. Those results come without bounding boxes on a padded canvas, so `cutout_card.py` finds where the layer sits by matching it against the photo; the same pixel check still refuses a redrawn item. The cloud environment must allow `dnznrvs05pmza.cloudfront.net` (Runway's file host) to download them. First 3 samples (Nov 24): Sky Trak 6042, Atmax MowerMax, Goodman split system, mean difference 5 to 7.5 against the real photo (limit 14).

## Seedance 2.5 Flash clips (Runway Nov 16 2026)
`model: seedance2_5_flash` is image to video at 720p (`720:1280` for Shorts) or 480p, 4 to 30 s, 20 credits a second at 720p (52 minimum), so a 5 s opener is 100 credits against Gen-4 Turbo's 25. Use it only when a clip must run longer than 10 s in one take. The clip may come back with generated audio: never post that audio, our renders lay licensed music or the narration over it.

## Spend guard and tags
Every run prints the estimate first and stops before spending if it is above `max_credits` (default 60) or above the balance; we never buy credits without Alan's OK. Every generation is sent with Runway's request tags (`yardswaps,organic,model:<model>,slug:<slug>`, Nov 18 2026), so the Usage page in the Runway developer portal splits spend by use. `log.json` keeps the estimate and the tags too.

## Making one
Actions > "Runway clip" > Run workflow. `photo` = `broll/in/<file>.jpg` (commit it first) or an https URL; `prompt`; `model` `gen4_turbo` (25 credits per 5 s), `gen4.5` (60), `seedance2_5_flash` (100 per 5 s at 720p), `gen4_image` (5 to 8 per edit) or `seedream5.5_layers` (about 9, see above); `ratio` `720:1280` for Shorts; `slug`. `mode: balance` only prints the credit balance.

One run is one generation. Nothing is scheduled. The run stops before spending anything if `RUNWAYML_API_SECRET` is missing.

## Setup (Alan, once)
1. Sign up at https://dev.runway.com with yardswaps@gmail.com, create a project.
2. Billing tab: add $10 of credits (1,000 credits, the minimum).
3. API Keys tab: create a key named `yardswaps-media`, copy it (shown once).
4. https://github.com/AIE-Solutions/yardswaps-media/settings/secrets/actions/new : name `RUNWAYML_API_SECRET`, paste, Add secret.
5. Reply "runway key added" in the project. The thread runs `mode: balance`, then the first opener clip.

## Rules for a clip before it is used
No person, no text, no logo, no new object, the machine does not drive. The reversed clip's last frame is the photo. The finished Short still passes cropaudit and objectaudit.
