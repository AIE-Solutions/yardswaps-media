# YardSwaps messaging guide

One page. Every post, ad, email, caption, DM, store listing and agent prompt
follows it. Where older copy notes in this repo or the app repo disagree, this
page wins. Owner: Alan. Started 2026-11-21 ("if we grow we should have a clear
precise message").

## The one line

> **YardSwaps is the marketplace for used commercial and industrial equipment.
> Snap a photo and the AI writes the listing.**

Short form (bios, store subtitle): "Buy and sell used equipment. AI writes the
listing from your photos."

## What we say to each audience

| Audience | Lead with | Then | Link |
|---|---|---|---|
| **Anyone selling** (owners, contractors, shops with one or two units) | "Equipment sitting idle? List it free." | The AI writes the listing from your photos. No selling fee. Local pickup. | yardswaps.com/i (or the platform letter, see below) |
| **Dealers and businesses with stock** | "Open your storefront." | Your logo, website and social links, your inventory imported from your site or a spreadsheet, stats and a buyer demand report, and your new listings featured in our social posts. 30 days free, then the founding price. | yardswaps.com/s (offer: yardswaps.com/o) |
| **Buyers** | "Find used equipment near you." | Message the seller, make an offer, pick it up. | yardswaps.com/h |

Rules that come with the audiences:

- **Dealers never hear "posting is free" or "list it free".** Their message is
  the storefront and what it does for them. No "Free to list. Free boosts." line
  under a storefront clip, email or DM.
- **Dealers set up their own storefront.** Point them to the website import or
  the spreadsheet paste. Never offer to load their inventory for them.
- **Sellers hear free listing first**, then the AI, then no selling fee.
- One clip, one audience. A storefront clip ends on the storefront; a seller
  clip ends on free listing.

## The offer, word for word

Source of truth: `packages/shared/src/founding-offer.ts` in the app repo. Copy
these lines; don't rephrase the numbers.

- **Monthly (the headline):** "Open your storefront free for 30 days. Then $29
  a month for your first 3 paid months, our founding price for the first 100
  storefronts. Then $49 a month."
- Short: "30 days free, then $29/mo for 3 months, then $49/mo. First 100
  storefronts."
- Safe add-on: "Cancel before day 30 and you pay nothing."
- **There is no closing date.** Never write "by Dec 1", "ends soon", "this
  week only" or any deadline. The limit is the first 100 storefronts.
- **Yearly:** the plan page shows $490/yr, with the founding deal ($60 off the
  first year). Outbound copy does not lead with yearly or quote a yearly figure
  until the first yearly founding redemption is logged; "$490" is on the
  outbound banned list until then.
- **Pro (sellers):** $9.99/mo or $99/yr. **Boosts:** 1 day $2.99, 3 days $7.99,
  7 days $14.99; every 4 listings earns a free 7-day boost, up to 5. AI scan
  packs are not promoted yet.
- When the founding spots run out, the app switches copy off with
  `FOUNDING_IN_COPY`; posts and agents stop using the founding line the same day.

## Words we use

| Say | Don't say | Notes |
|---|---|---|
| storefront | dealer storefront, dealer account, shop page (as a name) | "Open your storefront" |
| Storefront plan | Dealer plan | Renamed 2026-11-21 |
| Storefront boosts | Dealer boosts | 5 a month, from the first payment |
| storefront trial / 30 days free | free dealer trial, free storefront | The storefront is free for 30 days, not free |
| founding price | founding dealer price, early-bird | |
| dealers, businesses | | Only to say who the storefront is for: "for dealers and equipment businesses" |
| Verified Dealer badge, the Dealer chip | | Buyer-facing labels, kept on purpose. Badge = paid plan (or team approved) plus a confirmed phone. It is not an inspection. |
| used commercial and industrial equipment | heavy equipment only, a single trade | Vary examples across trades; lead broad (trucks, trailers, forklifts, generators, tools, restaurant gear) |
| list it free, no selling fee | commission-free forever, always free | |
| paused (a lapsed storefront) | deleted, removed | Nothing is deleted when a plan ends |

Internal ids, routes and Stripe names (`dealer_monthly`, `/account/dealer`,
`/dealers`, `/dealer/<slug>`) stay as they are; users don't read them.

## Proof points we can back up

Use only these, or a number pulled the same day from the admin digest.

- Free to list. No fee when it sells. Local pickup only.
- Take photos and the AI fills in the title, make, model and specs, and suggests
  a price. You check it before it posts.
- Buyers message the seller in the app and can make an offer.
- Web, iPhone and Android apps.
- Storefront: logo, banner, website and social links, hours, service area,
  reviews, followers, no listing cap, bulk upload, inventory feed, website
  import, spreadsheet paste, stats for 30/90/180 days with CSV, buyer demand
  report, saved replies, and new listings in our social posts.
- Business verified (free): our team checked the legal name and address.
- Verified seller (free, any account): the green check next to a name means
  the phone was confirmed with a one-time text code. Recommend it as trust
  ("so buyers and other sellers know you're reachable"), never as an ID check
  and never as more views or sales.
- Nationwide. YardSwaps, Inc., a Delaware company.

Not proof: view counts we can't show, "thousands of buyers", "sells fast",
competitor claims we haven't checked.

## Do

- Write plain and concrete: what it is, what it costs, what to tap.
- Post as the business. Emails and DMs come from one real person: "I'm Alan
  Jacquez, Cofounder and CEO of YardSwaps." Articles: "By the YardSwaps team".
- End social captions with an open question.
- Show the real item, whole, and say only what the video shows.
- Cite credible sources only (manufacturer, government, trade body).

## Don't

- **No category count.** Never "33 categories" or any number of categories.
  Say "List commercial or industrial equipment", or a few examples then "and more".
- **Never promise views, sales, leads or placement** ("more views", "will
  sell", "top of search", "guaranteed").
- **No promotion until its payout path is verified end to end**: live price or
  coupon, code on main, one logged redemption.
- Never tell anyone their search "came up empty" or that we "found nothing".
- No location on social; no faces or plates; no founder photo.
- No hype words ("hell nah", "game changer", "insane deal").

## Links

| Link | Goes to | Use for |
|---|---|---|
| yardswaps.com/s | /dealers | Storefront posts, dealer emails |
| yardswaps.com/o | /dealers?offer=founding | The founding offer |
| yardswaps.com/i, /f, /t, /y, /x, /h, /r, /l, /p, /d, /c | /sell-equipment | Seller posts (one letter per platform, see UTM-LINKS.md) |

## Where this is enforced

- App repo `apps/web/lib/data/copy-rules.json`: the banned phrases, checked at
  send time (`lib/copy-rules.ts`) and on files with
  `node scripts/check-copy-rules.mjs <files>`.
- Media repo posting engines: `reels/post_reels.py`, `reels/post_tiktok.py`,
  `reels/promos.json` (storefront clips get storefront captions and links).
- Agent prompts in `agents/` and the scheduled tasks read this page before
  writing copy. The daily Guard checks new copy against it.
- HeyCatch writes its own captions; its brief and phrases-to-avoid list must
  match this page (Alan changes those in app.heycatch.ai).
