# Storefront ad on YouTube Shorts (draft, nothing live)

Source: `out-viral4-cards-biglogo/yardswaps-storefront-viral4-cards-biglogo-paid-9x16.mp4`
(commit be2f074), the cut running on Meta as `r1-yard-biglogo`.

## What changed for Shorts

`yardswaps-storefront-biglogo-shorts-9x16.mp4` (1080x1920, 30 fps, 13.0 s, same audio).

Shorts covers the right side with the like, comment and share buttons and the
bottom third with the channel name, headline and button. The Meta end card ran
to the right edge, so "months.", the end of the wordmark and "now?" sat under
the buttons. From 10.0 s the end card is scaled to 82% and moved left so all of
it sits inside x 48 to 888, y 288 to 1248 (AdKit's Shorts safe-zone figures,
which match the 15% top / 35% bottom reserve). The fade from black is rebuilt so
the padding fades with it. Seconds 0 to 10 are untouched.

`safe-zones.jpg`: red marks what Shorts covers. Known and accepted: the full
stops of "Your whole yard." and "Your hours." touch the button column, and the
listing cards at the bottom of the phone beat sit under the ad text.

Rebuild:

```
ffmpeg -i <biglogo 9x16> -filter_complex "[0:v]split[a][b];[b]trim=start=10.2,setpts=PTS-STARTPTS,tpad=start_duration=0.2:start_mode=clone,scale=886:1574:flags=lanczos,pad=1080:1920:25:91:color=0xF5F4F7,fade=t=in:st=0:d=0.17:color=black,setpts=PTS+10.0/TB[e];[a][e]overlay=0:0:enable='gte(t,9.999)':eof_action=pass,format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -preset slow -crf 20 -profile:v high -r 30 -c:a copy -movflags +faststart out.mp4
```

## Proposed campaign (build PAUSED, no spend until Alan approves a budget)

- Account: needs a YardSwaps Google Ads account. On 2026-11-21 the only account
  under the owner's Google login was 853-110-6937, "setup in progress", with a
  wizard prefilled for another business. Not touched.
- Video: Google requires Shorts ad videos on YouTube; upload this file to the
  YardSwaps channel as Unlisted.
- Type: Demand Gen, goal website traffic, bid Maximize clicks.
- Channels: YouTube Shorts only (Demand Gen channel controls).
- Location US, English, ages 25 to 65+.
- Audience: custom segment, people who searched for: used skid steer for sale,
  used forklift for sale, used excavator for sale, used box truck for sale, sell
  used equipment, equipment dealer website; plus people who browse sites like
  machinerytrader.com, equipmenttrader.com, machinio.com, ironplanet.com.
  Channel placements (equipment YouTube channels) are not offered in Demand Gen;
  they need a separate Video campaign later if search intent works.
- Budget proposal: $5 a day for 7 days, about $35 total, with an end date.
- Headline (40 max): `Your whole yard on one page`
- Description (90 max): `30 days free, then $29/mo for 3 months, first 100 storefronts. Then $49/mo.`
- Business name `YardSwaps`, CTA `Learn more`.
- Final URL: `https://www.yardswaps.com/dealers?utm_source=youtube&utm_medium=paid&utm_campaign=storefront_shorts&utm_content=biglogo_shorts`

No dates in any copy. Never "listing is free" for dealers.
