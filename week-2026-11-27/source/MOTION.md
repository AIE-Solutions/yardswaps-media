# YardSwaps motion design videos

> **REAL ITEMS ONLY (Alan, 2026-11-26: "For the reels the items in the pictures need to improve and be real the rig one looks terrible"). This wins over every older line in this file and in the Motion routine prompts.** Every opener, and the photo uploaded in the recording, comes from a live YardSwaps listing: run `pickreal.py 7` and make each Short from what it returns. No Canva, Pexels, Unsplash, Wikimedia or other stock photo and no AI image anywhere in a Short; skip the photo pass. Entries get `"real": true`, `"picture": "real"`, `"listing_id"`. Since media PR "Reels: real items only" every poster skips clips not marked real, so a stock cut never posts. Make fewer than 7 rather than fill with stock; zero is a valid run. A distant, small, cut-off or unclear item fails the whole-item gate (the drilling-rig stock derrick is the example; never copy its shape).


Rebuilt Oct 10, 2026 after Alan asked for a rethink. The new direction is "app as the star." There are three 15-second videos, each with one idea. The real, current YardSwaps app runs on a big phone, and the camera zooms into the screen as things happen. The listings use the real stock photos from the Canva folder (never the AI images). Files are in `assets/motion/`. These are drafts: Alan approves each one before it goes out.

Brand theme: light gray background, Space Grotesk headlines in slate and blue, and a blue gradient end card with the YardSwaps wordmark, App Store and Google Play badges, and yardswaps.com. Every word is on screen, so the videos work with the sound off. Since Oct 10 the 9x16, 4x5 and 1x1 files carry original background music made for these videos (upbeat electronic, about 120 BPM, with a hit when the end card lands). Nobody else owns it, so there are no copyright claims. Silent copies are in `silent/` if you would rather pick a song in Instagram or TikTok. The music source is in `source/music/`.

| Video | Length | What happens | Files |
|---|---|---|---|
| **1. Add a photo. AI lists it.** | 15 s | "Selling equipment? Just add a photo." A compressor photo goes into the real sell screen. "AI reads your photos" while the app reads it, then the title, category, condition, description and a $350 to $650 suggested price fill in by themselves, with check pills for each. Ends on "You check it. Then post." over the AI disclaimer. | `yardswaps-ai-lists-it-4x5.mp4`, `-1x1`, `-9x16` |
| **2. Find it nearby.** | 15 s | "Need equipment? Find it nearby." The home feed (Katy, TX) scrolls, and forklift, boom lift, combi oven and vacuum truck cards lift out of the phone ("Commercial and industrial equipment. All local." after the Nov 15 re-cut; the old cut said "33 categories"). Then a tap opens the backhoe listing, with pills for price, condition, hours and location. | `yardswaps-find-it-nearby-4x5.mp4`, `-1x1`, `-9x16` |
| **3. Free to list. No cut of the sale.** | 14 s | A big "$0 to list your equipment." flips to "$0 taken from your sale." Then a buyer sends a $13,800 offer on a forklift in the real app, and a "You keep all $13,800" pill pops up: "They pay you directly. All of it." | `yardswaps-free-to-list-4x5.mp4`, `-1x1`, `-9x16` |

Sizes: 4x5 is 1080x1350 (best for LinkedIn, Facebook and the Instagram feed), 1x1 is 1080x1080 (X and LinkedIn), and 9x16 is 1080x1920 (Reels, TikTok, Shorts, Stories). The 9x16 cuts were re-laid out on Oct 10 for the Reels safe zone: headline and app sit between 220 px from the top and 1500 px down, clear of the right-side buttons, so the bottom caption and icons cover only background. The earlier 9x16 cuts are in `previous/9x16-before-reels-fix/`.

The phone screens are real recordings of the current app code (Oct 10), run with sample listings that use the stock photos and a "YardSwaps Demo" seller. No real customers are shown.

The previous nine motion videos (idle gear, 3 steps, free storefront) are in `assets/motion/previous/` in case any are still wanted.

## Set 2 (Oct 11): chat, saved searches, categories

Same format and sizes, with music (silent copies in `silent/`; 16x9 has `-music` and silent versions).

| Video | Length | What happens | Files |
|---|---|---|---|
| **4. Message the seller.** | 12 s | A buyer asks to see the forklift run Saturday, the app's pickup safety tips show up, and the seller replies "Saturday at 10 works." | `yardswaps-message-the-seller-*` |
| **5. Save a search. Get alerts.** | 12 s | Search "forklift", tap Save search ("We'll notify you about new matches"), then Saved shows the search with push and email alerts on. | `yardswaps-save-a-search-*` |
| **6. Sell your...** | 15 s | "Sell your" stays while the second line flips with the category chips: fleet trucks, forklifts, aerial lifts, restaurant gear, farm equipment, laundry machines. Ends on "And more. Free to list." (Nov 15 re-cut; the old cut said "33 categories") | `yardswaps-every-category-*` |


## Set 3 (Oct 14, weekly routine): offers, storefront, follow

| Video | Length | What happens | Files |
|---|---|---|---|
| **7. Make an offer.** | 13 s | A buyer taps a $13,100 quick pick on the forklift with a note, the seller counters at $14,000, one tap accepts, and the listing shows "Offer accepted" with Message seller. | `yardswaps-make-an-offer-*` |
| **8. Your own storefront.** | 15 s | "Selling a lot? Get a storefront." A demo dealer page ("Your Equipment Co.") with hours, service area and verified badge, the inventory scrolls, then a search for "lift". | `yardswaps-dealer-storefront-*` |
| **9. Follow a seller.** | 13 s | From the mini excavator listing, open the seller, tap Follow, and the app confirms it will alert you when they post. | `yardswaps-follow-a-seller-*` |

Builders: `source/app-first/n789.js`. Recording: `source/recording/recall3.js` (modes offer2, store, follow; mock options counter and store).

## Set 4 (Oct 21, weekly routine): seller videos, free boosts

All three are for sellers and end on "Free to list. Free boosts." Boost wording is the app's own (Free boosts card, publish confirmation, Dealer boost tile).

| Video | Length | What happens | Files |
|---|---|---|---|
| **10. List 4, all boosted free.** | 16 s | My Listings shows 3 listings and the Starter boost countdown (3 of 4 listed), AI fills in a 4th from a photo, publish, "Starter boost on: 4 listings boosted free", and all 4 rows show the Starter boost badge. | `yardswaps-list-4-boosted-free-*` |
| **11. Already on Craigslist?** | 15 s | Paste the link to your own Craigslist post, the flatbed truck's photo and details fill in, a seller who has a free boost credit picks "Free · 7 days (1 left)" and publishes: "Your free boost runs until Oct 28." On-screen: "Got a free boost? Use it as you publish." | `yardswaps-already-on-craigslist-*` |
| **12. See what buyers want.** | 17 s | Dealer plan only: the Buyer demand report (categories, top searches, counts rounded to 5; NEVER show the "Searches that found nothing" section, Alan 11-10; clip held until re-cut), then a Dealer boost on the boom lift listing. | `yardswaps-see-what-buyers-want-*` |

Builders: `source/app-first/n101112.js`. Recording: `source/recording/rec10.js` (modes starter, craigslist, demand) with mock option `promo` (starter, craigslist, dealer). Demo data only: generic search terms, the demo "Your Equipment Co." dealer, stock photos.

## Set 5 (Oct 28, weekly routine): spare part, invite a seller, cold start

Seller-first, situation-first open, comment question on the end card (`ASK=`), music rotated per video. Real app at 3x with stock photos; no AI images.

| Video | Length | What happens | Music | Files |
|---|---|---|---|---|
| **Snap it, list it.** | 19 s | POV snap: a phone frames an idle compressor and takes the photo, then AI fills in the listing and it goes live free. Asks "What would you snap first?" | sunny | `yardswaps-snap-it-list-it-*` |
| **Spare part, one photo.** | 21 s | POV snap of a spare gear motor on a bench ("POV: the spare motor / doesn’t fit anything you own."), then one photo in the app: AI fills in title, category (Pumps & Motors), condition and description, suggests $150 to $300; the seller sets the price and it goes live free. No part numbers or fitment claimed. Asks "What spare parts are sitting in your shop?" | grit | `yardswaps-spare-part-*` |
| **Invite a seller.** | 19 s | "POV: your buddy’s tractor / hasn’t moved since spring." Profile, Free boosts card, Invite a seller, Share invite (code KATY42), then the friend’s sign-up form with the code filled in. "You both get a free 7-day boost" with pills "After their first listing / has been live 3 days". Asks "Who do you know with gear sitting idle?" | lift | `yardswaps-invite-a-seller-*` |
| **Show the cold start.** | 18 s | "POV: every buyer asks / “does it start?”" One photo, AI fills it in, then Add a walkaround video ("Video ready to upload", up to 3 minutes), set the price, live free. Asks "Which of your machines is hardest to start?" | punch | `yardswaps-show-the-cold-start-*` |

Builders: `source/app-first/n151617.js` (n15 part, n16 invite, n17 cold start; n14 = snap-it-list-it is n1 with `SNAP=`), finish with `source/app-first/mk.sh nX id style` (env OP or SNAP, ASK). Recordings: `source/recording/recpart.js` (env `SCANF=part-scan.json UPIMG=part.jpg`, mock.js reads them), `recinv.js`, `reccold.js`. Snap opener: `SNAP="photo.jpg|l1|l2|m1|m2"` (photo in `source/app-first/sit/`).

## Weekly 16:9 compilations (from Oct 21)

Alan chose "Combine weekly" for YouTube 16:9 on Oct 21: no more one-clip 16:9 uploads. Each week's clips go up as one video, Saturdays 8:30 am Central (the YouTube thread uploads it and posts to LinkedIn). Built from the silent 16x9 files: the opening cover stays only on the first clip, the end card only on the last, 0.3 s fades between clips, one continuous music bed. Script: `source/weekly-make.py N style id1,id2,...`.

| File | Length | Clips | Goes up |
|---|---|---|---|
| `yardswaps-weekly-1-16x9-music.mp4` | 50 s | free-to-list, ai-lists-it, list-4-boosted-free, already-on-craigslist | Sat Oct 24 |
| `yardswaps-weekly-2-16x9-music.mp4` | 41 s | every-category, dealer-storefront, see-what-buyers-want (seller-only recut, Oct 21) | Sat Oct 31 |
| `yardswaps-weekly-3-16x9-music.mp4` | 50 s | spare-part, invite-a-seller, show-the-cold-start (music: tech) | Sat Nov 7 |
| `yardswaps-weekly-4-16x9-voice.mp4` (and `-music`) | 1:21 | stripped-well-pump, control-panel-pulled, drilling-rig-parked, pressure-washer-1000-psi, building-things-concrete-mixer, bluecollar-shelf-parts (music: lift, narrated) | Sat Nov 14 |

Compilations are seller clips only (Alan, Oct 21).

From Oct 28 on, each Wednesday batch also makes the next weekly-N from that week's three new videos.

## YouTube and influencer sponsor spot (16x9)

Added Oct 10. Each video also comes in 16x9 (1920x1080) for regular YouTube: `yardswaps-ai-lists-it-16x9.mp4`, `yardswaps-find-it-nearby-16x9.mp4`, `yardswaps-free-to-list-16x9.mp4`. The 9x16 files work as YouTube Shorts.

`yardswaps-sponsor-38s-16x9.mp4` is a 38 s sponsor spot for the end of an influencer's YouTube video: Find it nearby, then AI lists it, then Free to list, ending on the end card with the store badges. The plain file is silent so the creator can talk over it; `yardswaps-sponsor-38s-16x9-music.mp4` and the three `-16x9-music.mp4` files have the same music as the social cuts. The creator still has to disclose the sponsorship in their own words and turn on YouTube's paid promotion setting.

## Covers / thumbnails (standard for every video)

Every video opens on its cover for 0.5 s, then fades into the motion (music starts at 0.5 s), so Instagram and TikTok use the cover by default. Build: `source/app-first/cover-frames.js` renders cover frames at video sizes; ffmpeg xfade 0.3 s at 0.5 s plus adelay 500 ms. Pre-cover cuts: `previous/before-cover-frame/`.

Every video gets a matching cover in `assets/motion/thumbnails/`: `yardswaps-<video>-cover-reels-9x16.jpg` (1080x1920; words and phone sit inside the middle 3:4 that the profile grid shows), `-cover-feed-4x5.jpg` (1080x1350) and `-cover-youtube-16x9.jpg` (1280x720, under 2 MB). The sponsor spot has a YouTube cover only.
Layout: light gray, YardSwaps pill, two-line headline (slate + blue), the real app screen on a tilted phone, one to three stock-photo listing cards with prices, and an optional blue badge ("AI", "$0").
Instagram: when posting a Reel, tap Edit cover, then Add from camera roll. YouTube: Details, Thumbnail, Upload file.
Rebuild: `source/app-first/thumb.html` (per-video words in `C`) and `node thumbs.js` from the renderer folder.

## LinkedIn post copy

Post from the company page with the 4x5 file. On your own profile, add "I work on YardSwaps" and put the link in the first comment.

**1. AI lists it**
> Listing a piece of equipment shouldn't take an afternoon.
>
> On YardSwaps you add a photo and AI fills in the title, category, condition and description, and suggests a price range. You check it and post.
>
> Free to list. No cut of the sale. yardswaps.com

**2. Find it nearby**
> Need a forklift, a boom lift or a combi oven this week?
>
> YardSwaps shows used work equipment from sellers near you, from fleet trucks to restaurant gear. Tap a listing, message the seller, and pick it up locally.
>
> yardswaps.com

**3. Free to list**
> $0 to list. $0 taken from your sale.
>
> Buyers make offers right in the YardSwaps app and pay you directly at pickup, so the whole price is yours.
>
> List your idle equipment at yardswaps.com

Hashtags if you want them (2 or 3 max on LinkedIn): #equipment #smallbusiness #construction

## Rebuilding or editing

`assets/motion/source/app-first/` holds the animation (`app.html`, `n23.js`) and the render script. `assets/motion/source/recording/` holds the scripts that run the app with sample listings and record the screens. To change a line, a photo or the timing, ask in the "Motion design videos" thread and it can be re-rendered.

## Instagram captions (Reels, 9x16)

Links don't click in Instagram captions, so each one says "Link in bio". Up to 5 hashtags.

**1. AI lists it**
```
Listing equipment shouldn't take all afternoon.

Add a photo and AI fills in the title, category, condition and description, and suggests a price. You check it and post.

Free to list. No cut of the sale. Link in bio.
#usedequipment #equipmentforsale #smallbusiness #contractor #heavyequipment
```

**2. Find it nearby**
```
Need a forklift, a boom lift or a combi oven this week?

YardSwaps shows used work equipment from sellers near you. Tap a listing, message the seller, pick it up locally.

Link in bio.
#usedequipment #equipmentforsale #forklift #restaurantequipment #smallbusiness
```

**3. Free to list**
```
$0 to list. $0 taken from your sale.

Buyers make offers right in the app and pay you directly at pickup. The whole price is yours.

List your idle equipment free. Link in bio.
#usedequipment #equipmentforsale #smallbusiness #contractor #sellyourequipment
```

## Long seller how-to: How to list equipment (Oct 21)

`yardswaps-how-to-list-walkthrough-16x9-music.mp4` (1920x1080, 2:09, music; silent copy in `silent/`, cover `thumbnails/yardswaps-how-to-list-walkthrough-cover-youtube-16x9.jpg`). A step-by-step walkthrough in the real app at 3x: sign up, add photos, AI fills it in, check condition and specs, set the price, publish free (paid boosts optional), how free boosts work, then unlocking the Starter boost with a 4th listing. Each step has a "STEP N OF 8" tag, a two-line caption and one plain sentence of explanation. Builder `source/app-first/n13.js`, recorder `source/recording/rec13.js` (mock `promo:'walk'`).

YouTube chapters (each at least 10 s, times include the 0.5 s cover):
0:00 Sign up
0:18 Add photos, AI fills it in
0:39 Check the details and specs
1:00 Set your price and publish
1:23 How free boosts work
1:49 Unlock the Starter boost

## Set 6 (Oct 30, Friday routine)

| File id | Opener (situation cover) | Music | Length | Notes |
|---|---|---|---|---|
| sold-it-list-the-next | flatbed-truck, "When the buyer shows up / and it starts first try." | drive | 16 s | My Listings status pill, Sold, then a second phone lists the next one. Builder `source/app-first/n181920.js` (buildN18), recorder `source/recording/recsold.js` (mock promo `sold`: three own rows, PATCH sets status). |
| that-trailer-next-season | enclosed-trailer, "Me pretending I'll use that / trailer again next season." | sunny | ~19 s | canva-18 trailer photo, AI fills Type: Enclosed. buildN19 (shared `sellShort`), recorder `recsell.js` with SCANF=trailer-scan.json UPIMG=trailer.jpg CLIP=trailer. |
| forklift-sitting-there | warehouse-racks, "POV: you finally deal with / the forklift that's been sitting there." | tech | ~19 s | canva-91 forklift, AI picks Electric, 2-Stage, Cushion. buildN20, recorder `recsell2.js` (SCR=300,300,300,300,320 UP=1470). |

## Long seller how-to #2: Move your Craigslist listings (Oct 30)

`yardswaps-how-to-move-craigslist-listings-16x9-music.mp4` (1920x1080, about 2:14, music grit; silent copy `yardswaps-how-to-move-craigslist-listings-16x9.mp4`, cover `thumbnails/yardswaps-how-to-move-craigslist-listings-cover-youtube-16x9.jpg`). Opens on the flatbed-truck POV card, then 7 steps: open the import, paste the link, photos and details copy in, check the price, condition and specs, publish (optional free boost), find it in My Listings. Builder `source/app-first/n21.js`, recorder `source/recording/rechow2.js` (mock promo `craigslist`).

YouTube chapters (each at least 10 s, times include the 0.5 s cover and 1.8 s opener):
0:00 Why move your Craigslist ads
0:12 Open the import
0:23 Paste the link
0:37 Photos and details copy in
0:53 Check the price
1:06 Condition and specs
1:35 Publish
2:00 Find it in My Listings

## Music from Nov 2026 batches: ElevenLabs tracks (Oct 31)

From the next weekly batch, every Short, how-to and weekly compilation uses the licensed ElevenLabs instrumentals instead of the synth.py beds: `assets/elevenlabs/music/yardswaps-music-{tech-120,drive-118,punch-124,sunny-122,grit-116,lift-126}bpm.mp3` (Creator plan, commercial license confirmed by Alan; all checked wordless). Same six style names, same rotation rule (no two Shorts in a batch and no two days in a row share a style), Shorts stay voice-free, and every video keeps its silent copy. `source/app-first/mk.sh` now picks the track for the style automatically (trimmed to the video length, 1.6 s fade-out, loudnorm -16 LUFS); set `SYNTH=1` to fall back to synth.py. Oct 31 (Alan: upgrade everything not yet posted): the Oct 28 and Oct 30 Shorts (all sizes), the Craigslist how-to music cut, weekly-3, the forklift commercial 9x16/4x5/1x1 (drive) and the sponsor spot (tech) were remuxed onto the ElevenLabs tracks from their silent copies, same file names, same styles (script `elmux.py` in the Motion thread scratchpad; old synth versions not kept in the project). Later on Oct 31 (Alan: "video 10 still uses the old sound") the posted ones were moved onto ElevenLabs too; synth versions are in `assets/motion/previous/synth-music/`.
Narrated how-to: `yardswaps-how-to-move-craigslist-listings-16x9-voice.mp4` (English) can post as its own YouTube video. The Spanish `-voice-es.mp4` must not be posted until Alan or Emmanuel proofreads it. Details in ELEVENLABS-PRODUCTION.md.

## Situation-first open (from Oct 28)

Every seller Short now opens on the seller's situation before the app: cover (~0.5 s), then 1.8 s of a full-screen idle-gear stock photo with a POV hook on a white card, then the phone rises in as before. Reason: the Oct 26 YouTube report found HeyCatch's POV Shorts average about 700 views and ours about 7. Code: `withOpener` in `source/app-first/app.html`; details and this week's hooks in MOTION-BACKLOG.md.

## Commercial: the idle forklift (Oct 26)

A 44 s story commercial, seller-first, same house style. One forklift (the canva-80 stock photo) runs through the whole story: cover = opener first frame ("POV: the forklift / hasn't moved in months."), then "Someone nearby / could use it." The seller adds one photo and AI fills in the specs ("Add one photo. / AI fills it in.", "Specs included. / You check them."), sets the price and publishes free ("Set your price. / List it free.", pills "$0 to list", "List 4, all boosted free"), "It's live." The phone slides to a buyer 6 mi away who searches forklift and sends a $13,800 offer with "Can I see it run Saturday?", then back to the seller, who accepts in My Offers and replies "Saturday at 10 works." End card: "Got idle gear? List it free. / Free to list. Free boosts." with the store badges and a small "Demo listings and accounts. Dramatization." line. No view or sale promises.

Files: `yardswaps-commercial-idle-forklift-9x16.mp4`, `-4x5`, `-1x1` (music; silent copies in `silent/`), `-16x9-music.mp4` (YouTube) and `-16x9.mp4` (silent). Covers in `thumbnails/` (reels and feed = the opener frame; YouTube = designed "Idle forklift? / List it free." thumbnail). Music: synth.py `drive`, 118 BPM, hit on the end card.

Rebuild: recordings with `source/recording/story.js` (modes sell, buy with ROLE=buyer, deal with ROLE=seller; MOCK=./mockc), app started with `recording/app-up.sh` (stubs in `recording/stubs/`, includes an Alert stub so confirm dialogs complete on web). Builder `source/app-first/n14.js`, render `node renderapp.js n14 W H out.mp4`, finish with `python3 finish-story.py <raw-dir> <out-dir> drive`, YouTube cover `node thumbs-story.js`.


## Oct 31 rebuild: videos 1-12, weekly 1-2, sponsor, 1440p how-tos

Alan asked to bring the Oct 10-21 videos up to the current style, use believable imagery, and mix in real YardSwaps listing photos ("just the equipment images", no faces, no seller details, mix with the generic ones, best ones up front). Done:
- Videos 1-12 rebuilt with the situation-first POV opener (0.5 s cover + 1.8 s), a comment question on the end card and new covers (thumbnails/). Openers: 8 from real listing photos (tractor, Hyundai excavator, red day cab, crane dump truck, dozer, Deere mini excavator, Hotsy washer, Takeuchi), 4 stock (pickup on trailer, warehouse racks, backhoe on trailer, enclosed trailer). Music rotation 1 tech, 2 drive, 3 punch, 4 sunny, 5 grit, 6 lift, 7 tech, 8 drive, 9 punch, 10 sunny, 11 grit, 12 lift. Hooks and questions: `source/app-first/rebuild12.sh` (n2: real-hyundai, "POV: you need an excavator / by Monday.", drive).
- Sample listings (`source/recording/listings.js`) now mix 13 real listing photos (assets/real-listings/, equipment only, mock titles, prices, places and the generic demo seller) with the stock ones, best real ones first. Feed, listing, search and category screens re-recorded from main (Oct 31) and time-warped onto the old timing; offer, chat, storefront, follow, starter, Craigslist and demand screens kept from the earlier recordings.
- Weekly 1, weekly 2 and the sponsor spot (now 41 s) rebuilt from the new clips. Old-style files in `assets/motion/previous/old-style-oct10-21/`.
- Both long how-tos rendered at 2560x1440 (`DSF=1.3333333`), same timing; 1080p copies in `previous/1080p-howto/`.
- Already-posted versions on YouTube and other channels were not touched.

## Nov 1: whole phone in frame, every video (Alan: "not cutting off the phone views in any of the videos")

Rule from Nov 1: the whole phone, all four bezel edges, stays inside a per-aspect safe box on every frame of every size. No camera zoom-ins; the phone is shown at the largest size that fits the safe box. Template change in `source/app-first/app.html` (`?nz=1`, set by `NZ=1` in the environment for `renderapp.js` and `mk.sh`): the camera clamps to `SAFE`, the stage mask is off, the entrance is a short rise and scale instead of a slide from below, and the story commercial's side-to-side phone slides became an in-frame fade (`n14story.js`, wired into `app.html` as `n14s`). The previous template is `app.pre-whole-phone.html`.

Re-rendered under the rule, same copy, same music, same durations: Shorts 1 to 12 and 14 to 20 (all four sizes), both narrated how-tos at 2560x1440 (English, Spanish and music cuts; the Craigslist one keeps its 1.8 s POV opener so the 134.0 s narration mix still lines up), the forklift commercial (app clips re-recorded Nov 1 from main with `source/recording/story.js`, raw frames in `source/recording/raw-story-nov1/`, time-warped onto the builder's frame anchors), weekly reels 1 to 3 and the sponsor spot. Scripts: `redo-whole-phone*.sh`, `voice-remux.sh`, `weekly-make-op.py`. The files these replaced are in `previous/pre-whole-phone-nov1/`. Already-posted videos on YouTube and other channels were not touched.

Render gate: `python3 -I video-upgrade/tools/cropaudit.py <files>` must come back clean before a file goes to yardswaps-media. Known false positives: the end-card circle reveal (reported as "phone-top-cropped" in the last 3 s), a full-bleed opener photo (left/right edge in the first 2.5 s), floating listing cards that overlap the phone's outline (find-it-nearby around 6 s), and a chapter crossfade in the how-tos.

Next: the v2 upgrade plan in `video-upgrade/UPGRADE-PLAN.md` (callout cards instead of zooms, match-cut opener, SFX on taps), Shorts 1 to 12 first. From Nov 1, new cuts are built from the best-performing videos of the last 14 days and the posting queue is ordered by engagement (UPGRADE-PLAN.md section 5).

## Nov 1 (evening): v2 cuts of every video

Alan (Nov 1): keep building the upgrade and deploy every improvement. So every video was re-cut in the v2 style from `video-upgrade/UPGRADE-PLAN.md`, same recordings, same copy, same music, same durations as the morning's whole-phone cuts (the Shorts are 0.2 s longer because the opener is 2.0 s instead of 1.8 s; the n3 free-to-list cut lost a 3.4 s text intro and is 13.1 s):

- POV photo opens full screen and flies into the phone on a shutter (match cut); the phone stays whole on every frame; detail comes from a callout card beside the phone instead of a zoom-in; captions reveal word by word; every tap has a sound; the end card wipes in as a blue circle with the question.
- Audio: -14 LUFS integrated, music ducks about 3 dB under each tap, true-peak target -2.0 dBTP with the `fast` AAC coder (the default coder clipped the tap transient to +1.6 dBTP on 1 file in 6).
- Files: same names in `assets/motion/` (19 Shorts x 4 sizes + silent copies in `silent/`, the forklift commercial, `weekly-1/2/3-16x9-music`, `sponsor-38s-16x9` and `-music`, both how-tos at 2560x1440 with `-music`, `-voice`, `-voice-es`). The morning's files are in `previous/pre-v2-nov1/` (with the old thumbnails). New thumbnails in `thumbnails/` are frame 0 of each cut (the POV card over the photo).
- The how-tos keep the old timeline plus the 0.5 s cover hold, so the existing ElevenLabs narration mixes line up unchanged (129.4 s and 134.0 s); the voice cuts are now normalised to -14 LUFS like everything else. Step tags and notes carried over.
- Weekly reels and the sponsor spot are compiled from the v2 silent 16x9 cuts (opener only on the first clip, end card only on the last, tap sounds carried over): weekly-1 49.8 s, weekly-2 43.4 s, weekly-3 44.3 s, sponsor 37.8 s.
- `yardswaps-media` `reels/library/` holds the v2 9x16 cuts under the same names (commit "Reels library: v2 cuts of all 20 videos"), so the Reels poster and HeyCatch pick them up without any change to `library.json`.
- Already-posted videos on YouTube, Instagram, Facebook and TikTok were not re-uploaded.

How it was done: `video-upgrade/source/v2-port/` (README there). The old builders were replayed frame by frame to a timeline spec, converted to a v2 playback spec and rendered with the v2 template; `batch.sh` runs the four sizes plus `finish.py`, `cropaudit.py` and `audioaudit.py`. New videos should be written for the v2 template directly (`video-upgrade/source/v2/`), not ported. Known cropaudit false positives on v2 cuts: the match cut at 2.5 s, a scene fade with a callout ghost, the end-card circle.

## Nov 1 (night): the opener must show the machine on screen (Alan: "the forklift reel isn't even taking a picture of a forklift")

The v2 match cut makes the POV photo become the listing photo, so a photo of the wrong machine is now glaring. Audit of all 20 recordings against each opener: 11 openers showed a different machine than the recording. Fixed, re-rendered (all four sizes, silent copies, covers) and redeployed under the same names:

| Video | Recording shows | Opener was | Opener now |
|---|---|---|---|
| forklift-sitting-there | Electric warehouse forklift listing | warehouse racks | forklift-yard |
| save-a-search | search "forklift" | warehouse racks | forklift-yard |
| free-to-list | offer on the propane forklift | Peterbilt day cab, "the old day cab" | forklift-yard, "the old forklift is just taking up space" |
| message-the-seller | chat about the forklift | pickup on a trailer | forklift-yard |
| make-an-offer | counter-offer on the forklift | backhoe on a trailer | forklift-yard |
| ai-lists-it | Swan air compressor listing | tractor, "the tractor hasn't moved" | air-compressor, "the compressor hasn't moved since spring" |
| list-4-boosted-free | Swan air compressor listing | Hotsy pressure washer | air-compressor |
| find-it-nearby | backhoe loader listing | Hyundai excavator, "need an excavator" | backhoe-on-trailer, "you need a backhoe by Monday" |
| follow-a-seller | mini excavator listing | Deere tractor | mini-excavator |
| already-on-craigslist | flatbed work truck import | enclosed trailer | flatbed-truck |
| see-what-buyers-want | boom lift listing | Takeuchi mini excavator | boom-lift |

Pass: every-category, dealer-storefront (mixed feeds), snap-it-list-it, spare-part, invite-a-seller, show-the-cold-start, sold-it-list-the-next, that-trailer-next-season, commercial-idle-forklift, both how-tos. Old files in `assets/motion/previous/pre-fix-nov1/`.

In `yardswaps-media`, the held `forklift-sitting-there` stays held (its post is live); the fixed cut is the new slug `forklift-finally-deal` (added Nov 1, posts next). The other ten were replaced under the same file names.

Render gate, third check: `python3 -I video-upgrade/tools/objectaudit.py r/spec/<id>.json` (hand-maintained tables: sit photo -> machine, recording -> machine, machine words the copy can name). `batch.sh` and `howto.sh` run it first and refuse to render on a failure; a photo or recording missing from the tables also fails, so new assets get tagged when they are added. Then cropaudit and audioaudit after the render, as before.

Narration mixes (`voicemux.py`): plain gain to -14 LUFS with a brick-wall limiter at -4 dBFS, then the audio is encoded with both ffmpeg AAC coders and the one with the lower decoded true peak is muxed. Each coder overshoots by up to 4 dB on some material (twoloop on tap transients, fast on the Craigslist narration), so it is measured per file, not assumed.

Also Nov 1 night: `surplus-parts-cash-flow` (19 s, tech), a new v2 Short built from the Meta Page assistant insight Alan shared (Shorts about one concrete jobsite problem reach 300+ views): the surplus parts shelf, one photo of the gear motor, AI reads the nameplate and part number, buyers search by part number, end question "What's the oldest part still on your shelf?". Spec `video-upgrade/source/v2-port/spec/n22.json`, cloned from spare-part. Posted the same night as a one-off Reel and Story on IG and FB by the Reels thread. Pills fix in `v2play.html`: when a later pill group lands, the earlier group leaves (spare-part had the Price pill drawn over Condition and Description); only spare-part and the new cut had more than one group, both re-rendered. Rule going forward (Alan, Nov 1): every new Short names one jobsite problem in its opener, proximity-search style.

Also Nov 1 night (later): `surplus-parts-labels` (19 s, tech), the same cut re-shot after Alan asked for "a better part, maybe an actual part tag or label". The gear-motor stock shot and the old `part` recording were replaced by a real listing photo of new-surplus Eaton Field Mate hydraulic cylinders with the factory part labels on the bags (`real-listings/parts-cmvfkzdav0022pc3arlodzkj0.jpg`, cropped to `sit/surplus-cylinders-9x16.jpg` and `-16x9.jpg`), and the sell flow was re-recorded against the real app running locally with that photo (`video-upgrade/source/rec/recpart2.js` + `part2-scan.json`; the scan stub must name a real category, `agriculture`, because the app does not auto-fill the `parts` fallback). Spec `n23.json`, frames remapped onto the new recording by its tap times. Copy: "Snap the part. Label and all." / "AI reads the label. Part number, specs." Pushed to `reels/library` as a NEW slug so it posts as a new Reel; `surplus-parts-cash-flow` stays as posted. objectaudit gained `surplus-cylinders`, `part2` and the word `cylinder`.

### Nov 2 (early): small parts and the category range

Alan, Nov 1 night: "We should also line up small parts, this is not just for big stuff. Go read how many classes we support in YardSwaps." Eight new 19 s Shorts, every one from a real listing photo in `assets/real-listings/` (equipment only) with the sell flow recorded in the real app against that photo (`video-upgrade/source/rec/rec_<clip>.js` + `<clip>-scan.json`): micrometer-set-small-tools and boring-bars-tooling (Metalworking & CNC), chop-saw-small-tools (Power & Hand Tools), condenser-changeout (Commercial HVAC), pressure-washer-replaced (Pressure Washers), air-mover-fleet (Warehouse Storage), spare-truck-wheel (Auto Shop Equipment), leftover-anchor-adhesive (Concrete & Masonry). Specs `n24` to `n31`, all cloned from `n23` with the scene frames remapped onto each recording by its three tap frames. The 33-category coverage table and the Monday rotation rule are in MOTION-BACKLOG.md ("Nov 2: cover all 33 categories"); 17 of 33 covered after this batch.

Two pipeline fixes from the same night. (1) `batch.sh` now refuses to deploy a cut whose render log has no `done` line: two renders died mid-way (Chromium screenshot failure once the scratch disk filled) and the truncated 3.6 s and 5.2 s files sailed through the crop and audio audits, so a length gate was the missing check. (2) `finish.py` measures the encoded file and, when loudnorm's linear mode backed off from the true-peak ceiling (the punch track landed at -15.8 LUFS), adds the shortfall as plain gain after loudnorm and before the limiter, up to twice; the gain has to go after loudnorm because its dynamic fallback eats a pre-gain. Also: check the opener photo on the contact sheet by eye before pushing; two of tonight's photos were picked by the wrong index off a sheet (a floor machine labelled as an air mover, Hilti cartridges labelled as a wheel) and objectaudit cannot see that, it only checks names. Both were re-shot; the Hilti photo became its own cut.

## Nov 2 (early): the part-tag scan Short (Alan: show a user using a part tag and the AI pulling up info)

- Checked the app before writing a frame: `apps/web/app/api/scan-label/route.ts` tells the model to read nameplates, plates and stickers first and to fill `manufacturer`, `model`, `partNumber`, `year` and `specs` only from legible text (null otherwise). The Sell screen then shows those in "specs & details" and offers "Look up manufacturer specs" (web-searched sheet). So a tag video is accurate as long as the on-screen values are what the label actually says.
- `part-tag-scan` (n32, key `tag`): real Eaton Field Mate cylinder photo; the label reads EATON / FIELD MATE / 5008 FM(SHORT) / 2500 PSI / 172 BAR MAX. OPERATING PRESSURE. The scan stub (`source/rec/tag-scan.json`) fills exactly that. Opener is a tall crop of the labelled stack (`sit/part-tag-9x16.jpg`). `rec_tag.js` scrolls to the Manufacturer / Model / Part number fields and holds there 2.6 s so the callout can sit on them.
- Not shown: the "Look up manufacturer specs" result. A web search did not confirm the 5008 FM bore and stroke, so the sheet would have been invented. Show it only once a real lookup result is on hand.
- Caption lines that wrap on the 9x16 render get cut (two re-renders here): keep line 2 under about 26 characters.
- Reels thread (02:51Z): part-tag-scan posts Mon 22:30Z; its closing question was swapped to "Which part number do you know by heart?" (the review page and library match). The end card still says the old line; fine for this run. Next render: category in the stub could read Pumps & Motors instead of Farm & Ag for hydraulic cylinders, and the end-card ask should match the library question.

## Nov 2: "step 01 covered by the titles" report and the overlap gate

Alan reported the STEP 1 OF 8 tag being covered by the big titles in the English 16:9 narrated how-to. The deliverable files in `assets/motion` (EN and ES, Craigslist and How-to-list) were already correct at every step change: the step tag sits on its own line above the title. What Alan saw was the review page's narrated preview, an older render where the tag wrapped word per line into the title. Fresh 720p previews of all six how-to files were republished (page v43). Nothing in `assets/motion` or the YouTube upload queue changed, so Wednesday's Craigslist upload uses the file it already pointed at.

Rule learned: when a review-page preview is republished, every preview file must be re-sent, because the artifact keeps files that are not passed, and a stale preview looks like a broken video.

Gate added: `v2play.html` now runs `overlapCheck()` at init. At the entry of every step tag, note and caption it renders the frame and logs `OVERLAP t=... <kind> "<text>" meets <kind> "<text>"` to console.error when a step tag, a title word or a note box intersect by more than 2 px, or when a step tag wraps taller than one line. `batch.sh` and `howto.sh` grep the render logs for OVERLAP and exit before finish.py, so an overlapping cut never reaches `final/`. Negative test: append `?ovtest=1` to the player URL (the tag box is forced to 60 px wide), which produced 72 OVERLAP lines on n13; a clean n13 produces none.

## Nov 2: three long-form 16:9 videos for the YouTube queue (Monday batch ask)

- yardswaps-parts-and-labels-16x9-music.mp4 (2:07, grit) and yardswaps-idle-gear-16x9-music.mp4 (2:13, drive): best-of compilations built with compile.py from the v2 silent 16:9 cuts (opener only on the first clip, later clips start 2 s in, cut at their TE, 0.3 s crossfade, sfx carried, finish.py music). Chapter times in YOUTUBE-SEO.md items 5 and 6.
- yardswaps-how-to-price-equipment-16x9{,-music}.mp4 (2:00, sunny, spec n33): seller guide in 7 steps recorded in the real app (rec_price.js: compressor photo, suggested price card, Use price, Answer offers automatically with accept 550 / floor 400, publish) plus the buyer side from offer2 (offer under the accept price, countered, accepted). Callout boxes were re-aimed from frame stills before the render (y values in the spec are measured, not guessed). Crop audit flags 49.75-51 s are the step-4 callout overlapping the tab bar, not a cropped phone.
- Narration (done Nov 3): 8 English lines (ElevenLabs flow 5L6wrO8GiMOuJWNI4ESd, Justin Case) in assets/elevenlabs/voiceover/en/howto-pricing-en-line0..7.mp3. The cloud container cannot download from elevenlabsusercontent.com, so a session on Alan's PC fetched them and pushed them to yardswaps-media narration/howto-pricing/ (commit fe06cf9); the cloud side pulled from GitHub. Mix: mix33.py (bed = the music cut's own audio at -11 dB, sidechain-ducked under the voice, lines at chapter start + 0.6 s, loudnorm -15/-1.5) -> assets/elevenlabs/mixes/howto-pricing-en-final-mix.m4a, voicemux.py onto the silent master -> yardswaps-how-to-price-equipment-16x9-voice.mp4 (-14.1 LUFS, -3.7 dBTP). Same route works for any future narration: PC fetch -> media repo -> cloud.
- Queue rows 4-6 in YOUTUBE-UPLOAD-QUEUE.md; titles, descriptions, chapters, tags in YOUTUBE-SEO.md.

## Nov 3: ten more long-form 16:9 videos (Alan: "we should have at least like 10-20 long YouTube videos by now")

- Nine themed compilations built with `compile.py` from the v2 silent 16:9 cuts (same recipe as idle-gear and parts-and-labels; compile.py now also writes `out/<name>/chapters.json` and prints the chapter times, and knows `commercial-idle-forklift` as n14s): forklift-start-to-finish 1:41 tech, buyers-find-you 1:21 drive, full-tour 2:18 punch (videos 1 to 12), compressor-start-to-finish 1:20 sunny, free-boosts 1:13 lift, fleet-and-yard 1:28 grit, dealer-tools 1:18 lift, shop-tooling 1:26 punch, all-listings-marathon 6:21 drive (all 30 cuts; re-encoded at 1.8 Mbps, 56 MB, because GitHub refuses files over 100 MB in the media repo). Plus `yardswaps-seller-course-16x9-voice.mp4` (6:09, 1440p): the three English narrated how-tos (list, price, Craigslist) joined with 0.5 s video and audio crossfades, chapters 0:00 / 2:09 / 3:55.
- All passed audioaudit (-14 LUFS, true peak under -1.5; the forklift one was re-normalized once) and cropaudit (its flags sit on the 0.3 s crossfades, the phone rise-ins and callout overlays, checked by eye). Files and `-16x9.mp4` silent twins in `assets/motion`, covers in `assets/motion/thumbnails/yardswaps-<name>-cover-youtube-16x9.jpg` (the seller course reuses the walkthrough cover).
- Queue rows 7 to 16 in YOUTUBE-UPLOAD-QUEUE.md, titles, descriptions, chapters and tags in YOUTUBE-SEO.md items 7 to 16 (generated by `seo10.py` from `seo10.json` + chapters.json in the Motion scratchpad, copies in video-upgrade/source/v2-port/). The YouTube thread was asked to post one long video a day from Nov 3 instead of three a week. Count: 6 posted + 4 scheduled through Nov 7 + these 10 = 20.
- Next for volume: narrate the compilations' openers via the PC route when Alan wants voice on them, and build per-category walkthroughs as new category cuts land (3 a week from the Monday batch).

## Nov 3 (afternoon): parts stuck on a shelf, Alan's standing theme

Alan: the platform is also for gear laying around, extra plumbing parts, the old machine that is now a parts donor; scan the parts and make extra cash on what is stuck on a shelf. Four new Shorts (specs n34 to n37, all four sizes plus silent and covers in assets/motion) and one long video, yardswaps-parts-stuck-on-a-shelf-16x9-music.mp4 (2:04, nine parts listings, queue row 17, SEO item 17). Photos: a real listing photo (hydraulic thumb), Canva stock (gear wall) and two Wikimedia Commons photos (corporation stop, packaged PVC fittings) credited in yardswaps-media photos/plumbing/SOURCES.md. The two plumbing Shorts show the seller picking Parts & Other in the category list, because the app leaves that category to the seller even when the AI suggests it (apps/mobile/app/(tabs)/sell.tsx skips FALLBACK_CATEGORY); the thumb is filed under Excavators & Loaders and the gear lot under Metalworking & CNC by the AI itself. Captions were shortened to one line per size (17 characters or fewer per line) after the 16:9 and 1:1 cuts wrapped. Theme rotation and photo list: MOTION-BACKLOG.md "Nov 3". Scorecard tag: angle shelf-parts in yardswaps-media metrics/formats.json.

## Nov 3 (evening): narrated cuts for every unposted long video

Every compilation in the YouTube queue now ships as `-16x9-voice.mp4` (ElevenLabs narration, one line per chapter, see ELEVENLABS-PRODUCTION.md round 4). The silent and music cuts stay. From now on every new long video gets its narration before it goes to the queue: write the clip line in `assets/elevenlabs/voiceover/en/longform/scripts.json` when a new Short is built, and run mixlong.py on the compilation. Shorts stay without voice-over.

## Nov 5: the first YouTube video re-cut (how-it-works-v2)

Alan (YouTube thread, Nov 5): repost the first video (XJJPCWuhcW4, the silent 7-step 1:16 cut from Oct 10) with the improved style, music and narration. Built as a v2 compilation, not a re-shoot: every step already exists as a current-app v2 cut, so `compile.py how-it-works-v2 lift find-it-nearby,save-a-search,make-an-offer,message-the-seller,snap-it-list-it,free-to-list` (1:07, chapters 0:00 / 0:14 / 0:23 / 0:33 / 0:43 / 0:55), then `narr/mixlong.py` with the shared clip lines (no video-specific intro line: the cloud cannot fetch new ElevenLabs audio, and the find-it-nearby line already opens the video) and `narr/srtlong.py` for the caption file. Audits: audio -14.2 LUFS / -3.6 dBTP, crop flags only at the four scene fades. Files: assets/motion/yardswaps-how-it-works-v2-16x9-{voice,music}.mp4, silent/, thumbnails/yardswaps-how-it-works-v2-cover-youtube-16x9.jpg, assets/captions/yardswaps-how-it-works-v2-16x9-voice.en.srt; pushed to yardswaps-media week-2026-11-02/how-to-buy-and-sell-used-equipment-yardswaps-app-yardswaps.mp4 (a3e90c6). Queue row 18, SEO item 18.

## Nov 5: callout cards refined on every video

Alan (Nov 5, with a screenshot): "On all video these little screen need refinement sometimes they are misplaced or don't really show or follow anything." An audit of all 142 callouts (tap-vs-rect check plus OCR of the frames under each window) found 111 drifting (a live crop over a scrolling screen) or missing the element the caption named.

New template rule (`video-upgrade/source/v2/v2play.html`, `callouts()`): a callout is a frozen crop of one full-width row of the screen at a fixed frame, so it cannot drift; the card is 1.3x the phone width, centred on the phone just below the row it enlarges (above it near the bottom); a blue dot with a pulsing ring marks the control on the live screen and shows only while the live screen is on that frame (within 20 frames), so the dot never points at nothing; crops stop above the tab bar. Every callout is on for its caption's window. Each callout was re-aimed by reading the screen text (rapidocr) with the anchor tables in `video-upgrade/source/v2/callouts/anchors.py` (`anchor.py`, `stills.sh`, README there), then a still of every callout was checked by eye and 11 stragglers fixed by hand (chips row, Follow button, storefront inventory search, Dealer boost row, video-ready row, lift capacity specs, two description rows that sat under the header, two rows under the tab bar, a publish row caught on a modal fade).

Re-rendered and redeployed Nov 5: all 37 Shorts (four sizes, silent twins, covers; the Reels library too, yardswaps-media 3ac2e7f), the three how-tos (EN/ES voice muxes kept, same timeline), the 13 unposted compilations (forklift-start-to-finish, buyers-find-you, full-tour, compressor-start-to-finish, free-boosts, fleet-and-yard, dealer-tools, shop-tooling, all-listings-marathon, parts-and-labels, parts-stuck-on-a-shelf, weekly-3, sponsor-38s; narration re-muxed from the existing longform mixes, same chapter times) and the seller course. Not redone: commercial-idle-forklift (n14s; its Nov 1 recording frames were deleted from scratch, so it keeps the old callouts until re-shot) and the three already-posted long videos (idle-gear, weekly-1, weekly-2). Already-posted YouTube videos are not replaced; queued ones are re-pulled from assets/motion by the YouTube thread.

## Nov 5: YouTube covers for long videos

- Every long video needs `assets/motion/thumbnails/yardswaps-<slug>-cover-youtube-16x9.jpg` (under 2 MB); Zapier sets it right after each upload. Spotlight compilations get theirs from `batch.sh` (the POV photo with the headline). The how-tos and the seller course open on a blank 0.5 s hold, so `howto.sh` now takes the cover from the title card at 4.5 s instead of frame 0. The walkthrough, seller course and sponsor-38s covers were replaced by hand the same way (title card / "Need equipment? Find it nearby" frame).

## Nov 4 evening: hook box and trend-style music

- The closing question now also shows in the first ~3 s as a big blue rounded box (white Space Grotesk Bold on --blue) in the lower third, inside the Reels safe zone, then slides away as the phone enters. `hookBox()` in `video-upgrade/source/v2/v2play.html`; it reads `spec.hook`, else `spec.end.ask`; set `"hook": false` in a spec to skip it. Font shrinks until the text fits two lines.
- Three trend-style beds replace the synth.py beds on new Shorts: `waltz` (84 bpm, moody guitar + harpsichord), `phonk` (140 bpm, drill/phonk), `lofi` (86 bpm, chill). Files `assets/elevenlabs/music/yardswaps-music-{waltz-84,phonk-140,lofi-86}bpm.mp3` (take A; B takes in yardswaps-media `music/trend/`). Style keys in `finish.py` MUSIC map. Rotate them across the Monday batch; keep `tech`/`drive`/`grit` for long videos.
- Platform trending audio cannot be attached through any API. Recipe: post the music cut; when a sound is trending that week, re-upload the silent copy and pick the sound in the Instagram or TikTok editor.
- n38-n40 were re-rendered with the box and redeployed (media repo c507fe6).

## Nov 4: weekly batch (Wednesday routine)

Three Shorts in the v2 template, specs n38 to n40: stripped well pump (parts rotation, Wikimedia photo, no label so no part number on screen, Parts & Other picked by hand in the recording), control panel pulled (first Electrical spotlight, Canva stock) and drilling rig parked (first Drilling & Boring spotlight, Canva stock). Four sizes, silent copies, covers in assets/motion/thumbnails, 9:16 cuts in yardswaps-media reels/library dated Nov 4 (they post next), formats.json rows, captions in MOTION-CAPTIONS.md. The crop audit flags the 2.5 s frame on 4:5, 1:1 and 16:9 of every sell-flow Short: that frame is the full-screen photo preview inside the phone, not a cropped phone (checked by eye on every batch since Nov 3). The `drain-crew` stock shows workers and is not an opener; Hydro Jetting needs a photo. Scratch finals of deployed cuts are deleted after deploy now (disk), the recordings stay in mo/scr for compilations.

## Nov 7: Friday batch in the "demonstrate, don't explain" format, and the voice-over test

- Three Shorts from the trend picks (TikTok thread brief): 41 pressure-washer-1000-psi (search phrase "pressure washer"; the Hotsy nameplate has no PSI, so the hook has no number: "POV: you upgraded. The old pressure washer stayed."), 43 building-things-concrete-mixer ("building things") and 44 bluecollar-shelf-parts ("blue collar", made in 42's slot: no free-licence breaker photo, Wikimedia blocked from the cloud). The search phrase sits word for word in the hook card and the first caption line. Scorecard rows (`metrics/formats.json`): `demo: true`, `structure: problem-action-result`, and `voice: true` on 41 and 43.
- Format (specs built by `mkdemo.py` in the Motion scratchpad, template additions in `v2play.html`): the machine fills the screen for the first 4 to 5 s with movement from frame 0 (`opener.move` push or pan, optional second photo and `cut`), a loupe card enlarges its label (`opener.label` with a crop of the photo, placed per aspect ratio), the scan is shown as the action, the app part is five six-word captions of about 1.5 s, then `result` (a blue result line at the caption position plus a faded "before" card of the old photo with a slate chip, 30% white wash so the crop audit does not read it as bezel; the chip font shrinks until the label fits the 220 px card), end card. The text only states what the label or the app shows (no "find the match", no "no part number needed", no view or buyer promises).
- Recording: `recsell.js` has a `CATPICK=<category name>` step (taps "Choose a category", then the row in the picker sheet), because `sell.tsx` no longer files the fallback category from a scan, so Parts & Other has to be picked by the seller (44). Scan stubs washer/mixer/valve-scan.json; the valve stub reads "15MM" off the nut, matching the loupe.
- Voice-over test (Alan, Nov 5): 41 and 43 ship a third 9:16 cut, `yardswaps-<id>-9x16-voice.mp4`, for TikTok only: five Justin Case lines (ElevenLabs flow NJWBwjfxcNI9yJLm2thz; `narration/short/` in the media repo, fetched by the PC session, commit 29f10e9), placed by `narr/short/cues.json`, music cut audio at 0.28 sidechain-ducked, loudnorm -15/-1.5, muxed by `narr/mixshort.py`. The music-only and silent cuts stay; 44 and every other Short stay voice-free. Posters: the TikTok thread picks the -voice cut for these two; Reels and YouTube Shorts keep the music cut.
- Weekly-4 (16:9, lift): the six seller Shorts from this week (stripped-well-pump, control-panel-pulled, drilling-rig-parked, pressure-washer-1000-psi, building-things-concrete-mixer, bluecollar-shelf-parts). `compile.py` now keeps 2 s of the machine and hook box before the match cut on demo-format clips (`T` above 2.5 s) instead of cutting straight to the phone; `mixlong.py` ends the end-card window the same way. Narration: `intro:weekly-4` plus one clip line per Short (lines in `narr/scripts.json`, mp3s in media `narration/longform/`, commit 7845ac1 from the PC), muxed as `-16x9-voice.mp4`.
- Not made: long how-to #3 "How free boosts work". It needs a new recording pass (the Free boosts card and How it works sheet on the Sell screen, the invite screen, boost-on-publish), none of which the existing mo/scr recordings show at rest; next run, after the recording.
- Disk: the session's writable allowance filled during the raw-frame copy (the recordings were already in mo/scr; `r/raw` is now a symlink). Scratch finals of deployed cuts, old out_* folders and the duplicate weekly mp4s were deleted; keep doing that after each deploy.

## Nov 8: cadence raised to 14 Shorts a week

Per the Amplify thread (SHORTS-CADENCE.md): 10 new Shorts a week now (5 Wed + 5 Fri), 14 a week (7 + 7) from the week of Nov 16 once the photo pool covers the empty categories. Routine prompts updated Nov 8. House rules unchanged (music only, 12-15 s, question box, one jobsite problem up front, all gates). Every 9:16 also lands in yardswaps-media reels/library + library.json + formats.json and week-YYYY-MM-DD/.

## Nov 8: measured rules folded into the routines

From the feedback-loop read (Oct 25 to Nov 7): real item + question box in the first second, no app screen before 3 s; forklift and app-feature explainer Shorts paused; "one leftover item" Shorts for generators, pumps, vacuum trucks first; copy the micrometer set (159) and drilling rig (134) shape. Details in MOTION-BACKLOG.md "Measured rules from Nov 8".

## Nov 8 (afternoon): extra batch of seven and the 21-a-week cadence (Alan: "we need to stack it")

Alan asked whether we can post more TikToks within what we already pay for, then "we need to stack it" and "we might need to make more content". The ceiling is the library (no repeat within 10 days), so the fix is more clips, not more apps. Same afternoon: n45 to n51 cut in the demo format (compactor, combi oven, riding mower, prep line, laundromat washers, office desks, order kiosk), 17 s each, four sizes, all gates passed, deployed everywhere the Friday batch goes. Review page updated. Routines now run Monday, Wednesday and Friday with 7 Shorts each (21 a week), photo pass first; the Monday trigger is new. Library 43 -> 50; the Amplify thread was told so it can raise TikTok/Reels counts. Details in MOTION-BACKLOG.md "Nov 8 (extra batch)".

## Nov 8 evening: origin story set (Alan's story, brand/ORIGIN-STORY-KIT.md)

- Long: `yardswaps-origin-story-16x9-voice.mp4` (2:04, lift, nine Justin Case lines from kit section 3, music-only twin kept). New pre-roll path: `mkpre.py` builds a 42 s real-photo chapter reel (zoompan + blue-box text), `compile.py` takes it through `PRE=` and skips the usual first-clip trim, `narr/mixorigin.py` places the lines sequentially from `narr/origin-cues.json` and refuses a cut whose last line runs past the end. Order: pre-roll, origin-searched-everywhere, find-it-nearby, make-an-offer, message-the-seller, origin-sitting-cash, stripped-well-pump, snap-it-list-it. YouTube queue item 20, SEO item 20, cover text "Searched every app. Found nothing."
- Shorts (voice-free, measured format, captions from kit section 4, platform link lines above the closing question): `origin-searched-everywhere` (generator, drive, 16 s, new ogen recording: search generator, listing 16 miles away), `origin-part-in-a-yard` (well pump, lift, 17 s, new opump recording: search, listing 4 miles, Make an Offer, offer sent), `origin-sitting-cash` (copper fittings, grit, 18 s, the n44 valve sell flow with new copy). Library 50 to 53. formats.json angle `origin-story`, hook `origin`.
- Spanish cut (Nov 8, 20:05Z): `yardswaps-origin-story-16x9-voice-es.mp4`, same picture and music bed, nine Spanish lines (Justin Case, ElevenLabs eleven_v4 language es, neutral Latin American Spanish, informal tú; script with English beside it in `brand/ORIGIN-STORY-ES.md`). `narr/mixorigin.py` is LANG_CODE-aware (`LANG_CODE=es`, cues `narr/origin-cues.es.json`, writes `-voice-es.mp4` + `.es.srt`). Lines placed 0.6 to 108.2 s, last ends 117.9 s of 123.6; mix -14.1 LUFS, -3.5 dBTP. Audio mp3s came through `narration/origin-es/` (fetched on Alan's PC, cloud cannot reach the ElevenLabs file host). YouTube queue row 21 (Wed Nov 11 1:30 pm Central), SEO item ES-1. Self-checked by back-translation, no proofread hold; a flagged line is re-generated and the cut re-mixed.
- Photos: the generator-on-trailer demo image with the maker logo and plate blurred (`mo/sit/generator-trailer-*`); the well-pump and copper-fittings photos already in use. No AI images.

## Nov 9: fit the whole item, never zoom into it (Alan: "too zoomed in to show the complete item")

Cause: every Short opened on a 9x16 crop of a landscape photo (`sit/*-9x16.jpg`), shown full-bleed with `objectFit:'cover'` and then pushed to 1.17x (pan 1.14x). A 4:3 photo cropped to 9:16 keeps only 42% of its width, so the compressor, box truck, forklift, tractor, Hotsy, mixer, backhoe and trailer openers showed a slice of the machine. A contact sheet of all 53 `reels/library` cuts at 1.2 s: most openers clip the item (all the landscape photos).

Rule from Nov 9 (template `video-upgrade/source/v2/v2play.html`, `opener()`):
- The opener photo is FITTED: the whole uncropped photo sits in a 94% box with 18 pt rounded corners over a blurred copy of itself under a 55% light-gray wash. It flies into the phone slot from that box at the match cut.
- Movement stays inside the frame: push 1.0 to 1.04x, zoom 1.03x, pan 1.03x with plus or minus 0.8%. No more 1.17x push.
- Point `opener.img` / `imgw` at the ORIGINAL photo (`assets/real-listings/...`, Canva or Commons original), not a `sit/*-9x16.jpg` crop. A crop defeats the fit. The label loupe still takes its own `src` and coordinates.
- `"fit": false` in a spec brings back the old full-bleed cover look; only for a photo shot vertically with the whole item already in it.
- The result beat's faded "before" card uses `contain` on light gray instead of `cover`.
- `renderAt` lays a frame out again once a new image decodes (the fitted box needs the photo's real size).
- `mkpre.py` (origin pre-roll, ffmpeg zoompan) needs the same treatment: scale to fit with a padded or blurred background, zoompan at most 1.04x.
- Eye check before deploy: the 1.2 s frame of every new cut on a contact sheet must show the entire machine.

Before/after still: `video-upgrade/fit-opener-before-after.jpg` (old cover crop, fitted, fitted at the match cut, fitted 4:5). Re-rendering the library is the Motion thread's job (recordings live in its scratchpad); same file names, so the Reels/TikTok posters pick them up with no `library.json` change.

### Nov 9 (later): openers look organic, not templated
Alan saw the fitted stills: "looking better, need to make sure it looks organic and real." v2play.html opener at 9x16 now runs the photo edge to edge (full 1080 width) in the band y=412..1222, between the POV card and the blue question box, with no rounded card or drop shadow; the blurred copy of the photo behind it has a light .30 wash so it reads as the photo's own colors, like a landscape phone clip posted vertically. 4x5/1:1/16:9 keep a 94% box without the card shadow. Alan OK'd this style 15:20Z. Do not bring back framed photo cards in Shorts/Reels openers.

### Nov 9: the item in the opener is the item in the app (continuity rule)
Alan, 15:22Z: "make sure we are consistent: when we show in reels and videos what we take a picture of, that's what we show in the app walkthrough." In every Short, Reel and long video, the item photographed or shown in the opener must be the SAME item the app walkthrough then shows: the photo the phone snaps, the AI scan result (title, make/model, specs read off the tag), the listing card, the detail screen and the "listed" end state. No opener of a generator followed by an app recording of a forklift; no snap of a brass valve that lists as a skid steer.
How to apply: pick the opener photo FROM the listing the recording shows (same photo file), or record the walkthrough on a listing built from the opener photo. A feed/browse scroll may show other listings, but the hero card the viewer follows must be the opener item. Check before deploy: put the 1.2 s opener frame next to frames from the snap, scan, card and detail scenes; if the item differs, fix the spec or re-record, never ship it. Openers with no app item (pure feed/browse explainers) open on a photo of a listing that appears in that feed.
## Nov 9: Monday run, first of the 21-a-week cadence (category range rule), rendered with the fitted opener

- Trigger fired 13:42Z. Photo pass first: three stock photos cleaned for openers (`vacuum-truck-clean` with the door name blurred, `tank-hoses-clean` cropped so the crew is out of frame, `machine-shop-clean` with the shop labels blurred); the `mobile-crane`, `truck-lift` and `pickup-on-trailer` stock all show people or business names and were rejected, so Cranes & Rigging still has no opener. Pumps leftover-item Short skipped: the only pump photo is the stripped well pump already used twice.
- Alan, 13:54Z, while the first render ran: "Some of the equipment and or images are too zoomed in to show the complete item", then "Just the shorts and reels" and "the last couple of posts the equipment isn't even showing". The first render of these 7 (old full-bleed 9x16 crop opener) was stopped before deploy. The crop-fix thread patched `v2play.html` (fitted whole-item opener, see the "Nov 9: fit the whole item" section below); the 7 openers were repointed at whole-item originals (`mo/sit/fit-*.jpg`: canva-21/20/22/51/78 with blurs, the generator-trailer and tool-chest 16x9 frames) and the 1.2 s stills went to Alan for his OK (`/mnt/project-files/crop-fix/today-7/`). `objectaudit.py` now strips a `fit-` prefix and a `-clean` suffix when it looks the photo up. `batch.sh` writes `st/<n>-1.2s.jpg` per cut as the eye-check frame.
- Library fix the same day: 30 existing cuts (n23 to n51, o1 to o3) re-rendered at 9x16 from whole-item originals (`mo/sit/lib/*.jpg`; kiosk, flatbed and chop-saw cropped to drop a customer, a photographer's shadow and a gloved hand) and redeployed under the same file names via `batch916.sh` (guarded: a render that logs a missing resource is not deployed). At 15:11Z Alan asked for openers that "look organic and real": the crop-fix thread changed `v2play.html` so the 9x16 photo runs edge to edge (band y=412 to 1222) with no rounded card or drop shadow and a .30 wash, the 7 stills were re-sent, Alan answered "good, continue and complete" (15:20Z), and all 30 library cuts plus today's 7 were re-cut on that template. Sheets: `/mnt/project-files/crop-fix/today-7/` and `/mnt/project-files/crop-fix/library-30/` (1.2 s frames and pair sheets).
- Lost recordings: the Nov 1 cuts (n1 to n22) cannot be re-rendered because their app recordings (search, browse, listing, chat, offer, store, follow, demand, cold, craigslist, inv, sold, sell, part, trailer, fork, s_buy, s_deal, s_sell) are gone from scratch (the s_* folders are broken symlinks). 15 of them crop the machine at 1.2 s and are on `hold: true` until re-recorded; `forklift-finally-deal` is also held because its opener (yard forklift) is not the forklift the app lists (continuity rule, Alan 15:22Z). Active library 43 of 60 after today's 7, so the RAISE RULE ceiling is 4 a day until the re-cuts land.
- Continuity check (Alan 15:22Z, "what we take a picture of, that's what we show in the app walkthrough"): every opener photo was matched against the listing photos in `rec/img`. The forklift, backhoe, boom lift, tractor, flatbed, compactor, combi oven, laundromat and vacuum truck openers are the exact listing photos; every sell-flow cut from n23 on uploads the opener photo itself. `v2p/pairsheet.py` makes an opener-vs-app pair sheet per cut; it is now a gate in all three Motion routines.
- Seven sell-flow recordings (`recsell.js`, one per item, scan stubs filed under the item's own category) then n52 to n58 in the demo format, 17 s each, four sizes, silent twins, covers; objectaudit, cropaudit (only the known 4.75 s phone-edge false positive), audioaudit (-14.1 LUFS, -2.2 dBTP) and the overlap gate all passed. No heavy iron up front, per Alan's Nov 8 steer: generator (drive), vacuum truck (grit), vacuum tank and hoses (sunny), tool chest (punch), pallet racking (lift), scissor lifts (tech), manual lathe (phonk).
  - `job-wrapped-generator` (Generators & Power, leftover-item, first full Generators spotlight), `downsized-to-one-truck` (Vacuum Trucks, first), `sold-the-septic-route` (Environmental, first), `second-bay-closed-tools` (Power & Hand Tools, small-items angle), `warehouse-lease-ended` (Warehouse Storage), `interior-job-done-lifts` (Aerial Lifts, first sell-flow cut), `shop-went-cnc-lathe` (Metalworking & CNC).
- Deployed: reels/library + library.json (added 2026-11-09, priority 0 to 6 in the order above, so the generator posts first), metrics/formats.json (hook pov-idle, angle idle-gear, small-items for the tool chest), week-2026-11-09/ durable copies, assets/motion four sizes + silent + covers, review page. Library 53 to 60. Captions in MOTION-CAPTIONS.md. Amplify thread told (7 new clips).
- Coverage after this run: 29 of 33 categories with a sell-flow or spotlight Short. Still not yet: Cranes & Rigging (needs a people-free photo), Hydro Jetting, Pipe Inspection, Safety & PPE, Commercial Refrigeration (no photo). Pumps still owed a leftover-item Short (needs a second pump photo).
- Scratch: recordings recompressed to q82; finals deleted after deploy; `deploy_new.sh` now writes week-2026-11-09 (edit W for the next week).

### Nov 9 16:40Z: 15 held Shorts re-cut by splice
The 15 clips held for cropped openers (lost Nov 1 recordings) were fixed without re-recording: `v2p/splice.py NEW OLD OUT T` renders the spec with the edge-to-edge opener (phone blank), finds the first frame after T where new and old match outside the phone screen (~2.7 s), and concatenates new opener + old app footage/audio. Crop/audio audits pass, continuity pair sheet checked (`/mnt/project-files/crop-fix/held-15/`). Holds lifted in media 6a7710d: library 58 active of 60. Still held: forklift-finally-deal (opener forklift is not the listed one) and forklift-sitting-there (racks); both are forklift Shorts, paused by the Nov 8 measured rules.

### Nov 9 20:10Z: Motion scratchpad wiped (container reset); what survives
The session scratchpad (mo/scr recordings, v2p specs n34 to n58 and o1 to o3, sit/lib photos, rec/img listing photos, batch916.sh, deploy scripts, the review-page source) is gone. Nothing shipped is lost: every video is in assets/motion and in yardswaps-media (reels/library, week-*). Surviving sources: `video-upgrade/source/v2/v2play.html` (current edge-to-edge template, copied to `v2-port/v2play.html` too), `v2-port/renderspec.js`, `batch.sh`, `deploy.sh`, `finish.py`, `recsell.js`, `mkdemo.py`, `v2-port/spec` (n1 to n32), `v2-port/sit` (18 photos), `source/rec` (recorders), `tools/` (objectaudit, cropaudit, audioaudit, plus `pairsheet.py` and `splice.py` re-saved today). The three Motion routines now point the continuity gate at `tools/pairsheet.py` and say to rebuild the workspace from here and to save new specs, photos and scripts back into v2-port before a run ends. The review page's index.html is read back with the Artifact tool before any republish.

Also Nov 9: `library.json` entries carry `category` (a CATEGORIES id) when the clip is about one category; the Facebook Reel link then goes to yardswaps.com/sell-equipment/<id> (media PR 42). 43 of 60 clips tagged in 2a6c042; general and explainer clips stay untagged.


### Nov 11 11:35Z: ElevenLabs credits no longer a limit
Alan's account moved to the ElevenLabs startup Grant plan (until Nov 11, 2027; about 44M credits plus a separate image/video budget, confirmed live on the connector). Narration for every long video, Spanish lines, re-takes, music beds and SFX go ahead without rationing. Shorts stay voice-free. The 14 Spanish long videos still wait on the PC download route (fetch.ps1 with Alan's PC awake), not credits. Friday routine prompt updated.

## Nov 11 12:20Z: Spanish long videos ES-4 to ES-17 delivered (no PC needed)

The media repo now has an ElevenLabs job (`.github/workflows/narration.yml`, PR #49): push `narration/<set>/lines.tsv` (file, voice_id, model_id, language, text) and the bot commits the mp3s. The 54 Spanish takes signed on Nov 8 sat on a flow in the old ElevenLabs workspace, which the connector can no longer open ("You do not have access to this template"), so `narration/longform-es/lines.tsv` regenerated all 54 lines (same scripts, Justin Case, eleven_v4, es; run 43015001645, commit b26c13c). Mixed with `v2-port/narr/mixlong.py` (now LANG_CODE-aware: `-voice-es.mp4` output, music twin as the picture when the silent master is missing, end card = D - 3.2 s when the last chapter's spec is gone; n44 was lost with the scratchpad), no line over its window, loudness -14.2 LUFS on every file. SRTs via `srtlong.py`. Files: `assets/motion/yardswaps-<name>-16x9-voice-es.mp4` + `assets/captions/...-voice-es.es.srt` for the 14 names, durable copies in yardswaps-media `week-2026-11-11/` (Spanish-title slugs, commit 31a9e24). Queue rows 24-37, 1:30 pm Central daily Thu Nov 12 to Wed Nov 25.

Mistake caught and fixed in the same run: the first mix pass wrote through symlinks and overwrote ten English `-16x9-voice.mp4` masters (buyers-find-you, compressor, dealer-tools, fleet-and-yard, free-boosts, full-tour, parts-and-labels, parts-stuck-on-a-shelf, shop-tooling, weekly-3). They were regenerated from the English lines in yardswaps-media `narration/longform/` with the same recipe (same cues, -14.1 LUFS); the Spanish output that landed on those paths was renamed to `-voice-es`. Never symlink a workspace `final/` onto assets/motion; copy outputs in afterwards.

## Nov 11 ~15:40Z: Wednesday batch, 7 Shorts (n59 to n65)

Routine "YardSwaps weekly motion videos" (Wednesday). Two storefront Shorts first, then five categories the scorecard had empty. All seven: whole-item opener (1.2 s frames + pair sheet in `/mnt/project-files/crop-fix/2026-11-11/`, checked by eye: whole item, same item in the app), objectaudit, OVERLAP gate, cropaudit (only the known 2.5/2.75 s match-cut, 4.75 s phone-edge and 12.25 s end-card flags), audioaudit (-14.0 to -14.2 LUFS, peaks under -2.0 dBTP).

| key | slug | category | opener photo | music |
|---|---|---|---|---|
| n64 | whole-lot-one-link | trailers (dealer) | canva-18 enclosed trailer | drive |
| n65 | import-from-your-website | generators (dealer) | canva-13 towable generator | tech |
| n59 | trash-pump-after-the-job | pumps | canva-17 trash pump | punch |
| n60 | inspection-camera-in-the-van | inspection | canva-15 camera reel | sunny |
| n61 | second-jetter-by-the-fence | hydro | canva-12 jetter trailer | grit |
| n62 | cooler-still-humming | refrigeration | canva-60 beverage cooler | lift |
| n63 | chain-hoist-on-the-beam | cranes | canva-76 chain hoist | tech |

Deployed: `assets/motion/yardswaps-<slug>-{9x16,4x5,1x1,16x9,16x9-music}.mp4`, `silent/`, thumbnails; yardswaps-media `reels/library/` + `library.json` (67 videos) + `metrics/formats.json` (68) + `week-2026-11-11/` (commit 5903cc8). Captions in MOTION-CAPTIONS.md under "Nov 11, Wednesday batch". Backlog: the two storefront items marked done, a "Nov 11 (Wednesday batch)" section added. Review page republished (version 63) with 14 new previews.

Storefront decisions, so nobody re-litigates them: demo store is "Your Equipment Co." with `verified:false` and `dealerBadgePending:true` (the badge is only earned after the first payment, so the demo must not show it); the import button reads "Scan my website"; the share step shows a slate "Link copied" toast standing in for the native share sheet (navigator.share stubbed in recstore.js); n65's callout freezes rows 405-447 after the page scrolls post-scan. Claims used: Dealer plan, first 90 days free then $49 a month, no listing cap, one link for the whole lot. Nothing about search rank, views, sales or empty searches.

Workspace rebuild notes (scratchpad was lost): `rec/img/` rebuilt from canva-images + real-listings + app-first sit photos (recipe in `assets/motion/source/recording/README-img.md`); new `mockst.js` (WHICH=store|import wraps mock.js), `recstore.js`, `recimport.js`, `runall.sh`, `scan/*.json` SCANF stubs saved under `assets/motion/source/recording/`; `mkdemo2.py`, `mkstore.py`, `batch.sh`, `chk.js`, `reqlog.js`, `gen-nov11.py`, `spec-nov11/n59..n65.json`, `sit/<name>-{9x16,16x9}.jpg` saved under `video-upgrade/source/v2-port/`; objectaudit tables extended (trash pump, camera, jetter, cooler, hoist; the recording was renamed `trashpump` because `pump` maps to well pump). Expo web app needs `react-dom@19.2.0` + `react-native-web@~0.21.0` installed `--no-save` (install with nohup, not a backgrounded subshell).

Friday owes: storefront-stats, socials-on-storefront, see-what-buyers-want-v2 (re-cut). Safety & PPE still has no usable opener photo (canva-65/66 gear racks are candidates).

## Nov 13 ~16:05Z: Friday batch, 7 Shorts (n66 to n72), how-to #3, weekly-5

Routine "YardSwaps Friday seller videos". The two storefront cuts the Wednesday run owed, the buyer-demand re-cut, and four categories the scorecard had empty or thin. All seven: whole-item opener (1.2 s frames + pair sheet in `/mnt/project-files/crop-fix/2026-11-13/`, checked by eye: same item in the opener and in the app), objectaudit, cropaudit (only the known 4.75 s fly-in and 12.25 s to 14 s end-card flags; the lift 1:1 flags at 3.0 to 4.0 s are the white shop wall around the lift, the phone is whole), audioaudit -14 LUFS, OVERLAP gate, caption lines 17 characters or fewer (five cuts were re-rendered for it).

| key | slug | category | opener photo | music | recording |
|---|---|---|---|---|---|
| n66 | storefront-stats | welding (dealer) | canva-90 MIG welder on cart | sunny | `stats` (analytics 30/90/180, top listings, CSV) |
| n67 | socials-on-storefront | cooking (dealer) | canva-53 combi oven | lift | `socials` (header, social links, Follow, oven first) |
| n68 | see-what-buyers-want-v2 | aerial (dealer) | canva-77 yellow boom lift | drive | `demand` (Buyer demand report, Dealer boost 7 days) |
| n69 | lift-still-bolted-down | automotive | canva-01 two-post lift | grit | `lift` |
| n70 | box-truck-after-the-route | fleet | canva-11 box truck | punch | `boxtruck` |
| n71 | roller-after-the-overlay | paving | canva-81 asphalt roller | tech | `roller` |
| n72 | safety-gear-on-the-wall | safety | canva-66 hard hats and vests | sunny | `safety` |

n68 rules kept: no frame of the "Searches that found nothing" section (the mock returns `zeroResultSearches: []`), no "Few listed" row (`needsSupply:false` on every category; the first take had three and was re-recorded), no forklift row (Pumps took its place), end card "Dealer boosts start with the first payment". Two recording slips fixed before render: the box-truck scan stub said category `trucks` (the app id is `fleet`, so the publish was blocked by the empty Category field) and `demand` was first launched without `MOCK=./mockst`. mock.js now prices the published row from the scan's suggested range instead of a flat $500.

Long videos: `yardswaps-how-to-free-boosts-16x9-voice.mp4` (how-to #3, 2:06, 5 steps: How it works sheet, Starter boost publish, My Listings with every unit boosted, a boost credit at publish, Invite a seller; recordings `w3_card`, `w3_starter`, `w3_credit`, `w3_invite`; spec builder `mkhowto3.py`) and `yardswaps-weekly-5-16x9-voice.mp4` (1:24, the seven seller Shorts of Nov 9 to 13). Narration: the ElevenLabs connector was down (502) all session, so both sets went through the media repo's narration job (`narration/howto-boosts/lines.tsv`, `narration/longform/lines.tsv`; run 14, 1 minute, commit 210250c) and were mixed with `narr/mixhowto.py` (new, fixed line times) and `narr/mixlong.py`. English SRTs in `assets/captions/`. Music-only and silent twins in `assets/motion`.

Deployed: `assets/motion/yardswaps-<slug>-{9x16,4x5,1x1,16x9,16x9-music}.mp4`, `silent/`, thumbnails; yardswaps-media `reels/library/` + `library.json` (74 videos, the old see-what-buyers-want stays on hold with a note) + `metrics/formats.json` (75) + `week-2026-11-13/` (commit cd40147). Captions in MOTION-CAPTIONS.md (Nov 13 sections), queue rows 38 and 39, SEO items 21 and 22, WEEKLY-BATCH.md note. Sources: `video-upgrade/source/v2-port/` (mkstore, mkdemo2, mkhowto3, gen-nov13, spec-nov13/, sit/, narr/) and `assets/motion/source/recording/` (mockst.js, recstats/recsocials/recdemand/rechow3, runfri.sh, scan/).

Still open: the Spanish cut of how-to #3 and weekly-5 (the Spanish lines are not written; the longform-es set has the earlier clips only). Safety & PPE now has one Short; the scorecard's Nov 12 category list is covered.

## Nov 13 ~16:20Z: two fixes after the other threads' checks

- lift-still-bolted-down: the opener photo (sit/two-post-lift) had white padding baked into its left and right sides, which rendered as two white slabs beside a narrow photo (crop-fix thread). Source trimmed (`convert -fuzz 4% -trim +repage`, 607x1080, the lift stays whole), re-rendered all sizes, redeployed under the same name. New gate: `video-upgrade/tools/bordercheck.py` runs in batch.sh before every render and fails a spec whose opener or before photo has a flat white or black band on any side.
- see-what-buyers-want-v2: the recorded Buyer demand report said "Within about 50 miles of Katy, TX" while the real report covers 150 miles (storefront thread, DEMAND_REGION_MILES). mockst.js now returns 150 miles with no place name ("Within about 150 miles of your storefront"), the demand clip was re-recorded (725 frames, taps 512/637), mkstore.py n68 retimed, re-rendered and redeployed under the same name. Captions for the three storefront Shorts say "near you" and "first 90 days free for new dealers" (media PR #53, MOTION-CAPTIONS.md, review page).

## Nov 15 ~18:30Z: find-it-nearby and every-category re-cut without the category count

Alan's rule (Nov 15, category-count cleanup thread): never state how many categories YardSwaps has. The two library Reels that showed "33 categories" on screen were re-cut: find-it-nearby caption 2 is now "Commercial and / industrial gear." (the thread's "Commercial and industrial gear. / All local." wrapped to three lines, so it was split across the two caption lines; "Find it nearby." already carries the local point), every-category closes on "And more. / Free to list." after the six category chips. The browse, listing and cats frame folders no longer existed, so the clips were re-recorded with recall.js / recall2.js on the local app and the v2 specs (`video-upgrade/source/v2-port/spec/n2.json`, `n6.json`) retimed onto the new recordings using the tap frames as anchors (browse 549, listing 288, cats 421 frames). Rendered through batch.sh (all gates, whole-item fitted opener), redeployed under the same names to assets/motion and the Reels library, hold lifted in reels/library.json. Review-page captions and long-video chapter titles lost the number too. The 13 long videos in week-2026-11-08/09/11 that narrate "33 categories" stay as posted; no new upload reuses those cuts or the old narration lines (the longform narration scripts were updated by that thread).

## Nov 15 ~23:00Z: walkthrough screen-vs-words audit (Alan: "some of the iPhone walkthroughs still show incorrect views on what it's saying")

Checked all 71 live Reels (one contact sheet each: caption start/mid/end, pills, result; `tools/wordsheet.py`) and the 18 long videos (one frame per subtitle cue; `tools/longsheet.py`). Finding: 27 Shorts put the "price" callout on the wrong rows of the sell form. In the mkdemo2 batch (n59 to n63, n69 to n72) the frozen crop sat at y 456, which is "Answer offers automatically / Condition" in the Nov 11/13 recordings; the price field and Use price button are at y 250 to 380 (checked on frame tUP+24 of all nine recordings, `audit/pricerow-check.jpg`). In the older live-callout family (n15, n17, n19, n22 to n31, n36 to n39, n53) the crop landed on the boost rows ("7 Days $14.99 / No boost: publish for free"). Everything else matched. Full list with the minor items (a blank phone for half a second in three videos, a clipped header in four description callouts): `motion/audit/WALKTHROUGH-MISMATCHES-2026-11-15.md`.

Rule from this: a callout's `y` is checked against the recording's frame at the callout's `f` before render, never carried over from an earlier template; the price row moved when the suggested-price card was added to the form.

Done: the 27 put on hold in `reels/library.json` (commit c1eb8e3, 44 live) while they re-render; mkdemo2 price callout moved to y 250 and the nine re-rendered; the 18 lost recordings re-shot with recsell.js on the local app (scan stubs in `recording/scan/`, opener photos for the parts batch recovered from the old renders) and rebuilt on the mkdemo2 timeline via `mkdemo3.py` (same 5-caption shape; n17 no longer claims an "add a video" step the screen never showed). Long videos that embed the wrong segments (all-listings-marathon, parts-and-labels, shop-tooling, fleet-and-yard, parts-stuck-on-a-shelf, compressor-start-to-finish, weekly-3/4/5) and the seven that narrate "33 categories" were handed to the YouTube thread; nothing posted was replaced.

## Nov 15 ~23:50Z: new music beds (Alan: "Pick better music using elevenlabs")

Six new instrumental beds generated with ElevenLabs Music (eleven_music_v2_5, flow "YardSwaps music beds v2 (Nov 15)",
4 takes per style, one picked per style by loudness range and a clean start): clean-120, folk-118, shop-110, funk-112,
lofi-90, road-124, as `assets/elevenlabs/music/yardswaps-music-<style>-<bpm>bpm.mp3` (source copy in yardswaps-media
`music/v2/`, all 21 takes in `narration/music-v2/`). finish.py's MUSIC map carries both the old six and the new six;
batch.sh's ST map now rotates the new six across every Short. Applied Nov 15 to all 36 Motion Shorts in rotation: the 9
fixed demos by re-finish, the other 27 from their silent copies (`refinish2.sh`, SFX timings from the saved spec, or for
parts-donor-thumb / parts-bin-lot / drilling-rig-parked recovered by matched filter, `tools/sfxrecover.py`, verified
exact on part-tag-scan). Licence: ElevenLabs Music terms (elevenlabs.io/music-terms) allow all online commercial use on
paid tiers except film/TV/radio/games; Creator and Pro are "individual use only", company use needs Scale or better.
The grant account's tier is Alan's to confirm; the earlier six beds came from the same account.

Rule added to mkdemo3.py: the fill frame is detected in the recording (first frame whose top half changes after the
upload, then the first frame where the auto-scroll has settled), never assumed at F0+235. Scan speed varied 7 to 13 s
between recordings and the assumed offset is what put the photo row under the "AI fills it. Title. Category." callout.

## Nov 16 ~01:15Z: the 12 narrated long videos rebuilt on the fixed cuts

Asked by the YouTube thread (00:34Z) after the Nov 15 Shorts re-cuts: every long that embedded an old cut was re-rendered on the SAME filenames (`assets/motion/yardswaps-<name>-16x9{,-music,-voice,-voice-es}.mp4`, `assets/captions/yardswaps-<name>-16x9-voice.en.srt` + `-voice-es.es.srt`, `thumbnails/yardswaps-<name>-cover-youtube-16x9.jpg`). Recipe in the Motion scratchpad `v2p/`: `compile12.sh` (compile.py per name, new beds: shop-tooling funk, fleet-and-yard shop, parts-stuck-on-a-shelf lofi, parts-and-labels shop, weekly-3 folk, weekly-4 funk, how-it-works-v2 clean, all-listings-marathon road, dealer-tools clean, full-tour road, buyers-find-you clean, free-boosts folk) then `finishlong.sh <name>` (chapters.json refresh, mixlong EN + `LANG_CODE=es` mixlong ES, srtlong, audioaudit, copy). Chapter times per video are in the YouTube thread messages and `out/<name>/chapters.json`.

New narration lines (EN `narration/longform/lines.tsv`, ES `narration/longform-es/lines.tsv` in yardswaps-media; the Action never remakes an existing file, so new takes get `-v2.mp3` names and are copied over the old key in `narr/mp3-*`): clip find-it-nearby, clip every-category, intro buyers-find-you, intro free-boosts ("Free boosts on YardSwaps: here's how to earn them", no "every boost is free"), clip see-what-buyers-want-v2 (Buyer demand report; no "searches that found nothing"), intro all-listings-marathon ("Twenty-nine listings..."). `scripts.json` / `scripts.es.json` updated in `assets/elevenlabs/voiceover/{en,es}/longform/`.

Caught mid-run: the first compile pulled two HELD cuts, forklift-sitting-there (racks opener, held Nov 1) into the marathon and the old see-what-buyers-want ("Searches that found nothing" card, against the Nov 10 rule) into buyers-find-you, full-tour, dealer-tools and the marathon. Those four were re-compiled (`compile4.sh`) with see-what-buyers-want-v2 and without the forklift clip; the marathon is now 29 clips, 5:37. RULE: before compiling a long, check every id against `reels/library.json` holds (and the old clip's narration line), not only against the Shorts just fixed. Marathon files are re-encoded at 1.8 Mbps (`small/`) so each stays under GitHub's 100 MB (voice 81 MB).

Minor: mixlong prints `OVER` for the ES boring-bars-tooling and plumbing-part-label lines (0.02 to 0.1 s past the 0.2 s margin; the speech itself ends before the next cue, measured with silencedetect), left as is.

## Nov 16 ~14:20Z: Monday batch, seven idle-gear Shorts (n74 to n80)
Trigger "YardSwaps Monday motion videos". Full recipe: photo pass on the Canva stock sheets (free licence, no faces, no business names, fitted whole, no crop), one recsell.js sell-flow recording per item with a scan stub, mkdemo4.py + cfg-nov16.json specs, batch.sh (four sizes, silent twins, covers, objectaudit, bordercheck, OVERLAP, cropaudit, audioaudit), whole-item and continuity sheets, deploy.sh, publish-nov16.py. Media commit 49df853; library 74 to 81; formats.json 82 rows.

| key | slug | category | photo | music | recording |
|---|---|---|---|---|---|
| n74 | welder-from-one-job | welding | stick-welder (canva-27) | funk | stickwelder |
| n75 | compressor-by-the-fence | compressors | towable-compressor (canva-16) | lofi | towable |
| n76 | rooftop-unit-on-the-pallet | hvac | rooftop-unit (canva-06) | road | rtu |
| n77 | sprayer-after-the-season | agriculture | sprayer-rig (canva-41) | clean | sprayer |
| n78 | light-tower-after-night-work | generators | light-tower (canva-05) | folk | lighttower |
| n79 | fryers-from-the-closed-kitchen | cooking | fryer-line (canva-62) | shop | fryers |
| n80 | zero-turn-after-the-account | landscaping | zero-turn-mower (canva-89) | funk | zeroturn |

Gates: objectaudit ok x7, bordercheck ok x14, no OVERLAP, audio -14.2 LUFS / -2.3 dBTP on all 28 files, cropaudit clean on every 9x16; the 4x5, 1x1 and 16x9 cuts of n77 to n80 carry the known one-frame "phone-top/bottom-cropped" flag at 4.75 s (the phone slide-in at T=4.3, same as the Nov 15 batches, not a hold). Whole-item 1.2 s frames and the continuity pair sheet are in /mnt/project-files/crop-fix/2026-11-16/ (whole-item-1.2s.jpg, pairs-nov16.jpg, the seven PNG frames, st contact sheets): every opener shows the whole item and the app thumbnail is the same photo in all seven.
Review page: seven entries at the top of the list plus 14 previews (version 68). The page script had a duplicated `"16x9-voice":"youtube-16x9"` key in the CT map that made the whole script fail to parse (left by an earlier sed); fixed in this publish, so check that the buttons work when the page is next opened.
Disk: rec/raw is recompressed to JPEG quality 82 for every clip outside this batch (recompress-old.sh); the Nov 11 long renders in scratch en/final and es/final were deleted (the Nov 16 rebuilds in assets/motion supersede them). deploy.sh overwrites page/v previews with the full-size file when one already exists, so encode previews after deploy, not before.
Sources saved: video-upgrade/source/v2-port/{spec/n74..n80.json, cfg-nov16.json, mkdemo4.py, gen-nov16.py, publish-nov16.py, batch.sh, scan/*.json, sit/*.jpg, runmon.sh, recsell.js}.

## Nov 16 ~15:55Z: 10-second cuts (Nov 16 YouTube weekly report, applied on Alan's "implement the recommendations")
The report: our 17 s Shorts averaged 30 views, HeyCatch's 4-10 s clips 942. New cut, `mkdemo5.py` (reads `cfg-all.json`, every batch's config merged; spec id `<n>s`): opener 2.4 s with the question box in the first second, library tap at T+0.2, photo lands at 3x and the scan fills at 16x, scroll at 12x, Use price after 0.5 s, publish after 0.4 s, FOUR captions (the condition caption dropped), result beat 0.6 s, brand card 2.3 s so the question pill lands. D = 9.9 to 10.1 s. Rendered with batch.sh (ids `<slug>-10s`) through the same gates: objectaudit, bordercheck, no OVERLAP, audio ok on all 60 files; cropaudit flags one frame at 7.75 s on two 9x16s, the first frame of the brand-card circle wipe, not a hold.
Shipped 15 (media commit eb0623d): today's seven (welder-from-one-job, compressor-by-the-fence, rooftop-unit-on-the-pallet, sprayer-after-the-season, light-tower-after-night-work, fryers-from-the-closed-kitchen, zero-turn-after-the-account) plus eight demand-category cuts (trash-pump-after-the-job, stripped-well-pump, inspection-camera-in-the-van, chain-hoist-on-the-beam, lift-still-bolted-down, roller-after-the-overlay, downsized-to-one-truck, second-jetter-by-the-fence). Files: assets/motion/yardswaps-<slug>-10s-{9x16,4x5,1x1,16x9,16x9-music}.mp4 with silent twins and covers; week-2026-11-16/ carries the -10s 9x16 and 16x9-music. `publish10.py` copies the 10 s 9x16 OVER reels/library/yardswaps-<slug>-9x16.mp4 (same name, so every posting engine switched without a config change) and marks the library entry `cut: 10s, seconds, cut_added`; the 17 s cuts stay in assets/motion under their old names. Not re-cut: Nov 9 and earlier Shorts whose raw recordings are gone (job-wrapped-generator among them), and the storefront Shorts. New Shorts from the Wednesday run use mkdemo5 by default; generators first.
Review page version 69 carries the 15 under "(10 s cut, Nov 16)". The page hit the 256 MiB cap: previews of the held forklift, origin-story, 33-category how-tos, seller-course, weekly-1/2, idle-gear and the old see-what-buyers-want were removed (their entries stay, with no preview).
Also fixed: tools/objectaudit.py had the Nov 16 PHOTO additions spliced into the middle of a line, which commented out the two-post-lift, box-truck, road-roller, safety-gear and boom-lift entries (caught when n69s failed the audit); the queued batch waiter matched its own command line in pgrep and never started, so run batches directly.

## Nov 16 ~20:00Z: new listings into the Shorts mix (Alan: "we usually get new users with new stuff daily so we can add them to promotion mix")
Wired, not yet exercised. Media commit f84abdc: `listings/just_listed.py` saves each queued listing's cleaned photo to `listings/photos/<id>.jpg` (faces skipped, digit words blurred, long edge 1600) plus price, condition, year, place and created in `queue.json`; `reels/post_reels.py` skips a Reel whose `listing_id` posted as a Just-listed card today; new `listings/motion-used.json` records listings already cut. New `video-upgrade/source/v2-port/pickreal.py` picks up to 2 approved or posted listings (one per seller, no forklifts, not in motion-used) and writes `cfg-real.json`, the sit/ opener copies, the rec/ photo and a scan stub, and prints the batch.sh and objectaudit lines; merge cfg-real.json into cfg-all.json before `mkdemo5.py r<id6>s`. The Monday, Wednesday and Friday scheduled runs now open with that step and make up to 2 of the 7 Shorts from real listings (listing photo as opener and as the recording upload; copy uses the item and category only). First queue entries with a photo arrive with the Nov 17 15:10Z prep, so the Nov 18 run is the first that can cut one.
Nov 16 ~21:10Z addendum (paid-seller thread): the listings workflow's `git add` in f84abdc left out `listings/photos/`, so no photo would have reached main; media PR #66 (paid-seller thread) adds it and sorts paying Pro/Dealer listings first (rank 1), trial storefronts second. pickreal.py now skips `opted_out` entries and sorts `feature: paid` first, newest after. Nov 18 run: confirm PR #66 is merged before step 0; if not, photos are absent and the run falls back to the backlog.

## Nov 16 ~22:55Z: words-vs-screen sheets for the 15 10-second cuts (Guard 2c caught the gap)
The 10 s re-cuts and the Monday batch went into rotation without the Nov 15 words-vs-screen sheet. Made now: `motion/audit/<slug>-10s.jpg` for all 15 (tool `video-upgrade/tools/wordsheet10.py`, reads the rotation file in reels/library), eye-checked, all pass; summary in `motion/audit/WORDS-VS-SCREEN-2026-11-16.md`. Nothing held. RULE: every new render, including a re-cut that overwrites a library file, gets its wordsheet in motion/audit/ before it goes into reels/library.json (added to the Mon/Wed/Fri run prompts).

## Nov 16 ~23:55Z: slower phone walkthrough (Alan: "Slow down the phone action walk through, right now they're super fast in the shorts")
The Nov 16 afternoon 10 s cuts ran the app part in about 3.9 s (AI fill at 16x, scroll 12x, taps 2x, live listing 7x). Alan found it too fast to follow. `mkdemo5.py` now has one knob, `PACE=dict(land=2,fill=8,scroll=6,tap=1.5,live=4)`: half the afternoon speed in every app scene. The app part runs about 6 s, each caption holds 1.2 to 2.2 s, the whole Short is about 12.1 s (opener 2.4 s unchanged, result 0.6 s, brand card 2.3 s). The fast values are kept in `mkdemo5-fast-nov16.py` for reference only. All 15 cuts in rotation (welder, compressor, rooftop unit, sprayer, light tower, fryers, zero-turn, trash pump, well pump, inspection camera, chain hoist, lift, roller, one truck, second jetter) were re-rendered from the same recordings and swapped into reels/library, assets/motion and week-2026-11-16 with fresh words-vs-screen sheets.
PACING RULE (Alan, Nov 16): in the app walkthrough a viewer must be able to follow every tap and screen change. No recorded segment plays faster than 8x (the AI fill), scroll at most 6x, every tap at 1.5x or slower with the finger visible before and after, and the live listing holds at 4x or slower. If a cut has to be shorter, show fewer steps, never speed the steps up. The opener (2.4 s) and the brand card are not where time comes from. Applies to every Short, Reel and real-listing cut (pickreal.py specs use the same mkdemo5.py).
Nov 17 00:35Z: the 15 slowed re-cuts are in reels/library, assets/motion (-10s files) and week-2026-11-16; words-vs-screen sheets regenerated and all pass (motion/audit/WORDS-VS-SCREEN-2026-11-16.md, Nov 17 section). Durations 12.0 to 12.4 s. library.json seconds updated by publish10.py.

## Nov 18 ~14:55Z: founding $29 hold lifted
Storefront thread: a live test previewed a $29 first invoice and FOUNDINGDEALER was redeemed once, so the founding price may appear in motion videos (media PR #75 released storefront-founding-29). Exact wording for any founding-price cut: "30 days free, then $29 a month for your first 3 paid months, then $49, for the first 100 storefronts, before Dec 1." Plain storefront cuts keep "First 30 days free, then $49 a month." Words-vs-screen sheet still required. Pull every founding cut from rotation on Dec 1. Run prompts rule H updated.

## Nov 18 ~15:00Z to 20:30Z: Wednesday batch, seven seller Shorts at 12 s (n81s to n87s)
Trigger "YardSwaps weekly motion videos". Step 0 (pickreal.py): no eligible real listing in listings/queue.json (none approved or posted with a saved photo), recorded, so all seven came from the backlog. mkdemo5.py with the slow PACE (land 2, fill 8, scroll 6, tap 1.5, live 4), one recsell.js recording per item with a scan stub, batch18.sh (same gates as batch.sh, two sizes at a time), whole-item and pair sheets, words-vs-screen sheets, deploy.sh, publish-nov18.py. Media commit 452e8f4 on main; library 85 to 92; formats.json 91 rows; week-2026-11-18/ holds the 9x16 and 16x9-music. YouTube-thread asks honoured: a Spanish soldadora cut and a data-plate specs cut, generators first.

| key | slug | category | photo | music | recording | angle |
|---|---|---|---|---|---|---|
| n81s | generator-for-the-storm-season | generators | generator-trailer (canva-13) | road | gen | idle gear |
| n82s | soldadora-en-el-carrito (ES) | welding | welder-cart (canva-90) | funk | migcart | idle gear, Spanish captions and end card |
| n83s | read-the-plate-welder | welding | engine-welder (canva-47) | tech | engwelder | data plate: "Forgot the amps? Snap the plate." the app fills amps, volts, process |
| n84s | skid-steer-after-the-grading | excavators | skid-steer (canva-03) | clean | skid | idle gear (the one heavy-iron cut, not first) |
| n85s | dump-trailer-after-the-cleanouts | trailers | dump-trailer (canva-10) | lofi | dumptrailer | idle gear |
| n86s | cord-reels-after-the-events | electrical | cord-reels (canva-68) | shop | reels | small items, lot of 6 |
| n87s | wrench-wall-from-the-sold-shop | tools | wrench-wall (canva-86) | folk | wrenches | small items, lot |

Photos rejected on the pass: canva-75 crane (worker and a company name), canva-61 freezer (branded products), canva-45 (person), canva-85 compactor (used Nov 8). No clean crane, pump, inspection or automotive stock photo is left in the pool, so those demand categories wait for real listings.
Gates: objectaudit ok x7 (tables gained the five new photos and six recordings), bordercheck ok, no OVERLAP, audioaudit ok on all 28 files, cropaudit clean on every 9x16; the 4x5, 1x1 and 16x9 cuts carry the known phone slide-in flag at 2.75 s and the brand-card frame at 10.0 s, not holds. Sheets: /mnt/project-files/crop-fix/2026-11-18/whole-item-1.2s.jpg and pairs.jpg, also in the media repo at week-2026-11-18/sheets/ (commit 33aab01; every opener whole, app thumbnail is the same photo). The project folder hit its 10 GB cap during this run; Alan chose (card, 15:49Z) to delete the 75 superseded 17 s files of the 15 Shorts re-cut on Nov 16 from assets/motion (577 MB; the media repo history keeps them), done 15:50Z; words-vs-screen motion/audit/<slug>-10s.jpg x7, all pass after one re-cut (below). Durations 12.1 to 12.3 s.
Fixes this run: (1) the scan stubs first used display names ("Output": "20 kW") so the app's spec fields stayed empty; stubs must use the field keys from packages/shared/src/equipment-specs.ts (generators kw/kva/voltage/phase/fuelType/portable, welding amps/voltage/weldType/dutyCycle/engineDriven, trailers trailerType/deckLength/axles/gvwr/hitch/brakes, excavators machineType/operatingWeight/hp/digDepth, electrical voltage/amps/equipType, tools toolType/powerSource/voltage/included; top-level `hours` fills Hours). All seven were re-recorded. (2) Four parallel Chromium renders crashed the GPU process ("Target crashed"); renderspec.js now launches with --disable-gpu --disable-dev-shm-usage and batch18.sh renders two sizes at a time. (3) wordsheet10.py takes WS_SRC to read scratch finals before publish. (4) n83s first said "AI reads it. Amps. Engine." while the screen showed the title row; re-cut to "Plate read. / 300 A, filled in." with Title/Category pills, sheet re-checked.
Spanish cut (n82s): l1 "POV: la soldadora MIG en el carrito." l2 "Nadie la enciende desde marzo."; captions "¿Parada? / Una foto.", "La IA lo llena. / Título. Tipo.", "Escrito por IA. / Estado, amperios.", "Un toque. / Precio puesto.", "Publicada. / Sin costo."; end card "Una foto de la soldadora. Lista." / "Publicar es gratis. Sin comisión." / "¿Qué soldadora tienes parada en el taller?". Library entry lang "es" with fixed IG tags. Only "YardSwaps" and "yardswaps.com" are fixed strings in mkdemo5, so any language works from cfg.
Review page version 71: seven entries at the top plus 14 previews (page/v 157M + c 18M, under the cap).
Sources saved: video-upgrade/source/v2-port/{spec-nov18/n81s..n87s.json, cfg-nov18.json, cfg-all.json, gen-nov18.py, publish-nov18.py, page18.py, mkdemo5.py, batch18.sh, renderspec.js, scan-nov18/*.json}, video-upgrade/tools/{objectaudit,wordsheet10}.py, assets/motion/source/recording/{runnov18.sh, recsell.js, mock.js, scan/}.
Nov 18 ~15:55Z addendum (crop-fix review): the cord-reels opener photo cuts the row off at both edges, so the hook "Six cord reels sit in the shop." claimed more than the frame showed (four whole reels). Re-cut n86s with "The cord reels sit in the shop." (cfg-nov18/cfg-all, same recording, gates and words-vs-screen sheet redone), swapped into assets/motion, reels/library and week-2026-11-18 (media commit below), captions updated in MOTION-CAPTIONS.md and the backlog. Rule reminder: a count in a hook line must be countable in the opener frame.

## Nov 27 ~14:37Z (made Nov 28 ~10:00Z to 10:30Z): Friday batch, two real-listing Shorts at 12 s (r3tp04qs, r5fbt0ss)
Trigger "YardSwaps Friday seller videos" fired Nov 27 14:37Z; the session hit its usage limit at once and the run happened Nov 28 from 10:00Z. First run under the REAL ITEMS ONLY rule (Alan, Nov 26): `pickreal.py 7` found only two eligible listings (approved or posted, photo on disk, not used, one per seller, no forklifts), so the batch is two Shorts and nothing was filled from stock: the 2024 Billy Goat DL3700VE leaf vacuum (cmwv95og80026t83akg3tp04q, Landscaping & Turf) leads, the zero-tail-swing Deere 50G excavator (cmvsip9ad002jmp3arr5fbt0s, Excavators & Loaders) second, so no heavy iron leads and the count is one. Listing photo is the opener and the upload, copy names item and category only (pickreal's four-word title cut gave "Zero-tail-swing Deere 50G with." and was replaced by "Deere 50G excavator."), library entries carry listing_id, real true and picture real, both ids in listings/motion-used.json in the same commit. Same recipe as Nov 25 (mkdemo5 slow pace, recsell.js with scan stubs, batch18.sh, objectaudit, bordercheck, OVERLAP, cropaudit, audioaudit, whole-item 1.2 s and pair sheets, words-vs-screen sheets checked before publish, publish-nov27.py reads the scratch finals, deploy.sh, endcard.py fix marks seller-v1). Fix this run: mkdemo5.py derived the recording key with rstrip('s'), which ate the trailing s of r5fbt0s; now n[:-1]. Gates: cropaudit clean, audio -14.1 and -14.2 LUFS, durations 12.1 and 12.07 s, both openers show the whole item, pair sheets match, word sheets pass caption by caption. Library entries plus two (library.json now 281 entries with the listing Reels and Studio clips other threads add). week-2026-11-27/ holds the 9x16 and 16x9-music plus sheets/ and source/. Project folder: assets/motion copies (10 files plus 6 silent and 6 thumbnails) verified by duration, crop-fix/2026-11-27/ sheets verified by listing. Long video (how-to 3, free boosts) and the weekly compilation: see the lines below this entry.

| key | slug | category | photo | music | recording |
|---|---|---|---|---|---|
| r3tp04qs | listed-billy-goat-leaf-vacuum (REAL) | landscaping | real-3tp04q (listing photo) | road | r3tp04q |
| r5fbt0ss | listed-deere-50g-excavator (REAL) | excavators | real-5fbt0s (listing photo) | clean | r5fbt0s |

Crop-fix review: two of two keep the whole item in the 1.2 s frame (the excavator sits on a dealer lot with other machines behind it, all whole). Heavy iron: one (the excavator), in second place.

Weekly 7 (made Nov 28 ~10:20Z): `compile.py weekly-7 sunny` over the week's six real-listing 16:9 silent cuts (Billy Goat leaf vacuum, Instapak SpeedyPacker, floral walk-in display cooler, used pallet racking, Caterpillar 140H V-plow, Deere 50G excavator; compile.py NUM now maps the `-10s` ids to their r-specs), 0:50, chapters 0:00 / 0:09 / 0:17 / 0:24 / 0:32 / 0:39, audio -14.1 LUFS / -1.1 dBTP, ends on the blue end card (endcard.py check: blue 2.0 s). Music cut and silent master in assets/motion, cover in thumbnails/, media week-2026-11-27/ plus youtube/long-queue.json row weekly-7 (kit slot Sat Dec 5; Sat Nov 28 is weekly-5), queue row 40, SEO item 23. Narration is on hold: the PC route was not available this run, so the music cut queues and `-16x9-voice.mp4` replaces it when Justin Case lines exist (write the six clip lines in assets/elevenlabs/voiceover/en/longform/scripts.json first). Long video how-to 3 is NOT remade this week: the narrated how-to-free-boosts (2:06, Nov 13) already sits in the long queue for Fri Nov 27 and YouTube is on hold until the Nov 30 batch, so a second cut would only duplicate it; next long video waits for the Nov 30 run. Note: the Nov 20 queue rows 40 and 41 and SEO items 23 and 24 named in the Nov 20 entry are not in the project-folder files (they stop at row 39 / item 22), only in youtube/long-queue.json; weekly-7 takes row 40 and item 23 here.

## Nov 25 ~14:52Z to 15:50Z: Wednesday batch, seven seller Shorts at 12 s (riq3khms, rsfmh3ls, n100s to n104s)
Trigger "YardSwaps weekly motion videos". Step 0 pickreal.py picked two real listings: the floral walk-in display cooler (cmwsc8u1f001rqk3af9iq3khm, Commercial Refrigeration) and the Caterpillar 140H V-plow (cmwosmtfl003bob3aetsfmh3l, Landscaping & Turf); listing photo is the opener and the upload, copy names item and category only, library entries carry listing_id and real true, both ids in listings/motion-used.json in the same commit. Photo pass: canva-69 (electrical cabinet), canva-72 (drill rig) and canva-20 (vac tank truck) joined the pool copies combi-oven and boom-lift-yellow; still no clean stock for generators, pumps, inspection cameras, automotive, cranes or paving, so those wait for real listings. Same recipe as Nov 23 (mkdemo5 slow pace, recsell.js with scan stubs, batch18.sh, objectaudit, bordercheck, OVERLAP, cropaudit, audioaudit, whole-item 1.2 s and pair sheets, words-vs-screen sheets checked before publish, publish-nov25.py reads the scratch finals, deploy.sh). Fixes this run: the vac truck opener (canva-20) carried a readable business logo on the tank, caught at the eye-check after the first render; covered it with a feathered patch of the tank's own texture (convert, no AI fill), re-recorded vactank and re-rendered n104s, sheets redone. cropaudit flagged "phone-bottom-cropped" at 10.0 s on boomlift 1x1 and on ecabinet and vactank (all sizes) in the first pass; frames 9.8/10.0/10.3 show it is the fade into the brand card, not a crop (sheets/crop-flags.jpg), and the vactank re-render came back clean. Durations 12.17 to 12.2 s, audio -13.9 to -14.2 LUFS, heavy iron count 0, run leads with the real cooler. Library 122 to 131 (two entries from other threads in between); week-2026-11-25/ holds the 9x16 and 16x9-music plus sheets/ and source/ (cfg, gen, publish, page, batch18, pickreal, deploy, chain25, objectaudit, wordsheet10, pairsheet, runnov25, specs, scan stubs). Project folder: assets/motion copies (35 files plus 21 silent and 21 thumbnails) verified by frame hash and duration; the filestore adds a 5,875-byte uuid manifest box to every mp4 a few seconds after upload, so a byte compare with the repo copy always differs and the check is frames or duration, not size. HOLD WEEK: the YouTube thread asked for no new volume this week (Zapier out of tasks, Metricool November limit), so these seven go into its Nov 30 batch; the own Reels poster still draws from the library.

| key | slug | category | photo | music | recording |
|---|---|---|---|---|---|
| riq3khms | listed-floral-walk-in-display-cooler (REAL) | refrigeration | real-iq3khm (listing photo) | folk | riq3khm |
| rsfmh3ls | listed-caterpillar-140h-v-plow (REAL) | landscaping | real-sfmh3l (listing photo) | road | rsfmh3l |
| n100s | combi-oven-after-the-remodel | cooking | combi-oven | clean | combioven |
| n101s | boom-lift-after-the-fitout | aerial | boom-lift-yellow | lofi | boomlift |
| n102s | control-cabinet-off-the-line | electrical | electrical-cabinet (canva-69) | tech | ecabinet |
| n103s | drill-rig-between-contracts | drilling | drill-rig (canva-72) | funk | drillrig |
| n104s | vac-truck-after-the-season | vacuum | vac-tank-truck (canva-20, logo covered) | shop | vactank |

Crop-fix review (thread, 15:41Z): five of seven clean; vac-truck-after-the-season shows only the back of the tank and hoses (no cab, no whole truck) and drill-rig-between-contracts shows a distant mast with no carrier truck while the title says truck-mounted, so both carry hold true in reels/library.json until a photo of the whole truck or rig exists (remake, do not post). All seven end on the blue seller end card (2.1 s, endcard.py check) and carry endcard seller-v1. Heavy iron: none.

## Nov 23 ~13:41Z to 14:25Z: Monday batch, seven seller Shorts at 12 s (renr7e2s, r3no15xs, n95s to n99s)
Trigger "YardSwaps Monday motion videos". Step 0 pickreal.py picked two real listings: Instapak SpeedyPacker floor model (cmwsc5e1k0011q3l6c0renr7e2) and the used pallet racking lot (cmws1onb20007qzl6ma1r3no15x); listing photo is the opener and the upload, copy names item and category only, library entries carry listing_id and real true, both ids in listings/motion-used.json in the same commit. The Instapak sits under Parts & Other on the live site; the sell screen never auto-files Parts & Other (the seller picks it), so a scan stub with category parts blocks Publish and the recording was re-filed under Warehouse. Photo pass: no clean stock left for generators, pumps, inspection cameras, automotive, cranes or paving (the demand order), so those wait for real listings; external photo hosts are 403 through the proxy, Canva folder pool is the same set as assets/canva-images. Same recipe as Nov 20 (mkdemo5 slow pace, recsell.js with scan stubs, batch18.sh, objectaudit, bordercheck, OVERLAP, cropaudit, audioaudit, whole-item 1.2 s and pair sheets, words-vs-screen sheets checked before publish, publish-nov23.py now reads the scratch finals, deploy.sh). Fixes this run: hvac-condensers source had a dark bottom band that bordercheck caught (-trim did nothing, chopped 90 px with convert -gravity South -chop 0x90); batch18 IDs must carry -10s or the finals are misnamed (renamed and fixed). Durations 12.1 to 12.2 s, audio about -14 LUFS, cropaudit clean apart from the known 2.75 s phone slide-in flag (eye-checked, full-screen photo preview). Library 115 to 122; week-2026-11-23/ holds the 9x16 and 16x9-music plus sheets/ and source/ (cfg, gen, publish, page, batch18, pickreal, objectaudit, wordsheet10, specs, scan stubs). Project folder is still at its cap: assets/motion copies (35 files), crop-fix/2026-11-23/ sheets and video-upgrade/source/v2-port sources were verified by re-reading after the save.

| key | slug | category | photo | music | recording |
|---|---|---|---|---|---|
| renr7e2s | listed-instapak-speedypacker-floor-model (REAL) | warehouse (Parts & Other live) | real-enr7e2 (listing photo) | shop | renr7e2 |
| r3no15xs | listed-used-pallet-racking-complete (REAL) | warehouse | real-3no15x (listing photo) | folk | r3no15x |
| n95s | griddle-from-the-closed-diner | cooking | flat-top-griddle | clean | griddle |
| n96s | dryers-from-the-sold-laundromat | laundry | commercial-dryers | lofi | dryers |
| n97s | condensers-after-the-changeout | hvac | hvac-condensers (90 px chopped) | tech | condensers |
| n98s | lawn-tractor-after-the-route | landscaping | lawn-tractor | road | lawntractor |
| n99s | backhoe-still-on-the-trailer | excavators | backhoe-lowboy | funk | backhoe |

Crop-fix review: seven of seven keep the whole item in the 1.2 s frame; the griddle source photo itself ends at the right edge of the unit (like the Nov 20 chairs), swap in a wider shot at the next render if the pool has one. Heavy iron: one (backhoe), in last place.

## Nov 20 ~14:40Z to 16:10Z: Friday batch, seven seller Shorts at 12 s (r90kwc7s, n88s to n93s), how-to 6 and weekly 6
(Re-written Nov 23: the Nov 20 save of this entry, the Nov 20 captions and the backlog marks were lost when the project folder hit its 10 GB cap; the media repo kept everything.) Trigger "YardSwaps Friday seller videos". Step 0 pickreal.py picked the first real listing (belt conveyor cmwm5nuh9005fql3ag390kwc7, owner cmwm5jve20055ql3a4b222kbk): the listing photo is the opener and the upload, copy names the item and category only, library entry has listing_id and real true, id in listings/motion-used.json. Same recipe as Nov 18 (mkdemo5 slow pace, recsell.js with scan stubs, batch18.sh, objectaudit, bordercheck, OVERLAP, cropaudit, audioaudit, whole-item and pair sheets, words-vs-screen sheets checked before publish, deploy.sh, publish-nov20.py). Media commit 4ac48e9 (merge f659a7d); library 92 to 99; week-2026-11-20/ holds the 9x16 and 16x9-music plus sheets/. Review page version 73 (15 superseded 17 s previews removed to stay under the 256 MiB cap).

| key | slug | category | photo | music | recording |
|---|---|---|---|---|---|
| r90kwc7s | listed-omni-metalcraft-powered-24-w (REAL) | warehouse | real-90kwc7 (listing photo) | folk | r90kwc7 |
| n88s | pressure-washer-the-crew-skips | pressure | hot-pressure-washer (canva-14) | road | washer |
| n89s | mixer-after-the-pour | concrete | towable-mixer (canva-02) | clean | mixer |
| n90s | scissor-lift-after-the-fitout | aerial | scissor-lift (canva-09) | lofi | scissor |
| n91s | lathe-from-the-closed-shop | machining | engine-lathe (canva-22) | tech | lathe |
| n92s | flatbed-after-the-last-contract | fleet | flatbed-truck (canva-93) | funk | flatbed |
| n93s | chairs-from-the-closed-office | office | office-chairs (canva-46) | shop | chairs |

Crop-fix review: six of seven clean; the office-chairs source cuts the conference table at the right edge (swap in a wider shot at the next render if the pool has one). Long videos: how-to 6 "How to sell restaurant or shop equipment" (2:06, combi oven, narrated by Justin Case, English SRT, cover; recorder rechow6.js marks a stop before stopping, frame = round((mark - t0)*30), callout y values measured from gridded screenshots) and weekly 6 (1:19, eight clips; compile.py HOLDS per-clip last-frame freeze, mixlong.py CLOSE_OFF keeps narration inside each 12 s chapter). Both in assets/motion, thumbnails/, assets/captions/ and week-2026-11-20/ (queue rows 40 and 41, SEO items 23 and 24). Project folder at 11.2 GB by du; Alan chose (card, 15:44Z) to keep everything, so the media repo and the review page are the deliverables and every project-folder save is verified by re-reading.
