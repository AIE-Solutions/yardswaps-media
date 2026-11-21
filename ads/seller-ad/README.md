# "Equipment sitting idle?" seller ad (Nov 21 2026, 15.6 s)

Alan, Nov 21: "We got some new items we can look at including and building another ad from", then "put it towards just sellers ... or anyone wanting to sell equipment". So this cut is seller-first: list your equipment, AI writes the listing from your photos, listing is free. No storefront or founding pitch. Same look as the live Meta ad r1-yard-biglogo (big wordmark pill top-left, big white captions with a slate outline that pop in on beat cuts, the real app on the phone stage, the light end card).

**Not posted, not in any campaign.** Preview for Alan first; no spend.

| Time | Shot | Line on screen |
|---|---|---|
| 0.0-1.5 | Real listing photo: 2001 Caterpillar 950G wheel loader, parked | Equipment sitting idle? |
| 1.5-2.4 | Real listing photo: 2008 Tadano GR-800XL rough-terrain crane, parked on pads | Cranes. |
| 2.4-3.4 | Real listing photo: 2006 Dynapac CA602PD padfoot roller | Rollers. |
| 3.4-4.4 | Real listing photo: pallet racking lot (beams and uprights) | Racking. |
| 4.4-5.3 | Real listing photo: Instapak SpeedyPacker foam packer | Packaging machines. |
| 5.3-7.0 | Real app recording: Choose from Library, the same 950G photo lands, AI starts reading it | Snap a photo. |
| 7.0-9.3 | AI fills title ("2001 Caterpillar 950G Wheel Loader"), category, condition; form scrolls | AI writes the listing. |
| 9.3-11.0 | Tap "Use price", $52,000 goes in | Set your price. |
| 11.0-13.0 | "Your listing is live!" | Listed free. |
| 13.0-15.6 | End card: wordmark, "List it free.", "AI writes the listing from your photos.", "No selling fee.", store badges, yardswaps.com | What's sitting in your yard right now? |

Outputs (`out/build-*/`):
- `yardswaps-sellers-new-listings-9x16.mp4`: Meta Reels/Stories (text inside Meta's 9:16 safe zone).
- `yardswaps-sellers-new-listings-4x5.mp4`: Meta feed.
- `yardswaps-sellers-new-listings-shorts-9x16.mp4`: YouTube Shorts / TikTok, end card inside the safe box x 48-888, y 288-1248.

Sources: the five photos are the listings' own first photos from the public listings API (newest, listed Nov 20), unedited:
1 `cmwosmtfk002dob3a2ir3um3c` (950G), 2 `cmwosmtfl002yob3aoii07nyf` (Tadano), 3 `cmwosmtfl002qob3acb852grs` (Dynapac, photo 2 of the listing: photo 3 carries the seller's sticker), 4 `cmwp8zzf0000jqt3a2d3no15x` (racking, photo 2), 5 `cmwpdczz50009tc3ao0enr7e2` (Instapak). The app recording is the mobile app's Sell tab (Expo web build, mock API as in the Motion recordings: `assets/motion/source/recording/recsell.js` with a scan stub built from the 950G listing's own title, year, hours and price range), so the item photographed in the app is the item in the opener.

Rules checked (sheets `words-vs-screen-9x16.jpg`, `words-vs-screen-4x5.jpg`):
- Whole item in every opener: each photo is fitted inside the photo box, never cropped; the push is 1.035x and grows into the box margins.
- No faces, no plates, no dealer stickers or banners in frame (the Ford box truck was skipped for its dealer banner, the roller's third photo for its sticker).
- The item in the opener is the item the app lists. Every line matches the screen at that moment; "Listed free." starts after the boost prices leave the screen.
- No category count, no promise of views or sales, no storefront or price-plan claims. "List it free" and "No selling fee" match the site FAQ ("Listings are free and there is no selling fee"). AI listing is the free tier's AI scan (5 free, then Pro or packs); the line says what it does, not how many.
- Music: ElevenLabs Music bed `music/v2/yardswaps-music-clean-120bpm.mp3` (our grant), whoosh and tap SFX from `music/v4/sfx` (copied to `source/music`). No voice. -14 LUFS.
- No AI-generated imagery: every shot is a real photo or the real app, so no AI label is needed.

Rebuild: `python3 layout.py && python3 apprec.py <recording frame dir> && for r in 9x16-paid 4x5 9x16-shorts; do RATIO=$r ./build.sh; done`, then `python3 wordsheet.py <mp4> <sheet.jpg>`. `source/base/` holds the phone stage, mask and end card base from the storefront ad (ads/storefront-ad on PR #73), so this folder builds on main without that branch. Earlier ads are untouched.

Found on the way: the Sell tab crashed with "Rendered more hooks than during the previous render" when a session finished loading on it (the scan-packs `useState` sat below the early returns). Fixed in Marketplace PR #434.
