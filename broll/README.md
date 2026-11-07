# Runway b-roll

Short Runway clips made from our own photos, for the 2-second opener of a Short and for cutaways inside the long YouTube videos. Why and what it costs: `RUNWAY.md` in the campaign folder.

- `in/`: the photo a clip starts from (a real listing photo or Canva stock, equipment only, no people, plates blurred). Keep each under 16 MB and between 1:2 and 2:1.
- `<slug>-<ratio>.mp4`: the clip as Runway returned it (first frame = the photo).
- `<slug>-<ratio>-rev.mp4`: the same clip played backwards, so it ends on the photo. The opener uses this one and the match cut still lands on the listing photo.
- `<slug>-<ratio>.png`: a photo edit (people removed, lettering removed) from `gen4_image`.
- `log.json`: every generation with its prompt, seed and credits spent. The Monday report reads it.

## Making one
Actions > "Runway clip" > Run workflow. `photo` = `broll/in/<file>.jpg` (commit it first) or an https URL; `prompt`; `model` `gen4_turbo` (25 credits per 5 s), `gen4.5` (60) or `gen4_image` (5 to 8 per edit); `ratio` `720:1280` for Shorts; `slug`. `mode: balance` only prints the credit balance.

One run is one generation. Nothing is scheduled. The run stops before spending anything if `RUNWAYML_API_SECRET` is missing.

## Setup (Alan, once)
1. Sign up at https://dev.runway.com with yardswaps@gmail.com, create a project.
2. Billing tab: add $10 of credits (1,000 credits, the minimum).
3. API Keys tab: create a key named `yardswaps-media`, copy it (shown once).
4. https://github.com/AIE-Solutions/yardswaps-media/settings/secrets/actions/new : name `RUNWAYML_API_SECRET`, paste, Add secret.
5. Reply "runway key added" in the project. The thread runs `mode: balance`, then the first opener clip.

## Rules for a clip before it is used
No person, no text, no logo, no new object, the machine does not drive. The reversed clip's last frame is the photo. The finished Short still passes cropaudit and objectaudit.
