# Motion video backlog

The weekly routine picks the next 3 unmade ideas from this list, top to bottom, and makes them in the standard motion format (see MOTION.md and the house-style memory). Each idea must show a real screen from the current app. Before recording, check that the feature still exists in apps/mobile/app/. If it doesn't, skip it and note why here.

Status: [ ] to do, [x] done (date).

Every Wednesday batch also makes one combined 16:9 video, assets/motion/yardswaps-weekly-N-16x9-music.mp4, from that week's three new videos (see "Weekly 16:9 compilations" in MOTION.md). weekly-1, weekly-2 and weekly-3 (Oct 28 batch) exist, seller clips only; the Nov 4 batch makes weekly-4.

## Done
- [x] 1 AI lists it (Oct 10)
- [x] 2 Find it nearby (Oct 10)
- [x] 3 Free to list (Oct 10)
- [x] 4 Message the seller (Oct 11)
- [x] 5 Save a search (Oct 11)
- [x] 6 Sell your... every category (Oct 11)
- [x] 7 Make an offer: offer, seller counters, accept in one tap (Oct 14)
- [x] 8 Dealer storefront: a demo "Your Equipment Co." store, scroll and search (Oct 14)
- [x] 9 Follow a seller: open a profile from a listing, tap Follow (Oct 14). The Sellers you follow screen was left out because one row looked empty.
- [x] 10 List 4, all boosted free (Oct 21). The hook says "the pump" instead of "the pressure washer": no pressure washer stock photo in the demo set.
- [x] 11 Already on Craigslist? (Oct 21). Broad item: flatbed work truck.
- [x] 12 See what buyers want, dealers (Oct 21). Shows the Buyer demand report, then a Dealer boost on an existing boom lift listing.

## Nov 5: TikTok search terms (MAKE FIRST in the next batch, pressure washer first)

Source: Alan's screenshots of TikTok Creator Search Insights, Nov 5 (Suggested, Content gap and Experiences tabs). These are phrases people are typing into TikTok search right now. Kept only the ones that fit our two angles (idle gear taking up space; parts on a shelf, scan the tag, list it, extra cash) and a category in `CATEGORIES`. Dropped as off topic: realtor real estate, stock market, skincare, private jets, dolls, forex, work from home, photography lighting, apartments, food, knee pain, hiring.

Numbers as shown (TikTok search popularity, not views): BlueCollar 2.02M "easy to create"; 1000 psi pressure washer 279K in Content gap (people search it, few videos answer it); Electrician Work 204K "trending in US"; building things 182K, up 68.9%; head light restoration 164K; Construction Life 95.6K; small business 87.7K "easy to create"; home improvements (no number visible).

How a search term goes into a Short (all six below):
- The exact search phrase is spoken by the screen: it sits word for word in the opener hook card (line 1 or 2), and word for word in the first line of every caption. TikTok search reads on-screen text and captions, not only hashtags. Use the phrase as people type it ("pressure washer", "electrician work", "building things", "construction life", "small business", "blue collar").
- Everything else stays the house format (MOTION.md, v2 template, situation opener, real stock or real listing photo, no faces, AI fills the fields, ends "Free to list. Free boosts.", end-card question).
- Seller-first. Never say the search number on screen and never promise views, buyers or sales. "Extra cash" is fine as Alan's wording for listing it; never "make $X".
- Only show what the label or app shows. Numbers in the hook must match the label in the photo.
- Hashtags come from the TikTok/Instagram rules in CAPTIONS.md ("TikTok search terms, Nov 5"); each item lists its machine tags.
- formats.json rows already exist for the six slugs (hook `search-term`), so the scorecard can tell whether search-term hooks beat our POV median. Keep the slugs as written or rename the row.

DEMONSTRATE, DON'T EXPLAIN (Alan's TikTok account analysis, Nov 5: 11 followers, about 1 like a post; the niche reads clearly as used equipment, dealer inventory and jobsite parts, but posts feel like static ad copy and app-screen explanation, and the audience signal is still mixed with fishing/outdoors). For the six Shorts above and every TikTok/Reels Short after them:
- The real machine or part carries the first half. Open on it for 4 to 5 s, not 1.8 s: a slow push-in or pan across the opener photo only (the phone stays whole in frame with no zoom, per the Nov 1 rule), then a close-up crop of the label or data plate (the same photo, cropped), before any app screen. The hook card sits on the photo as now.
- Show the scan as an action: the label close-up, then the phone frame snaps it and the AI fields fill in. Keep the app part to about 5 s and cut every screen that only explains a feature.
- Before/after beat at the end: the idle photo ("in the yard") next to the live listing card ("listed, free"), 1.5 s, then the end card.
- Problem first, in the searcher's words: the hook names the situation with the search phrase, never the app.
- No faces still. Gloved hands holding a part are fine when the photo has them; no people otherwise.
- Same trade words every time (blue collar, jobsite, used equipment, the machine's name) in hook, caption and tags, so TikTok learns the niche.
From the post-by-post part of the same analysis (Nov 5): the dealer-storefront lift post got 290 views and 0 reactions (static photo, text only, no demo); the missing-part app demo got 167 views and 1 like and was read as the clearest use case. So, also:
- 1-second problem frame first, shown not told: for parts Shorts the unknown part on the bench and a stalled job ("Job's stalled. What part is this?"); for idle gear the machine sitting where it's in the way. Then the app solving it.
- Chunk the app part: one short caption per screen (6 words max), about 1.5 s each, so the payoff lands by second 8.
- One bold result line on screen right before the end card, true to what the video shows, e.g. "One photo. No typing. Listed free." or "The AI read the label." Not "find the match" or "no part number needed": the app never promises a match, part number or fitment.
- Dealer posts: open on the problem on screen ("buyers can't find half your inventory": scattered listings), then the one storefront as the after. No more static-photo-with-text posts.
- VOICE-OVER TEST (Alan said yes, Nov 5): 41 and 43 get a TikTok version narrated with the ElevenLabs "Justin Case" voice (ELEVENLABS-PRODUCTION.md), short lines that follow the problem, action, result beats, music ducked under it. Keep the silent and music-only cuts for Reels and YouTube as usual. Add `"voice": true` to the formats.json rows for 41 and 43 when you make them; compare their TikTok results with 42 after a week. Every other Short stays voice-free until Alan decides from the result.

Tag these in formats.json with the existing hook and angle; add `"demo": true` to the row so the scorecard sample can be split later.

3-POST TEST (end of the same analysis): static single-frame posts (meme image, photo plus text) did worst on TikTok (105 views, 0 reactions). 41, 42 and 43 are the test: all three follow one structure, jobsite problem shown in the first second (with movement: push-in or pan from frame 0), then the app action, then the visible result (the live listing), and the first frame shows the outcome in plain words, not the brand name. No static single-frame Shorts while the test runs (Alan, Nov 5: memes are still fine as separate posts; tie the joke to one specific owner or dealer pain). Their formats.json rows carry `"structure": "problem-action-result"`; the scorecard prints them as "Video structure tests" once they have 3 settled posts.

Make these 3 first (next batch, in this order):
- [x] (Nov 7; hook without a PSI number, the Hotsy photo has no rating plate) 41 pressure-washer-1000-psi (Pressure Washers, angle: idle gear + scan the tag). Content-gap term, so this goes first. Opener: a small electric pressure washer with its rating plate or box label readable (free-licence photo: Canva stock or Wikimedia, no people; credit in SOURCES.md). Hook: "POV: you upgraded to 3000 psi." / "The 1000 psi pressure washer stayed." In the app: one photo of the label, the AI fills PSI, GPM and Power Source (Electric) from it (spec fields from equipment-specs.ts `pressure`), check, Publish. If the label in the photo shows a different PSI, put that number in the hook and keep "pressure washer" as the phrase; the caption may say "small 1000 to 2000 psi pressure washer" only if the label falls in that range. Machine tags: #PressureWasher #PressureWashing. Question: "What size pressure washer is sitting in your garage?"
- [ ] (skipped Nov 7: no free-licence labelled breaker photo in hand, Wikimedia unreachable from the cloud; 44 went in its place) 42 electrician-work-leftovers (Electrical, angle: shelf parts). Takes the "Electrical: breakers and contactors, new in box" parts-rotation item. Opener: stock `electrical-panel` in sit/. Hook: "POV: electrician work leftovers." / "Breakers still in the box." In the app: one photo of a boxed breaker or contactor with the label up; the AI reads only what the label prints (amps, poles, brand), filed under Electrical, listed as a lot. Needs a free-licence labelled breaker photo (none in hand; Wikimedia first). If no photo by batch day, swap in 43 and make this next. Machine tags: #Electrician #ElectricianWork. Question: "What's left over from your last electrical job?"
- [x] (Nov 7) 43 building-things-concrete-mixer (Concrete & Masonry, angle: idle gear; fills a "not yet" row). Opener: stock `concrete-mixer` in sit/. Hook: "POV: done building things this season." / "The mixer stays in the yard." App: one photo, AI fills the Concrete specs, Publish. Machine tags: #ConcreteMixer #Concrete. Question: "What did you buy for one build and never use again?"

Then (the batch after):
- [x] (Nov 7, made in 42's slot; the seller taps Parts & Other since the app no longer files the fallback category from a scan) 44 bluecollar-shelf-parts (Parts & Other, angle: shelf parts). Uses the copper and brass box photos already in hand (yardswaps-media photos/plumbing/: copper-tees-shop-bins, compression-isolating-valve-15mm). Takes the "copper and brass box" parts-rotation item. Hook: "Blue collar extra cash:" / "the parts already on your shelf." App: scan one valve label, the AI reads size and connection only, list the lot. Machine tags: #Plumbing #PlumbingParts. Question: "What parts are stuck on your shelf right now?"
- [x] (Nov 8, extra batch) 45 construction-life-compactor (Paving & Compaction, idle gear; fills a "not yet" row). Opener: stock `soil-compactor` in sit/. Hook: "Construction life: the job's done." / "The compactor hasn't moved since." (the copy avoids "trailer" so the object audit passes). Machine tags: #SoilCompactor #Paving. Question: "What's parked that hasn't worked all year?"
- [x] (Nov 8, extra batch; the two maker labels on the stock photo are blurred, saved as `combi-ovens-clean`) 46 small-business-old-oven (Cooking & Ovens, idle gear; fills a "not yet" row; same idea as the Oct 21 fryer pick, which it replaces). Opener: stock `combi-ovens` in sit/. Hook: "Small business owners:" / "the old oven in the back still works." Machine tags: #RestaurantEquipment #CommercialKitchen. Question: "What's sitting in the back of your kitchen?"

Lower priority, only with a photo: head light restoration (164K) as a small-items Short, "POV: you bought a polisher for one head light restoration" (Power & Hand Tools, a car buffer or polisher photo, no car plates). Home improvements: fold into idle-tool Shorts (tile saw, compressor) as a caption keyword, not a Short of its own.

Effect on the Monday category plan: 43, 45 and 46 pull Concrete, Paving and Cooking forward from Nov 16/23; Generators, Welding and Landscaping follow these.

## Next up (re-ordered Oct 20 from the market research)

Order and hooks come from MARKET-RESEARCH-NOTES.md (same folder) and the research page https://claude.ai/code/artifact/eef40f3a-ee2f-4663-929b-23e6ed0e2b57. Equipment buyers worry most about (1) scams and fake sellers, (2) saving money compared with buying new, (3) finding gear close by. POV-style hooks get about 6x the views on our channel. Keep the house format exactly as it is (MOTION.md). The research only decides which ideas go first and what the first caption line says. Titles, hashtags and captions per platform are handled by the YouTube thread's research.

Made Oct 21 (see Done above). The boost facts below still hold for later seller videos.

Boost facts (from the repo, apps/web/lib/free-boost-rules.ts + config.ts defaults on origin/main; only say what the app says):
- Starter boost: post 4 listings within 14 days of your first, and every listing you have is boosted free for 14 days. Anything posted while it runs is boosted too. Once per account.
- Boost credits: every 4 listings you post earns a free 7-day boost, up to 5. Credits never expire.
- Invite a seller: you and the seller you invite both get a free 7-day boost after their first listing has been live 3 days (REFERRAL_LIVE_DAYS = 3).
- What a boost does (BOOST_EXPLAINER): shows ahead of unboosted listings in Suggested results (home feed, search, categories) for buyers whose distance and filters match. Never promise more views or sales.
- The numbers are env-configurable. Before recording, check the app's own wording (Free boosts card / "How free boosts work" in the Sell tab, starterBoostLabel and creditProgressLabel in packages/shared/src/boosts.ts) and use exactly that. If the live values can't be checked, word it as the app's default rules and keep the numbers to what the repo shows.


Make these 3 next (Wed Oct 28). Seller-first, per Alan's Oct 21 goal: each ends "Free to list. Free boosts."

SITUATION-FIRST OPEN (from Oct 28, every seller Short). The Oct 26 YouTube report: HeyCatch's POV Shorts average about 700 views, ours about 7, with the same upload settings. Its fix: relatable POV hooks, no "#shorts" tag in titles, and open on the seller's situation (idle gear, a messy yard) before the app appears. So: designed cover first (~0.5 s, unchanged), then 1.8 s of a full-screen idle-gear stock photo with the POV hook on a white card (slate line + blue line), then the usual app video. Code: wrap the builder with `withOpener(vid,{img,l1,l2})` in source/app-first/app.html (photos in source/app-first/sit/, the 34 real stock backgrounds, never AI images). Test any builder with `OP="img|line 1|line 2" node renderapp.js nX W H out`. Keep each hook line short enough to stay on one line; the card shrinks the text if not. Use curly quotes (“ ”) in hooks. Captions: TikTok and YouTube get the app line described at the top of MOTION-CAPTIONS.md.

COVER = THE SITUATION (added Oct 26, from YouTube Analytics: our Shorts keep about 1 in 10 viewers past the first seconds, HeyCatch's about 1 in 3, and ours open on app UI). For seller Shorts the 0.5 s designed cover is the opener's own first frame: render it with `OP="img|l1|l2" node renderapp.js nX W H cf/<id>-<size> 0` (writes cf/<id>-<size>_0.png; rename it to the usual cf/<id>-<size>.png), then build with fin6.sh as usual. The hook card starts already in place, so the cover fades into the same picture and the first ~2.3 s are all situation, with no app on screen. Stills check: frame 0 and 1 s of the final file must show the photo and hook, not the app.

MUSIC ROTATION (Alan, Oct 28): synth.py now has six styles (tech, drive, punch, sunny, grit, lift). Rotate them so no two Shorts in a batch, and no two days in a row, share a style; note the style used next to each video in MOTION.md. Always keep the silent copies: Alan can post one from the TikTok or Instagram app with a trending sound from the platform's commercial library (the only way to use platform music, since auto-posting can't add it).

COMMENT QUESTION (from Oct 28, every video; asked by the engagement thread, see ENGAGEMENT-PLAYBOOK.md). Each new video gets its own question in the playbook's style: seller-first, open, answerable in a few words (pick from or add to the "Comment prompt bank" there, never repeat one already used). Captions: on Instagram, Facebook and TikTok it goes right before the link line; on YouTube right after the summary. On screen: the same question as one line in a white pill under yardswaps.com on the end card, rendered by passing `ASK="What's sitting idle in your yard?"` to renderapp.js (all four sizes; it stays inside the Reels safe zone and shrinks to fit). Use curly apostrophes.

Openers for this batch:
- Invite a seller: img farm-tractor, "POV: the tractor" / "hasn't moved since spring."
- Show the cold start: img air-compressor, "POV: every buyer asks" / "“does it start?”"
- My listings: img enclosed-trailer, "POV: it sold last week." / "Buyers still message you."
- [x] (Oct 28, spare-part; opener changed to a POV snap of a spare gear motor, canva-38, since a loose part reads better than a bucket; AI filled title, category Pumps & Motors, condition, description and a price range, no part number or fitment) FIRST (added Oct 28 from Facebook's Page assistant: our "identifying replacement parts" video is the Page's most viewed content, and Meta says heavy-machinery pages get the most engagement from specs and troubleshooting demos). Seller-first "one photo of a part" video. Opener: img mini-excavator, "POV: the spare bucket" / "doesn't fit anything you own." Then the real app: one photo of a part or attachment (a real stock photo of a bucket, hydraulic pump or similar; never an AI image), AI fills in the title, category (Parts & Other or the machine's category) and the spec fields, check, Publish, live free. Show only specs the app's AI actually returns for that photo; never claim it finds part numbers or fitment. Caption angle: list a spare part from one photo, free (not Meta's "identify your gear" buyer angle). End-card question idea: "What spare parts are sitting in your shop?"
- [x] (Oct 28, invite-a-seller; opener "POV: your buddy’s tractor") Invite a seller (owners). Hook: "Know someone with gear sitting around?" Share the invite link, you both get a free 7-day boost after their first listing has been live 3 days. (invite/)
- [x] (Oct 28, show-the-cold-start) Show the cold start (owners). Hook: "Show the cold start. Buyers will ask anyway." Add a walkaround video to a listing (sell.tsx video upload). Research: missing condition info is buyers' #1 complaint.

After that, trend picks from the YouTube thread (Oct 21, Alan's OK on trend-based content). Seller-first, ending "Free to list. Free boosts.":
- [ ] POV: the forklift's been sitting in the yard since 2022. List it in 30 seconds on the phone. Title "POV: <gear> has been sitting in the yard for years" (no #shorts tag, per the Oct 26 report) (POV-with-a-feeling titles got 1,000+ views; plain ones under 70).
- [ ] 3 things in your shop you can list free today: generator, pressure washer, welder, quick cuts, then the List 4 all boosted free offer. (Numbered-list hook is a common trades format, not measured on our channel.)
- [ ] POV: you're upgrading the kitchen and the old fryer still works. List it free with AI from photos. Restaurant gear, beyond trucks and forklifts.

Oct 26 trend picks from the YouTube thread (Friday Oct 30 batch makes these 3 first; HeyCatch's POV, "When..." and "Me..." Shorts are its top formats on our channel at ~700 views each):
- [x] "When the buyer shows up and it starts first try." Made Oct 30 as sold-it-list-the-next (mark sold in My Listings, then list the next one; music drive). Opener img: flatbed-truck or backhoe-on-trailer. Ends on list it free. (Merges with the POV forklift idea above if needed.)
- [x] "Me pretending I'll use that trailer again next season." Made Oct 30 as that-trailer-next-season (AI fills Type: Enclosed; music sunny). Opener img: enclosed-trailer (or pickup-on-trailer if My listings already used it). Self-aware seller humor, pays off with a free listing.
- [x] "POV: you finally deal with the forklift that's been sitting there." Made Oct 30 as forklift-sitting-there (AI picks power, mast, tires; music tech). Use the POV forklift item above; no forklift stock photo in sit/, so open on warehouse-racks or mini-excavator and say that gear instead.
- [ ] (Moved from the Oct 28 batch for the part video) My listings: edit, mark sold, relist (my-listings.tsx). Hook: "POV: your 6th 'is this still available?' today" (mark sold).
Friday order: these 3, then the Oct 21 picks (3 things in your shop, the fryer). Titles: a POV/When/Me line with a feeling, no #shorts.

Then:

- [ ] Spot a fake listing (buyers, trust / scams). Hook: "3 signs that listing is fake." Safety box on the listing ("never pay by wire, gift card or crypto"), the seller's verification line, local pickup. Close: "See it run. Then pay." Say the app "warns", never "blocks"; never "every seller verified".
- [ ] Find parts (buyers, save money). Hook: "POV: you need one pump, not a whole machine." Search a part, results near you, message the seller. (parts.tsx)
- [ ] Used, not new price (buyers, save money + nearby). Hook: "Why pay new?" Price estimate chip and range on a listing, then distance on cards. Broad category.
- [ ] Seller reviews: check a seller's reviews before you buy (reviews.tsx). Trust angle, hook "Check the seller first."
- [ ] Save a draft: start a listing and finish it later (drafts.tsx). Seller POV hook: "POV: the trailer's been in your yard 3 years."
- [ ] Seasonal (Nov 1 to Dec 20): "Buying before Dec 31? Let the deal find you." (saved search + price-drop alert; on-screen "Tax questions? Ask your tax pro.")
- [ ] Seasonal (Dec to Feb): "Harvest's done. The planter you won't touch till April?" (list farm gear)
- [ ] Category spotlights, one per video, rotating across the range (forklifts, fleet trucks, restaurant gear, generators, aerial lifts, farm equipment...)

## Long seller how-to series (16:9, 2 to 3 min, one a week, from Oct 21)

Seller-first, per Alan (Oct 21): longer how-to videos for regular YouTube, one a week, made Thursdays about 12 pm Central and handed to the "Running the YouTube channel" thread with chapter times. Same house style as the Shorts (real app at 3x, captions, music, no voice-over, cover first, store-badge end card), plus a "STEP N OF M" tag and one plain sentence of explanation under each caption. Builder: source/app-first/n13.js (multi-chapter version of the Shorts builder). Only say what the app shows; check the app's own wording before recording.

Alan's standing OK (Oct 21): make new content from market trends whenever a trend is stronger than the next item here, aimed at more subscribers. The YouTube thread sends its Wednesday trend picks; use them for topics and titles (POV titles with a feeling get 1,000+ views, plain ones under 70). Swap items below for trend-based ones and note why. Standing trend angle (Oct 28, Facebook Page assistant): equipment specs and quick troubleshooting demos get the most engagement on heavy-machinery pages, and our parts video is the Page's most viewed; work that angle into future seller Shorts (spec fields the AI fills, "check this before you list it"), always ending on listing it free. Data point (YouTube thread, Oct 18-25): "the machine is down" got 2 subscribers from 103 views, the best subscriber rate on the channel; downtime hooks fit this angle.

- [x] 1 How to list equipment on YardSwaps, step by step (Oct 21). 2:09. yardswaps-how-to-list-walkthrough-16x9-music.mp4.
- [x] 2 (Oct 30, 2:14, yardswaps-how-to-move-craigslist-listings-16x9-music.mp4, music grit) Moving your Craigslist listings over: paste the link, photos and details copy in, check, publish. Title idea: "POV: you're done retyping the same Craigslist ad".
- [x] (Nov 13: yardswaps-how-to-free-boosts-16x9-voice.mp4, 2:06, narrated, English SRT; recorded card, How it works sheet, Starter boost publish, boost credit publish, invite) 3 How free boosts work, start to finish: Starter boost, boost credits, invite a seller, what a boost does (no view or sale promises).
- [x] (Nov 3) 4 How to price used equipment: suggested range, similar listings, Call for Price, Answer offers automatically (accept price and floor).
- [ ] (skipped: no forklift Shorts or how-tos, Nov 8 rule) 5 How to sell a used forklift: photos that answer buyers' questions (nameplate, hour meter, walkaround video), forklift spec fields.
- [x] (Nov 20, 2:06, combi oven) 6 How to sell restaurant or shop equipment: a broad-category walkthrough (combi oven or a lift), same steps, its own specs.
- [ ] 7 Dealers (REWRITTEN 11-10: a storefront is no longer free, it comes with the Dealer plan; first 30 days free for new storefronts (was 90 until Nov 18), then $49 a month; card saved at checkout). Angle: no listing cap, all units in one link, bulk upload and website import. See the storefront promotion plan (thread "Promote the dealer storefront").
- [ ] 8 Get your listing seen: good photos, the walkaround video, keeping it current (mark sold, relist).

## Real listing photos (Alan, Oct 31)
Use real YardSwaps listing photos (public listing pages only) for openers and in-app listings when rebuilding videos 1-12. Skip any photo with a person in it (Alan: no sellers' faces, don't blur, skip). Blur plates, phone numbers, addresses. No seller names, no listing counts.
Alan (Oct 31, later): equipment images only. Seller profile icons/avatars never shown; seller details stay generic (demo name and placeholder avatar, as in the current recordings).
Alan (Oct 31): "no seller details as well". From a real listing take only the photo; title, price, location, description, specs and seller shown in the video are mock values.
Alan (Oct 31 22:24): don't use only site photos. Mix real listing photos with the stock ones, and put the best-looking photos first (openers and top of feeds).

## Nov 1 (evening): idle-gear angle is what hits
Alan (Nov 1, 3:27 pm Central): the "Forklift sitting there" Reel got good views. Next new Shorts lean on that angle: POV of gear that has not run in months (skid steer, generator, pressure washer, scissor lift, walk-behind trencher, varied across categories), then list it from the phone with one photo. Build them in the v2 template directly. A new idle-gear 9:16 added to yardswaps-media reels/library with today's "added" date posts ahead of the queue.

## Nov 2: cover every category, not just big iron (Alan)

Alan, Nov 1 night: "We should also line up small parts, this is not just for big stuff. Go read how many classes we support in YardSwaps." The class list is `CATEGORIES` in `packages/shared/src/listings.ts` (33 browsable categories plus Parts & Other). Every Short is tagged below by the category its opener photo and in-app listing actually show, so the rotation can be checked against the list instead of guessed.

Standing rule from here: the Monday batch builds the next 3 category spotlights from the "not yet" rows, real listing photo first (`assets/real-listings/`, equipment only, no faces or seller details), Canva stock already in `video-upgrade/source/v2-port/sit/` second, and briefs the Motion thread for the categories with no photo at all. Small items get the same seller-first treatment as a forklift: one photo, AI fills the fields, free to list.

Nov 8 (Alan, Runway thread): "I know we got a lot of tractor images but YardSwaps is more than just heavy machinery." Reinforces the rule above. From the Mon Nov 10 batch on, openers and featured items rotate across the range (restaurant and kitchen equipment, shop tools, generators, trailers, mowers, lifts, HVAC, parts) and no batch leads with a tractor, excavator or forklift. The long-video queue (incl. Spanish cuts) follows the same rotation when it picks cover items and thumbnails.

| Category | Covered by | Status |
|---|---|---|
| Fleet Trucks | already-on-craigslist, sold-it-list-the-next, how-to-move-craigslist-listings (flatbed), every-category (crane dump truck) | done |
| Trailers | that-trailer-next-season, find-it-nearby (backhoe on trailer) | done |
| Generators | job-wrapped-generator (Nov 9, generator-on-trailer photo, logo and plate blurred); origin-searched-everywhere (Nov 8, buy side); list-4-boosted-free (named in copy only) | done |
| Pressure Washers | pressure-washer-replaced (Nov 2, real Hotsy) | done |
| Vacuum Trucks | downsized-to-one-truck (Nov 9, stock `vacuum-truck-clean`, door name blurred) | done |
| Pumps & Motors | spare-part (gear motor) | done |
| Hydro Jetting | stock `drain-crew` in sit/ | not yet |
| Pipe Inspection | no photo | not yet |
| Compressors | ai-lists-it, snap-it-list-it, show-the-cold-start, list-4-boosted-free | done |
| Welding Equipment | stock `welding` in sit/ | not yet |
| Metalworking & CNC | shop-went-cnc-lathe (Nov 9, stock `machine-shop-clean`, labels blurred); micrometer-set-small-tools, boring-bars-tooling (Nov 2, real photos) | done |
| Auto Shop Equipment | spare-truck-wheel (Nov 2, real photo) | done |
| Power & Hand Tools | second-bay-closed-tools (Nov 9, real tool chest); chop-saw-small-tools (Nov 2, real Ryobi) | done |
| Excavators & Loaders | find-it-nearby (backhoe), follow-a-seller (mini excavator), dealer-storefront (dozer) | done |
| Paving & Compaction | construction-life-compactor (Nov 8, stock `paving-roller`, `soil-compactor`) | done |
| Forklifts | free-to-list, message-the-seller, save-a-search, make-an-offer, forklift-sitting-there, commercial-idle-forklift | done |
| Aerial Lifts | interior-job-done-lifts (Nov 9, stock `scissor-lifts`); see-what-buyers-want (boom lift) | done |
| Cranes & Rigging | stock `mobile-crane` shows people and a company name (rejected Nov 9); needs a photo | not yet |
| Concrete & Masonry | stock `concrete-mixer` in sit/ | not yet |
| Drilling & Boring | drilling-rig-parked (Nov 4, stock `drilling-rig`) | done |
| Electrical | control-panel-pulled (Nov 4, stock `electrical-panel`) | done |
| Environmental | sold-the-septic-route (Nov 9, stock `tank-hoses-clean`, cropped so the crew is out of frame) | done |
| Safety & PPE | no usable photo (`hard-hats` shows people, not allowed) | not yet |
| Farm & Ag | invite-a-seller (tractor), surplus-parts-labels (cylinders listed under Farm & Ag); real `real-deere50`, `real-tractor` | done |
| Landscaping & Turf | mowing-contract-ended (Nov 8, stock `riding-mower`) | done |
| Restaurant Equipment | second-location-closed (Nov 8, stock `commercial-kitchen`) | done |
| Commercial Refrigeration | no photo | not yet |
| Cooking & Ovens | small-business-old-oven (Nov 8, stock `combi-ovens`) | done |
| Warehouse Storage | warehouse-lease-ended (Nov 9, stock `warehouse-racks`); air-mover-fleet (Nov 2, real photo) | done |
| Retail & POS | store-closed-kiosk (Nov 8, stock `pos-kiosk`) | done |
| Office Furniture | office-went-remote (Nov 8, stock `office-furniture`) | done |
| Commercial Laundry | laundromat-upgrade-washers (Nov 8, stock `laundromat`) | done |
| Commercial HVAC | condenser-changeout (Nov 2, real Goodman) | done |
| Parts & Other | surplus-parts-cash-flow, surplus-parts-labels | done |

Count on Nov 2: 17 of 33 covered by at least one Short with that category on screen, 1 partial, 15 not yet (11 of them have stock in sit/ and can be cut without new photos; Pipe Inspection, Safety & PPE, Commercial Refrigeration and Generators need a photo first).

Next three Mondays, in this order (broad first, then the trades): Nov 9 Generators (needs photo) + Welding + Landscaping; Nov 16 Restaurant + Cooking + Commercial Laundry; Nov 23 Cranes + Paving + Concrete. Then Vacuum Trucks, Hydro Jetting, Drilling, Electrical, Environmental, Retail & POS, Office Furniture, and the three with no photo once one exists.

## Nov 3: gear laying around, parts stuck on a shelf (Alan, standing theme)

Alan, Nov 3: "Remember the marketing. The platform can also be for gear laying around: extra plumbing parts, or that old machine that can be used for extra parts. Scan the parts and make extra cash on machines or parts stuck on a shelf." This is a standing theme next to idle gear, not a one-off. Wording to keep on screen and in captions: "stuck on a shelf", "extra cash", "scan the part". The parts rule still holds: every parts video shows a real tag or label and the AI reading it, and the AI only says what the label says (no part numbers or fitment the label does not carry).

Made Nov 3 (specs n34 to n37 in the v2 template, 9:16, 4:5, 1:1 and 16:9 each):
- [x] 34 Parts donor machine: the hydraulic thumb and cylinder off an excavator that is gone (real listing photo). "POV: the excavator is gone. Its thumb is still here."
- [x] 35 The parts bin: a mixed lot of gears, sprockets and bearings sold as one lot (Canva parts wall). "POV: the parts bin you keep meaning to sort."
- [x] 36 One brass fitting: a 3/4 in. corporation stop, the label in the frame, AI reads size and connection, seller picks Parts & Other (Wikimedia photo, credited in yardswaps-media photos/plumbing/SOURCES.md). "POV: one brass fitting left from the water job."
- [x] 37 Leftover fittings: PVC and poly fittings from three jobs, new in package, one lot (Wikimedia photo). "POV: the fittings left over from the last three jobs."
- [x] Long video yardswaps-parts-stuck-on-a-shelf-16x9-music.mp4: nine parts listings back to back (queue row 17).

Rotation from here (the Monday batch takes one of these every week in addition to the category spotlights, real or free-licence photo first, part label visible):
- [x] Stripped well pump (Nov 4, stripped-well-pump): the impeller and housing off a dead pump, listed as parts (photo yardswaps-media photos/plumbing/well-pump-stripped-impeller.jpg).
- [ ] The copper and brass box: a shelf of valves and unions, scan one label, list the lot.
- [ ] Truck donor: the alternator, starter and injectors off a truck that is being scrapped (needs a real photo with a part tag).
- [ ] Compressor donor: the motor and pressure switch off a dead compressor (needs photo).
- [ ] Dealer shelf stock: a storefront listing twenty slow parts in one sitting (dealer-tools angle).
- [ ] Electrical: breakers and contactors, new in box, label up (stock `electrical-panel` in sit/ for the opener, needs a labelled part photo).

Category table rows added by these: Parts & Other now also covered by parts-donor-thumb, parts-bin-lot, plumbing-part-label, leftover-fittings-lot; Excavators & Loaders by parts-donor-thumb (the thumb is filed under Excavators & Loaders in the app); Metalworking & CNC by parts-bin-lot.

## Nov 4 (Wednesday weekly batch): well pump parts, Electrical, Drilling & Boring

The weekly motion routine took one item from the Nov 3 parts rotation and two "not yet" category rows the Monday batch is not scheduled to take (Nov 9 is Generators, Welding, Landscaping). Specs n38 to n40 in the v2 template, 9:16, 4:5, 1:1 and 16:9 each, silent copies and covers in assets/motion, 9:16 cuts in yardswaps-media reels/library with today's added date (they post next), formats.json rows added.
- [x] 38 Stripped well pump: motor, impeller housing and pulley off a dead pump, listed as parts (Wikimedia photo, credited in photos/plumbing/SOURCES.md; no label, so no part number on screen, seller picks Parts & Other). "POV: the well pump died. The parts didn't."
- [x] 39 Control panel pulled: PLC rack and modules from a decommissioned line, filed under Electrical (Canva stock, no people). "POV: the control panel from the line you pulled."
- [x] 40 Drilling rig parked: truck-mounted rig since the last well, filed under Drilling & Boring (Canva stock). "POV: the rig hasn't turned since the last well."

Count on Nov 4: 19 of 33 covered by at least one Short, 1 partial (Generators), 16 rows still not yet. 12 of those have usable stock in sit/ (Vacuum Trucks, Welding, Paving, Cranes, Concrete, Environmental, Landscaping, Restaurant, Cooking, Retail & POS, Office Furniture, Laundry; the vacuum truck stock needs the company name on the door blurred first). 4 need a photo: Hydro Jetting (the `drain-crew` stock shows workers, not allowed as an opener), Pipe Inspection, Safety & PPE, Commercial Refrigeration. Parts rotation left: copper and brass box (photos in hand), truck donor, compressor donor, dealer shelf stock, electrical breakers (need photos).

## Volume from Nov 8: 14 Shorts a week (Amplify ask)

Alan, Nov 8: "We just need to amplify our video postings and shorts and reels." The Amplify thread raised YouTube to 2 Shorts a day and IG/FB Reels to 4 a day and asked Motion for 14 new 9:16 Shorts a week (SHORTS-CADENCE.md). Agreed count: 10 a week now (5 on Wednesday, 5 on Friday) and 14 a week (7 + 7) from the week of Nov 16, after a photo-pool pass. Both Motion routines carry these numbers. Order of work: empty-scorecard categories first (Generators first), then trend picks, then the rest. Every new 9:16 goes to reels/library with its library.json entry and a formats.json row, plus a durable week-YYYY-MM-DD copy in yardswaps-media, because the project folder sits near its 10 GB cap.

Photo-pool pass (before Nov 16): find free-licence, no-face opener photos for the 4 rows without one (Hydro Jetting, Pipe Inspection, Safety & PPE, Commercial Refrigeration), blur the door name on the vacuum truck stock, and gather the parts photos still missing (truck donor, compressor donor, dealer shelf stock, electrical breakers). That pool is what limits the count, not render time.

## Measured rules from Nov 8 (feedback-loop read, Oct 25 to Nov 7)

Deployed Nov 8 under Alan's standing rule to act on measured results; both Motion routines carry them.
1. Opener: every Short opens on the real item with the blue question box inside the first second; no app screen before the 3-second mark. We hold 21% of viewers past 3 s, HeyCatch holds 32-40%. The demo format and the situation-first opener both comply; app-screen openers are retired.
2. Topics: no forklift Shorts and no app-feature explainer Shorts (21-29 views each) until the scorecard turns them back on. Make "one leftover item" Shorts for the categories buyers search and find empty: Generators, Pumps, Vacuum Trucks first (vacuum truck stock needs the door name blurred), then the other empty rows.
3. Copy the winners: micrometer set (159 views) and drilling rig (134; its question-box Short did 124 views in 24 h vs about 7 typical). Same shape: one idle or leftover item, one jobsite problem in the box, then the listing goes live.

Next Wednesday run (Nov 11) picks, in order: generator leftover item, pump leftover item, vacuum truck (if the blur is done), then trend picks that are not forklift or app-feature, up to 7.

## Nov 8 (extra batch, Alan: "we need to stack it", "we might need to make more content")

Seven more Shorts made the same day, all demo format with the question box in the first second, 17 s, music only, 9:16, 4:5, 1:1 and 16:9 each, deployed to assets/motion, the review page and yardswaps-media (reels/library + library.json + formats.json + week-2026-11-08/). They take the seven "not yet" rows that had clean stock in sit/ and leave the category plan for Nov 16/23 free for the rows that still need photos.
- 45 construction-life-compactor (Paving & Compaction) and 46 small-business-old-oven (Cooking & Ovens), from the Nov 5 search-term list above.
- 47 mowing-contract-ended (Landscaping & Turf, stock `riding-mower`). "POV: the mowing contract ended." / "The riding mower didn't." Q: "What's parked in your shed since the last contract?"
- 48 second-location-closed (Restaurant Equipment, stock `commercial-kitchen`). "POV: the second location closed." / "The prep line is still plugged in." Q: "What's still plugged in at the location you closed?"
- 49 laundromat-upgrade-washers (Commercial Laundry, stock `laundromat`). "POV: you upgraded the laundromat." / "The old washers still line the wall." Q: "What did the upgrade leave behind in your shop?"
- 50 office-went-remote (Office Furniture, stock `office-furniture`). "POV: the office went remote." / "The desks stayed." Q: "How many empty desks are you still paying rent on?"
- 51 store-closed-kiosk (Retail & POS, stock `pos-kiosk`). "POV: the store closed." / "The order kiosk didn't leave with it." Q: "What's left in the store you closed?"

Cadence from Nov 9: three runs a week, Monday 7:41 am, Wednesday 8:52 am and Friday 8:37 am Central, 7 Shorts each = 21 a week (was 10, then 14 from Nov 16). Each run starts with a photo pass (free-licence, no faces, no names) so the pool, not render time, stops being the limit. Library after this batch: 50 clips in reels/library, which lets the Amplify thread raise the TikTok and Reels counts (the 10-day no-repeat rule needs 10x the daily count).

Count on Nov 8 evening: 26 of 33 covered, 1 partial (Generators). Still not yet: Cranes & Rigging (stock `mobile-crane`), Environmental (stock `tank-hoses`), Vacuum Trucks (door name to blur), and the four with no photo (Hydro Jetting, Pipe Inspection, Safety & PPE, Commercial Refrigeration). Generators and Pumps leftover-item Shorts stay first in line for Nov 9 (Monday run) because buyers search them most.

Linear (Nov 8, Alan: track all YardSwaps work in Linear): ARK-207 Shorts production cadence (parent); ARK-212 measured rules for the Nov 11 batch; ARK-209 photo pool for the uncovered categories; ARK-211 long how-to #3 free boosts. Each batch run files "Shorts batch <date>" under ARK-207 and closes it on deploy.

PAUSED Nov 8 15:06Z (Alan: "Pause the linear stuff"): no ARK issue filing or updates from Motion until Alan says otherwise; the four issues above stay as filed.

## Nov 9: Monday run (first of the 21-a-week cadence)

Photo pass: `vacuum-truck-clean` (door name blurred), `tank-hoses-clean` (crew cropped out), `machine-shop-clean` (labels blurred) added to sit/. Rejected: `mobile-crane`, `truck-lift`, `pickup-on-trailer` (people or business names, not fixable by blur). Pumps leftover-item Short skipped (only pump photo is the stripped well pump, already used); still first in line once a second pump photo exists.

- [x] 52 job-wrapped-generator (Generators & Power, leftover item, generator-on-trailer photo). "POV: the job wrapped." / "The generator hasn't run since." Q: "What's still hooked up from your last job?"
- [x] 53 downsized-to-one-truck (Vacuum Trucks, stock `vacuum-truck-clean`). "POV: you downsized to one truck." / "The second vac truck sits in the lot." Q: "What's sitting in your lot since you downsized?"
- [x] 54 sold-the-septic-route (Environmental, stock `tank-hoses-clean`). "POV: you sold the septic route." / "The tank and hoses stayed." Q: "What stayed behind when you sold the route?"
- [x] 55 second-bay-closed-tools (Power & Hand Tools, real tool chest, small-items angle). "POV: the second bay closed." / "Every wrench is still on the wall." Q: "What tools are still hanging in the bay you closed?"
- [x] 56 warehouse-lease-ended (Warehouse Storage, stock `warehouse-racks`). "POV: the warehouse lease ended." / "The racking is still bolted down." Q: "What's still bolted down in the space you're leaving?"
- [x] 57 interior-job-done-lifts (Aerial Lifts, stock `scissor-lifts`). "POV: the interior job is done." / "Three scissor lifts, one row, no work." Q: "How many lifts are parked in your row right now?"
- [x] 58 shop-went-cnc-lathe (Metalworking & CNC, stock `machine-shop-clean`). "POV: the shop went CNC." / "The manual lathe is still on the floor." Q: "What's still on your floor since you went CNC?"

Library 53 to 60. Count on Nov 9: 29 of 33 covered. Still not yet: Cranes & Rigging (photo needed), Hydro Jetting, Pipe Inspection, Safety & PPE, Commercial Refrigeration (no photo). Photo pool is the limit for those five; the Wednesday Nov 11 run picks from the trend/idle-gear list below plus a pump leftover item if a photo turns up.

Unmade ideas still open for the next runs (no forklift, no app-feature explainers; vary categories, no heavy iron first): welder that only ran on one job (Welding), concrete mixer left after the pour (Concrete), reach-in cooler from a closed cafe (needs photo), box truck after the route was cut (Fleet Trucks), equipment trailer with no season ahead (Trailers), compressor from a shop that closed (Compressors), pressure washer the new crew never uses (Pressure Washers), HVAC condenser pulled on a changeout (HVAC), sprayer rig after the season (Farm & Ag), breaker panel pulled on a remodel (Electrical), drill rig between contracts (Drilling), pallet jack fleet after the move (Warehouse).

## Nov 8 evening (origin story, from brand/ORIGIN-STORY-KIT.md)

- [x] origin-searched-everywhere (generators), origin-part-in-a-yard (pumps), origin-sitting-cash (parts): three origin-story Shorts, library 53.
- [x] yardswaps-origin-story-16x9-voice.mp4 (2:04, narrated): YouTube queue item 20, SEO item 20.

### Nov 9 20:00Z: YouTube weekly brief (input for the Wed/Fri/Mon routines)
From the YouTube thread's Monday batch. Week of Tue 11/10 takes 14 of our Nov 8-9 whole-item cuts; keep 21 Shorts/week, 12-15 s, music only, pov-idle + direct question.
- WANTED hook (id `wanted`, "buyers looked for X", true counts, no promises): generators ~20+, pipe inspection ~10+, pumps ~10+, hydro jetting ~10, automotive / cranes / paving ~8. Pumps still owe a leftover-item Short; inspection and hydro have none yet. Categories next per SCORECARD: generators, pumps, vacuum, inspection, hydro, automotive. Stop: forklifts, feature-statement.
- Variations to build on: drilling-rig-parked (question in title) and surplus-parts-cash-flow; angle parts-spec (part-tag-scan 81 views). Idea: "Generator won't hold load? Snap the data plate first" (AI reads kW, fuel, phase).
- Trend ideas, each pov-idle 12-15 s: (a) empty-bay reveal after the item is listed; (b) "Which one would you keep?" two idle items side by side; (c) data-plate close-up first frame, "What kW is this one?" (still must fit the whole item within second 1).
- LONG-FORM queue asks (3 English items left after this week): a 15-s Short cut from each long video; 2-4 min best-of compilations by theme (closed locations / small-business gear; vacuum + septic + environmental; generators + power) from the whole-item cuts; narrated how-tos on photos that sell and on answering buyer messages (narration blocked until ElevenLabs credits reset). Not started; needs Alan's go-ahead or the next routine's spare capacity.

## STOREFRONT SHORTS (added 2026-11-10, thread "Promote the dealer storefront"; Alan's goal: Dealer plan subscriptions + app downloads)
Plan doc: https://claude.ai/artifact/EV9q2xbVrpznzyffEBNfi5 . House style as always (12-15 s, music only, whole item fit in frame for the first second, zoom <= 1.04x, blue question box, no app before 3 s, same item in opener and app, problem -> action -> result). Demo store "Your Equipment Co." only, never a real dealer's name/phone/listings.
Library entries for these four: add `"audience": "dealer"` (Facebook then links /dealers, media PR #47) and a body that ends "Free to list. Free boosts.".
CLAIMS (checked in the app code 11-10): storefront needs the Dealer plan; first 30 days free for new storefronts (was 90 until Nov 18), then $49 a month; no listing cap; website import with Read more units (you pick the units, photos and prices come with them); stats 30/90/180 days + CSV from the trial. Verified Dealer badge and 5 Dealer boosts a month ONLY after the first payment. Never "top of search", never views/sales, never empty searches, no $490/yr.
- [x] (Nov 11, `whole-lot-one-link`, slug as planned; mobile storefront, Share storefront button, "Link copied" toast stands in for the share sheet) whole-lot-one-link (Trailers: enclosed cargo trailer on a lot). 0-3 s "Your units, spread over three websites." Box: "How many places do you list each unit?" App: that trailer first on a storefront, scroll, store search "trailer", tap Share, link copied. End: "Your whole lot, one link. First 90 days free." + store badges. (Re-cut Nov 18 to "First 30 days free, then $49 a month", media PR #74.)
- [x] (Nov 11, `import-from-your-website`; the mobile card says "Scan my website", not "Read more units"; 4 units found, the roller unticked, Import 3 listings, "3 listings posted") import-from-your-website (Generators: towable generator on a dealer lot). 0-3 s "Already listed on your own website?" Box: "Where does your inventory live today?" App: Website import, paste site, Read more units, tick 3 units incl. that generator, photos and prices come in. End: "Bring your website over. You pick the units."
- [x] (Nov 13, n66) storefront-stats (Welding: welder on its cart in a shop). 0-3 s "Which units do buyers actually look at?" Box: "Which unit gets the most calls at your shop?" App: Storefront stats 30/90/180 switch, that welder's row (views, saves, messages), Download CSV. End: "Storefront stats from day one of the trial."
- [x] (Nov 13, n67) socials-on-storefront (Cooking: commercial oven in a closed kitchen). 0-3 s "Your shop page, your socials, one place." Box: "Where do your customers follow you now?" App: storefront header with hours, service area, Instagram/Facebook/YouTube icon row, Follow, the oven in the inventory. End: "Your storefront: first 90 days free, then $49 a month." (Re-cut Nov 18 to 30 days, media PR #74.)
- [x] (Nov 13, n68: no "found nothing" frames, no "Few listed" rows, end card "Dealer boosts start with the first payment") RE-CUT see-what-buyers-want as see-what-buyers-want-v2: drop the "Searches that found nothing" card and any frame showing that section of the Buyer demand report (held since 11-10, media PR #46). Keep the boost part; say the Dealer boosts start with the first payment.
Captions for each: see the "Sample posts" section of the plan doc.
- [ ] LONG-FORM storefront walkthrough (16:9, 2-3 min, music only + captions; narration blocked by ElevenLabs credits): demo account "Your Equipment Co.": open the Dealer plan (30 days free, then $49/mo, card saved, nothing charged until day 30; was 90 days until Nov 18), Website import with Read more units (tick units, photos and prices come in), the finished storefront (search, category chips, hours, service area, social icons, Follow, Share), storefront stats 30/90/180 + CSV. Title: "How to open an equipment dealer storefront and import your inventory (YardSwaps)". Description and claims: STOREFRONT-POSTS.md. Goes in the YouTube 8:30 am long slot; cut a 15-s Short from it.

### Nov 11 (Wednesday batch): 7 Shorts, n59 to n65
Storefront first (the brief: two of the four this run): n64 whole-lot-one-link (enclosed trailer, canva-18, demo store "Your Equipment Co." with no Verified Dealer badge) and n65 import-from-your-website (towable generator, canva-13). Then the empty-scorecard categories: n59 trash-pump-after-the-job (Pumps leftover-item, canva-17), n60 inspection-camera-in-the-van (first Pipe Inspection, canva-15), n61 second-jetter-by-the-fence (first Hydro Jetting, canva-12), n62 cooler-still-humming (first Commercial Refrigeration, canva-60), n63 chain-hoist-on-the-beam (first Cranes & Rigging, canva-76: a hoist, because every crane stock shows people). No heavy iron, no forklift, no tractor lead. Photos are Canva stock originals fitted whole (no crop); objectaudit tables gained the five photos, the five recordings (`trashpump`, camera, jetter, cooler, hoist) and `import`. Still owed: storefront-stats (welder), socials-on-storefront (oven), see-what-buyers-want-v2 (Friday); Safety & PPE still has no people-free photo (canva-65/66 are gear racks, usable for a "safety gear" spotlight next).

## Nov 13 (Friday batch): four more categories filled
- [x] lift-still-bolted-down (Auto Shop Equipment, two-post lift, canva-01), box-truck-after-the-route (Fleet Trucks, canva-11), roller-after-the-overlay (Paving & Compaction, canva-81), safety-gear-on-the-wall (Safety & PPE, canva-66, the first usable PPE opener). Scorecard categories still owed after this run: none of the Nov 12 list (generators, pumps, vacuum, inspection, hydro, automotive all have a demo-format Short now).

## Nov 16 (Monday batch): seven idle-gear Shorts, n74 to n80
Photo pass from the Canva stock sheets (free licence, no faces, no business names, fitted whole, no crop): `stick-welder` (canva-27), `towable-compressor` (canva-16), `rooftop-unit` (canva-06), `sprayer-rig` (canva-41), `light-tower` (canva-05), `fryer-line` (canva-62), `zero-turn-mower` (canva-89). No heavy iron, no forklift, no tractor or excavator lead.
- [x] 74 welder-from-one-job (Welding). "POV: the welder you bought" / "for one job, two years ago." Q: "What did you buy for one job and never use again?"
- [x] 75 compressor-by-the-fence (Compressors). "POV: the crew rents compressors now." / "The towable one sits by the fence." Q: "What is parked by your fence since you switched to rentals?"
- [x] 76 rooftop-unit-on-the-pallet (HVAC). "POV: the changeout is done." / "The old rooftop unit is on a pallet." Q: "How many pulled units are on pallets behind your shop?"
- [x] 77 sprayer-after-the-season (Farm & Ag). "POV: the season ended." / "The sprayer is still at the field edge." Q: "What is still parked at your field edge from last season?"
- [x] 78 light-tower-after-night-work (Generators & Power). "POV: the night work ended." / "The light tower has not lit since." Q: "What has not lit up since your last night job?"
- [x] 79 fryers-from-the-closed-kitchen (Cooking & Ovens). "POV: the kitchen closed." / "The fryer line never got sold." Q: "What is still sitting in the kitchen you closed?"
- [x] 80 zero-turn-after-the-account (Landscaping & Turf). "POV: you lost the big account." / "The zero-turn is still on the trailer." Q: "What is still strapped on your trailer from the last account?"
Used from the Nov 9 open list: welder one job, compressor from a closed shop (as the rental-switch variant), HVAC changeout (rooftop unit instead of a condenser), sprayer after the season. Library 74 to 81.

Unmade ideas still open (no forklift, no app-feature explainers, vary categories, no heavy iron first): concrete mixer left after the pour (Concrete), reach-in cooler from a closed cafe (needs photo), equipment trailer with no season ahead (Trailers), pressure washer the new crew never uses (Pressure Washers), breaker panel pulled on a remodel (Electrical), drill rig between contracts (Drilling), pallet jack fleet after the move (Warehouse), plasma cutter after the fab contract (Metalworking & CNC), ice machine from the closed bar (Commercial Refrigeration, needs photo), stump grinder after the clearing job (Landscaping), portable AC units after the rental season (HVAC), pallet wrapper after the 3PL move (Warehouse), tire changer from the closed bay (Auto Shop), trench shoring boxes between jobs (Safety & PPE / Drilling). Plus the Nov 9 trend ideas (empty-bay reveal, "which one would you keep", data-plate first frame) and the long-form storefront walkthrough above.

## Nov 18 (Wednesday batch): seven seller Shorts at 12 s, n81s to n87s
No eligible real listing (pickreal found none with a photo), so all seven from the backlog. Generator first, then the two YouTube-thread asks, one heavy-iron cut not first, two small-item lots.
- [x] 81 generator-for-the-storm-season (Generators & Power). "POV: the generator you bought" / "for storm season. It never ran." Q: "What did you buy for storm season and never run?"
- [x] 82 soldadora-en-el-carrito (Welding, Spanish). "POV: la soldadora MIG en el carrito." / "Nadie la enciende desde marzo." Q: "¿Qué soldadora tienes parada en el taller?"
- [x] 83 read-the-plate-welder (Welding, data-plate specs angle). "POV: you forgot the amps." / "The plate did not." Caption "Forgot the amps? Snap the plate."; the app fills amps, volts and process from the plate photo. Q: "Which machine's plate do you need to read again?"
- [x] 84 skid-steer-after-the-grading (Excavators & Loaders). "POV: the grading work dried up." / "The skid steer sits by the pile." Q: "What is parked by your dirt pile since the last job?"
- [x] 85 dump-trailer-after-the-cleanouts (Trailers). Takes "equipment trailer with no season ahead". "POV: you stopped doing cleanouts." / "The dump trailer sits in the lot." Q: "What is sitting in your lot since you stopped hauling?"
- [x] 86 cord-reels-after-the-events (Electrical, small items, lot of 6). "POV: the event work dried up." / "The cord reels sit in the shop." Q: "How many cord reels are stacked in your shop?"
- [x] 87 wrench-wall-from-the-sold-shop (Tools, small items, lot). "POV: you sold the shop." / "The wrench wall came home with you." Q: "What came home with you when you sold the shop?"
Used from the open list: equipment trailer with no season ahead. Still open: concrete mixer, reach-in cooler (needs photo), pressure washer the new crew never uses, breaker panel pulled on a remodel, drill rig between contracts, pallet jack fleet, plasma cutter, ice machine (needs photo), stump grinder, portable AC units, pallet wrapper, tire changer, trench shoring boxes, plus the Nov 9 trend ideas. New ideas added Nov 18 (both from today's angles): a Spanish cut of the trash pump or the generator (ES captions worked end to end), a data-plate cut for a compressor or a pump ("Snap the plate" fills hp, voltage, phase), and a two-photo lot cut (two plate photos, one listing). Demand categories still without a clean stock photo: cranes, pumps (second), inspection, automotive; wait for real listings.

### Nov 16 afternoon: 10-second cuts (YouTube report)
Shorts are now cut at 10 s (mkdemo5: opener 2.4 s, four captions, brand card). 15 re-cut and swapped into reels/library (today's seven plus trash pump, well pump, inspection camera, chain hoist, two-post lift, roller, vac truck, jetter). Next runs: every new Short at 10 s; generators first (the only Nov 9 generator Short has no raw recording left to re-cut), then pumps, inspection, automotive, cranes, paving; no origin-story openers, no forklifts.

### Nov 16 evening: real-listing Shorts
From Nov 18, up to 2 of each run's 7 Shorts come from new approved listings (pickreal.py); they do not count against the backlog ideas above. Slug pattern `listed-<short-title>`.
YouTube thread, Nov 16 evening: 10 new 10 s rows scheduled Tue 11/17 to Mon 11/23 (media e5216d2), nothing held. Open slots for the Nov 18 run: Fri, Sat, Sun, Mon 10:00 am and Sun 11/22 1:30 pm. Asks for Nov 18: a Spanish "soldadora" 10 s cut (welder, ES captions), and one try of an equipment-specs angle (one photo of the data plate, the app fills the spec fields). Weekly target 14 Shorts at 8-10 s plus 10 s cuts pulled from the longs; no new longs needed this week.

## Nov 25 (Wednesday batch): seven seller Shorts at 12 s, riq3khms, rsfmh3ls and n100s to n104s
Made: listed-floral-walk-in-display-cooler (REAL, Commercial Refrigeration), listed-caterpillar-140h-v-plow (REAL, Landscaping & Turf), combi-oven-after-the-remodel (Cooking Equipment), boom-lift-after-the-fitout (Aerial Lifts), control-cabinet-off-the-line (Electrical), drill-rig-between-contracts (Drilling & Boring), vac-truck-after-the-season (Vacuum Trucks). Details MOTION.md "Nov 25 ~14:52Z". YouTube thread holds posting this week; clips queue for its Nov 30 batch.
Unmade ideas still open (no forklift, no app-feature explainers, vary categories, no heavy iron first; "needs photo" means no clean stock in the pool, wait for a real listing): reach-in cooler from a closed cafe (needs photo), equipment trailer with no season ahead (Trailers), pallet jack fleet after the move (Warehouse), plasma cutter after the fab contract (Metalworking & CNC), ice machine from the closed bar (Commercial Refrigeration, needs photo), stump grinder after the clearing job (Landscaping), portable AC units after the rental season (HVAC), pallet wrapper after the 3PL move (Warehouse), tire changer from the closed bay (Auto Shop), trench shoring boxes between jobs (Safety & PPE / Drilling), standby generator from the sold building (Generators, needs photo), dewatering pump after the trench job (Pumps, needs photo), gantry crane from the closed fab shop (Cranes, needs photo), plate compactor after the patio job (Paving, needs photo), POS terminals from the closed shop (Retail / POS, needs photo), walk-behind floor scrubber after the contract ended (Warehouse / janitorial, needs photo), welder after the pipeline job (Welding), air compressor from the closed body shop (Compressors), sewer camera after the contract ended (Pipe Inspection, needs photo), dish machine from the closed restaurant (Restaurant Equipment, needs photo).

## Nov 23 (Monday batch): seven seller Shorts at 12 s, renr7e2s, r3no15xs and n95s to n99s
Made: listed-instapak-speedypacker-floor-model (REAL, Warehouse; live listing sits in Parts & Other), listed-used-pallet-racking-complete (REAL, Warehouse), griddle-from-the-closed-diner (Commercial Cooking), dryers-from-the-sold-laundromat (Laundry), condensers-after-the-changeout (HVAC), lawn-tractor-after-the-route (Landscaping), backhoe-still-on-the-trailer (Excavators & Loaders). Details MOTION.md "Nov 23 ~13:41Z".
Unmade ideas still open (no forklift, no app-feature explainers, vary categories, no heavy iron first; "needs photo" means no clean stock in the pool, wait for a real listing): reach-in cooler from a closed cafe (needs photo), equipment trailer with no season ahead (Trailers), breaker panel pulled on a remodel (Electrical), drill rig between contracts (Drilling), pallet jack fleet after the move (Warehouse), plasma cutter after the fab contract (Metalworking & CNC), ice machine from the closed bar (Commercial Refrigeration, needs photo), stump grinder after the clearing job (Landscaping), portable AC units after the rental season (HVAC), pallet wrapper after the 3PL move (Warehouse), tire changer from the closed bay (Auto Shop), trench shoring boxes between jobs (Safety & PPE / Drilling), standby generator from the sold building (Generators, needs photo), dewatering pump after the trench job (Pumps, needs photo), gantry crane from the closed fab shop (Cranes, needs photo), plate compactor after the patio job (Paving, needs photo), POS terminals from the closed shop (Retail / POS, needs photo), walk-behind floor scrubber after the contract ended (Warehouse / janitorial, needs photo).

## Nov 20 (Friday batch): seven seller Shorts at 12 s, r90kwc7s and n88s to n93s
Made: listed-omni-metalcraft-powered-24-w (FIRST REAL LISTING, Warehouse), pressure-washer-the-crew-skips (Pressure Washers), mixer-after-the-pour (Concrete), scissor-lift-after-the-fitout (Aerial Lifts), lathe-from-the-closed-shop (Metalworking & CNC), flatbed-after-the-last-contract (Fleet Trucks), chairs-from-the-closed-office (Office Furniture). Also how-to 6 (restaurant or shop equipment, 2:06) and weekly 6 (1:19). Details MOTION.md "Nov 20 ~14:40Z".
Unmade ideas still open (no forklift, no app-feature explainers, vary categories, no heavy iron first): reach-in cooler from a closed cafe (needs photo), equipment trailer with no season ahead (Trailers), breaker panel pulled on a remodel (Electrical), drill rig between contracts (Drilling), pallet jack fleet after the move (Warehouse), plasma cutter after the fab contract (Metalworking & CNC), ice machine from the closed bar (Commercial Refrigeration, needs photo), stump grinder after the clearing job (Landscaping), portable AC units after the rental season (HVAC), pallet wrapper after the 3PL move (Warehouse), tire changer from the closed bay (Auto Shop), trench shoring boxes between jobs (Safety & PPE / Drilling), standby generator from the sold building (Generators, needs photo), dewatering pump after the trench job (Pumps, needs photo), gantry crane from the closed fab shop (Cranes, needs photo), plate compactor after the patio job (Paving, needs photo).
