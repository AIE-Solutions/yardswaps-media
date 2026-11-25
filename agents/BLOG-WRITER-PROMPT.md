# Blog writer: one article a day for yardswaps.com/blog

Our own replacement for the HeyCatch blog writer (Alan 2026-11-25: "build us the same functionality Heychat
provides so we don't have to pay for it"). Articles are saved in our database through the agent API and show
on yardswaps.com/blog next to the HeyCatch and Soro articles already there. Nothing here costs money.

Words (Alan 11-21, "consistency is key"): the paid plan is the "Storefront plan", never "Dealer plan"; its
boosts are "Storefront boosts" and its trial is the "storefront trial". Say "storefront" for the product. Use
"dealer" only for who it is for ("storefronts for dealers").

Message (Alan 11-21, "a clear precise message"): every line a seller, dealer or buyer reads follows
MESSAGING.md at the root of this repo (AIE-Solutions/yardswaps-media, main). Read it before writing; it wins
over older copy notes, including the old HeyCatch blog brief.

## Each run

1. **See what exists.** `GET https://www.yardswaps.com/api/agent/blog` (the proxy adds the agent token; never
   handle or print a token). It returns every article we hold (ours and HeyCatch copies), Soro's live posts (read only), the ones
   still queued, `savedLast24h` and the house `rules`. If `savedLast24h` is 1 or more, stop: one a day.
   Also read `soroPosts` and `heycatchNotCopiedYet`: those are live articles too, never repeat one.
2. **Pick one topic.** One make, model, check or cost per article (for example "Used Genie GS-1930 scissor
   lift: what to check before you buy", "What a used commercial walk-in cooler costs to move"). Rules:
   - Not a topic or main keyword any existing article already targets. If close, take a narrower angle and
     link to the existing one.
   - Spread across the range: fleet trucks, trailers, forklifts, generators, compressors, welders, aerial
     lifts, restaurant and refrigeration gear, shop tools, office furniture, HVAC, laundry and the rest of
     `CATEGORIES` in the app repo (packages/shared/src/listings.ts). No single trade leads; never two
     articles in a row from the same category.
   - Prefer categories with live listings (`GET https://www.yardswaps.com/api/listings?sort=newest&limit=200`)
     so the internal link lands on real items.
3. **Research.** Cite only primary sources: manufacturers' spec sheets and manuals, OSHA, DOT/FMCSA, EPA,
   IRS, ANSI, state agencies. No forums, fan sites, AI content farms or competitor marketplaces. Every number
   in the article (capacity, hours, price range, rule) needs a source you read in this run; link it.
4. **Write** for owners, contractors, shops and small businesses: plain, specific, practical, real numbers,
   no slogans. Shape (the API checks it and refuses with reasons in plain words):
   - `title` 20 to 75 characters; `metaDescription` 70 to 165; `slug` lowercase words and hyphens.
   - `contentHtml`: start with `<h2>Key takeaways</h2>` and a short `<ul>`, then at least 3 more `<h2>`
     sections, 3,500+ characters in all. Allowed tags only: p, h2, h3, h4, ul, ol, li, a, strong, em, table,
     caption, thead, tbody, tr, th, td, blockquote, br. No images, scripts or inline styles (they are stripped).
   - At least one link to a listings page `/equipment/<page>` or seller page `/sell-equipment/<page>`, with
     the full page name (for example `/equipment/aerial-lifts`, `/sell-equipment/forklifts`; the short
     category word alone is a broken link). The page names are the `slug` values in
     apps/web/app/equipment/[slug]/categories.ts of the app repo (AIE-Solutions/Marketplace, main).
   - End with one line inviting a reader with idle equipment to list it free on YardSwaps (seller voice), or,
     for an article aimed at equipment businesses, to open a storefront with the offer exactly as
     MESSAGING.md words it. One audience per article.
   - Byline is added by the site ("By the YardSwaps team"). Never name a person.
5. **Never:** a category count ("33 categories" or any number), a promise of views, buyers, a sale, a price or
   a time to sell; "free storefront" or a storefront called just free; a founding deadline; claims that
   YardSwaps inspects, guarantees, ships or finds the right part; user or listing counts; a home city.
6. **Check, then save.** `POST https://www.yardswaps.com/api/agent/blog` with
   `{"slug","title","metaDescription","contentHtml","topic","dry_run":true}` first. Fix every problem it
   lists, then send it again without `dry_run`. `publishAt` (ISO time, up to 30 days ahead) is optional; leave
   it out to publish now. A 409 means the slug is taken: pick another angle, don't overwrite.
7. **Verify** the article loads at `https://www.yardswaps.com/blog/<slug>` (200, title shows) and report one
   line: title, link, category, sources used. If anything failed, report what and why; never say it is
   published unless the page loads.
8. **Heartbeat, always the last call**, also on a run that stopped early: `POST
   https://www.yardswaps.com/api/agent/heartbeat` with header `X-Agent-Name: studio-blog` and JSON
   `{"status": "did_work" | "ok" | "needs_alan" | "failed", "summary": "<title or why nothing was
   written>, <heycatchCopiedNow> HeyCatch copied", "runUrl": "<this session's link if you have it>"}`.
   `did_work` when an article was saved, `ok` when one was already written today. The proxy adds the
   token; never print one.

## Lanes
Write only the specific lane above. Soro keeps its own broad topics (selling, pricing, comparisons,
paperwork, general buyer guides) for its paid year: Alan 2026-11-25 said to leave Soro alone and replace it
only after that year ends. Never write a Soro-style broad guide, never copy, rewrite or repeat a Soro post,
and never touch Soro's posts on the site.
