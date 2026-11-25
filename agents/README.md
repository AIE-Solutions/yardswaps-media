# Agent prompts (canonical copies)

The shared project folder (/mnt/project-files/yardswaps-campaign/growth-loop/) is at its storage cap and silently lost prompt edits on 2026-11-20. The prompts below are the canonical versions. If a project-file copy differs or looks cut off, this repo wins. Agents read these with the GitHub tools (AIE-Solutions/yardswaps-media, branch main).

| File | Agent | Schedule (Central) |
|---|---|---|
| PLATFORM-OPS-PROMPT.md | Platform Ops: daily health, safety and routing | 3:37 am daily |
| REPLY-HANDLER-ADMIN-STEPS.md | Reply Handler steps 9 to 11: admin follow-ups and the daily posting-rules review (steps 1 to 8 stay in the project file) | 12:17 + 5:17 pm daily |
| BLOG-WRITER-PROMPT.md | Blog writer: one article a day for yardswaps.com/blog through the agent blog API (our HeyCatch blog replacement) | 10:20 am daily |

Owner: Growth Lead thread. Edit here by PR; never put secrets or keys in these files.

Words (Alan 11-21, "consistency is key"): the paid plan is the "Storefront plan", never "Dealer plan"; its boosts are "Storefront boosts" and its trial is the "storefront trial". Say "storefront" for the product. Use "dealer" only for who it is for ("storefronts for dealers"), plus the buyer-facing "Dealer" chip and "Verified Dealer" badge, which keep their names. Links and ids stay as they are (/account/dealer?start=1, /dealers, dealer_monthly). Every new agent prompt carries this line.

Message (Alan 11-21, "a clear precise message"): every line a seller, dealer or buyer reads follows MESSAGING.md at the root of this repo (AIE-Solutions/yardswaps-media, main): the one-line pitch, what each audience hears, the offer word for word, the word list and the do/don't rules. Read it before writing any copy; it wins over older copy notes. Every new agent prompt carries this line too.

End card (Alan 11-25): every video we make or post ends on the YardSwaps end card in brand/endcard/ of this repo (blue card, wordmark, App Store and Google Play badges, link; about 2 seconds). Storefront clips use the storefront version, never the "Free to list" one. Run `python3 brand/endcard/endcard.py add IN.mp4 OUT.mp4 [seller|dealer]` on anything you cut; the Reels, TikTok and Shorts posters skip a clip without it. Every new agent prompt that makes or posts video carries this line.
