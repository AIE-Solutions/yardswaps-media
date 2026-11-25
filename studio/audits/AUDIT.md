# Studio audit, 2026-11-25

Site https://www.yardswaps.com. Read only. Overall **91/100**.

| Part | Score |
|---|---|
| SEO and GEO | 90.8/100 |
| &nbsp;&nbsp;crawl and index | 21.97/25 |
| &nbsp;&nbsp;on-page | 24.61/25 |
| &nbsp;&nbsp;structured data and GEO | 22.76/25 |
| &nbsp;&nbsp;speed and technical | 21.48/25 |
| Landing pages | 93/100 |
| App listings | 90/100 |

## Fixes, most points first

1. **SEO and GEO: HTML under 500 KB (uncompressed)** (+2.6). 26 of 26 sampled pages heavier; largest 1100 KB
   Prompt: In AIE-Solutions/Marketplace (apps/web): Trim the server HTML of the heavy pages: fewer listings inlined in the RSC payload, no duplicated JSON (docs/web-performance.md). Start with: / (1100 KB), /equipment/fleet-vehicles (1007 KB), /listing/cmwv854ej002equ3ayr92unc7 (1006 KB), /listing/cmwv7vedx001yqu3ahhjbq30f (1001 KB), /listing/cmwf235fa001qqk3al5civojb (1000 KB).
2. **App Store listing: Description: banned by copy-rules.json: "found nothing" (…urs, and a lot of the time we found nothing. So we built a pla…); the first lines (shown before 'more') leave out the AI listing** (+2.5)
   Prompt: In AIE-Solutions/Marketplace, edit apps/mobile/asc-runbook/paste/06-description.txt (Description, at most 4000 characters): banned by copy-rules.json: "found nothing" (…urs, and a lot of the time we found nothing. So we built a pla…); the first lines (shown before 'more') leave out the AI listing. Follow MESSAGING.md and copy-rules.json.
3. **SEO and GEO: Indexable pages linked on the site are in the sitemap** (+2.48). 31 indexable pages linked but not submitted
   Prompt: In AIE-Solutions/Marketplace (apps/web): Add the linked, indexable pages that are missing to apps/web/app/sitemap.ts, or noindex them if they should not rank. Start with: /videos/yardswaps-how-it-works-v3.mp4, /seller/cmwf21c2q001hqk3aryuivxu7, /seller/cmwtgi9q70005lh3ajbs9vq68, /seller/cmwls9l5d003jql3ay3lboj0s, /seller/cmwkyvxry000gpk3a0t8acol8.
4. **SEO and GEO: Article markup has a date and an author** (+1.67). 1 of 6
   Prompt: In AIE-Solutions/Marketplace (apps/web): Give the BlogPosting JSON-LD on /blog/[slug] an author (the 'YardSwaps team' Organization) next to datePublished and dateModified. Start with: /blog/buying-used-machinery-playbook, /blog/used-enclosed-cargo-trailer-for-sale-buying-guide, /blog/used-pressure-washer-trailer-for-sale, /blog/used-dumping-trailer-for-sale-inspection-pricing-guide, /blog/best-used-skid-steer-verification-guide.
5. **SEO and GEO: Share cards (og:title and og:image)** (+0.92). 20 of 26
   Prompt: In AIE-Solutions/Marketplace (apps/web): Add openGraph title and image to generateMetadata on the pages listed. Start with: /blog/used-box-truck-gvwr-cdl-usdot-rules, /blog/buying-used-machinery-playbook, /blog/used-enclosed-cargo-trailer-for-sale-buying-guide, /blog/used-pressure-washer-trailer-for-sale, /blog/used-dumping-trailer-for-sale-inspection-pricing-guide.
6. **Landing /sell-equipment: Shows real inventory or numbers** (+0.78). 0 listing links
   Prompt: In AIE-Solutions/Marketplace (apps/web), follow MESSAGING.md: Show live listing cards or a same-day number from the admin digest on /sell-equipment.
7. **Landing /dealers: Shows real inventory or numbers** (+0.63). 0 listing links
   Prompt: In AIE-Solutions/Marketplace (apps/web), follow MESSAGING.md: Show live listing cards or a same-day number from the admin digest on /dealers.
8. **SEO and GEO: No internal link is broken or redirects** (+0.5). 1 broken or redirecting internal links
   Prompt: In AIE-Solutions/Marketplace (apps/web): Point the broken or redirecting internal links straight at the final 200 URL. Start with: /listing/cmqrbcz12000nmy3a6tavw2s0.
9. **SEO and GEO: Articles use question headings** (+0.5). 5 of 6 sampled articles
   Prompt: In AIE-Solutions/Marketplace (apps/web): Rewrite at least two H2s per article as the question a buyer would ask (agents/BLOG-WRITER-PROMPT.md in yardswaps-media). Start with: /blog/used-box-truck-gvwr-cdl-usdot-rules.
10. **Landing /pricing: Leads with the storefront** (+0.39)
   Prompt: In AIE-Solutions/Marketplace (apps/web), follow MESSAGING.md: Lead /pricing with "Open your storefront." (MESSAGING.md, dealers).

## SEO and GEO checks

| Pillar | Check | Points | Detail |
|---|---|---|---|
| crawl | Sitemap pages answer 200 with no indexing error | 10/10 | 449 of 449 pages clean |
| crawl | robots.txt answers and names the sitemap | 3/3 | ok |
| crawl | Every sitemap URL has a lastmod date | 2.95/3 | 441 of 449 |
| crawl | Indexable pages linked on the site are in the sitemap | 1.52/4 | 31 indexable pages linked but not submitted |
| crawl | No internal link is broken or redirects | 4.5/5 | 1 broken or redirecting internal links |
| onpage | Titles 30-61 characters | 4.83/5 | 15 out of range |
| onpage | Meta descriptions 70-160 characters | 4.96/5 | 4 out of range |
| onpage | Titles and descriptions are unique | 3.82/4 | 4 pages share a title or description |
| onpage | Exactly one H1 per page | 4/4 | 449 of 449 |
| onpage | At least 600 characters of server-rendered text | 4/4 | 0 thin pages |
| onpage | Images have alt text | 3/3 | 0 of 161 sampled images without alt |
| geo | JSON-LD parses on every page | 4/4 | 0 pages with JSON-LD that does not parse |
| geo | Listing Product markup has what Google needs (image, offer) | 4.93/5 | 2 of 137 listings missing a Product field |
| geo | Home page has Organization and WebSite markup | 3/3 | Organization, WebSite, FAQPage |
| geo | llms.txt describes the site with links | 3/3 | 52 links |
| geo | Answer engines may read the site (robots.txt) | 3/3 | none blocked |
| geo | Articles use question headings | 2.5/3 | 5 of 6 sampled articles |
| geo | Article markup has a date and an author | 0.33/2 | 1 of 6 |
| geo | Articles open with takeaways or carry an FAQ | 2/2 | 6 of 6 |
| tech | HTML under 500 KB (uncompressed) | 2.4/5 | 26 of 26 sampled pages heavier; largest 1100 KB |
| tech | Images have width and height | 4/4 | 0 of 161 sampled images unsized |
| tech | lang attribute and viewport meta | 3/3 | 26 of 26 |
| tech | HTTPS with HSTS | 3/3 | ok |
| tech | HTML is compressed | 3/3 | 26 of 26 |
| tech | Share cards (og:title and og:image) | 3.08/4 | 20 of 26 |
| tech | Pages answer in under 800 ms on average | 3/3 | 141 ms average over 26 pages |

## Landing pages

### /: 100/100

| Criterion | Result | Detail |
|---|---|---|
| Says what it is up top (used commercial or industrial equipment) | pass | H1: "The marketplace where tradespeople buy and sell used industrial and commercial e" |
| A clear call to action in the first screen | pass | Browse |
| Says the AI writes the listing from photos | pass |  |
| Shows real inventory or numbers | pass | 25 listing links |
| Contact, privacy and terms are linked | pass | contact, privacy, terms |
| Answers buyer questions (FAQ) | pass |  |
| No banned phrase or category count (copy-rules.json) | pass |  |

### /dealers: 90/100

| Criterion | Result | Detail |
|---|---|---|
| Says who it is for up top (equipment businesses, the storefront) | pass | H1: "Your own storefront on YardSwaps" |
| A clear call to action in the first screen | pass | Browse |
| Says the AI writes the listing from photos | pass |  |
| Shows real inventory or numbers | fail | 0 listing links |
| Contact, privacy and terms are linked | pass | contact, privacy, terms |
| Answers buyer questions (FAQ) | pass |  |
| No banned phrase or category count (copy-rules.json) | pass |  |
| Leads with the storefront | pass |  |
| The founding offer, word for word, no deadline | pass |  |
| Never tells dealers posting is free | pass |  |

### /pricing: 94/100

| Criterion | Result | Detail |
|---|---|---|
| Says who it is for up top (equipment businesses, the storefront) | pass | H1: "Free to list. Pay only for extra reach." |
| A clear call to action in the first screen | pass | Browse |
| Says the AI writes the listing from photos | pass |  |
| Contact, privacy and terms are linked | pass | contact, privacy, terms |
| Answers buyer questions (FAQ) | pass |  |
| No banned phrase or category count (copy-rules.json) | pass |  |
| Leads with the storefront | partial |  |
| The founding offer, word for word, no deadline | pass |  |

### /sell-equipment: 88/100

| Criterion | Result | Detail |
|---|---|---|
| Says what it is up top (used commercial or industrial equipment) | pass | H1: "Sell Your Equipment in Minutes, Pickup Local" |
| A clear call to action in the first screen | pass | Browse |
| Says the AI writes the listing from photos | pass |  |
| Shows real inventory or numbers | fail | 0 listing links |
| Contact, privacy and terms are linked | pass | contact, privacy, terms |
| Answers buyer questions (FAQ) | pass |  |
| No banned phrase or category count (copy-rules.json) | pass |  |
| Sellers hear free listing first | pass |  |

### Against competitors (home pages, shared criteria)

| Site | Score |
|---|---|
| YardSwaps | - |
| Machinery Trader | not reachable (status 0) |
| Equipment Trader | not reachable (status 0) |

## App listings

| Store | Field | Length | Result | Notes |
|---|---|---|---|---|
| App Store | Name | 25/30 | pass |  |
| App Store | Subtitle | 27/30 | pass |  |
| App Store | Keywords | 95/100 | pass |  |
| App Store | Promotional text | 167/170 | pass |  |
| App Store | Description | 3798/4000 | fail | banned by copy-rules.json: "found nothing" (…urs, and a lot of the time we found nothing. So we built a pla…); the first lines (shown before 'more') leave out the AI listing |
| App Store | Screenshots | 5/10 | pass | 5 images |
| Google Play | Title | 25/30 | pass |  |
| Google Play | Short description | 77/80 | pass |  |
| Google Play | Full description | 3926/4000 | pass |  |
| Google Play | Screenshots | 5/8 | pass | 5 images |

Reviews: not read: the stores' review APIs need the owner's App Store Connect / Play Console keys.

