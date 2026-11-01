# Reels to Instagram and Facebook

Free, automatic Reels for @yardswaps (Instagram) and the YardSwaps Facebook Page, posted by GitHub Actions (free for this public repo) through Meta's own API. No scheduler subscription, no Zapier tasks, nothing on anyone's computer.

## What it does
- Two Reels a day on each platform: 7:00 am and 4:30 pm Central in winter (8:00 am and 5:30 pm in summer, since GitHub's clock is UTC). HeyCatch posts at about 4:30 am, 12:30 pm and 8:30 pm Central, so these slots stay 2+ hours clear. Before posting, the script also checks the last posts on each account and skips that slot if anything went up in the last 90 minutes.
- Picks the next video from `library.json`: videos never posted on that platform first (newest first), then the one posted longest ago. The same video never goes out twice on a platform within 10 days. On Instagram a repeat goes out as a Trial Reel (shown to non-followers first, shared to followers only if it does well), so followers don't see reruns.
- Uploads the file from `library/` directly, builds the caption and writes the result to `posted.json` (time, platform, video, post id, link).
- Safety cap: at most 2 of our Reels per platform in any 20 hours.

## Captions (built by `post_reels.py` from each video's `body`, `question`, `ig_tags`)
- Instagram: body, the question + "Tell us in the comments.", "Link in bio." (bio carries yardswaps.com/i), up to 5 hashtags.
- Facebook: body, the question, "List it free: https://www.yardswaps.com/sell-equipment?utm_source=facebook&utm_medium=social&utm_campaign=reels_<slug>", 3 hashtags.
- Rules (CAPTIONS.md, ENGAGEMENT-PLAYBOOK.md, UTM-LINKS.md in the campaign folder): seller-first, the body says "Free to list" and "Free boosts", plain words, no emoji or icons, one open question about the viewer's own gear, never promise views or sales, posted as the business. No #smallbusiness, #fyp, #reels, #explore.

## Adding new videos (weekly batch)
For each new 9:16 video with music:
1. Copy it to `reels/library/yardswaps-<slug>-9x16.mp4` (keep files under ~15 MB; Reels must be 3 to 60 seconds for Facebook).
2. Add an entry to `library.json`: `slug`, `file`, `priority` (0 = first), `added` (YYYY-MM-DD, today), `body` (seller text ending with a "Free to list ... Free boosts." line), `question` (from the comment prompt bank, not used before), `ig_tags`.
3. Commit to `main`. Newest `added` posts first.
Never delete `reels/` when clearing a week folder.

## Manual run
Actions tab > "Reels to Instagram and Facebook" > Run workflow. `dry_run` = 1 shows the pick and both captions without posting; `slug` forces a video; `platforms` can be just `instagram` or `facebook`.

## One-time setup (Alan, about 10 minutes, all free)
The workflow needs one Page access token, saved as the repo secret `META_PAGE_TOKEN`. Until it exists every run logs "not set yet" and posts nothing.
1. On the PC, in Chrome logged in to the Facebook account that manages the YardSwaps Page, open https://developers.facebook.com/apps and click **Create app** (accept the developer terms if asked).
2. Name `YardSwaps Reels`, contact email yardswaps@gmail.com. Use cases: tick **Manage everything on your Page** and **Manage messaging & content on Instagram** (if the screen instead asks for an app type, pick **Business**). Skip connecting a business portfolio. Create the app.
3. Open https://developers.facebook.com/tools/explorer/ . Meta App: **YardSwaps Reels**. Under Permissions add: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `business_management`. Click **Generate Access Token**, and in the Facebook window choose the YardSwaps Page and the @yardswaps Instagram account, then Continue/Save.
4. Back in the Explorer, in **User or Page** pick **YardSwaps** (the Page, not "Sunfire Corals"). The token box now holds a Page token.
5. Click the blue **i** next to the token > **Open in Access Token Tool** > **Extend Access Token** at the bottom. Copy the new token. (The token set on 2026-11-01 shows an expiry around Dec 31 2026, so it has to be renewed: see Renewal below.)
6. Open https://github.com/AIE-Solutions/yardswaps-media/settings/secrets/actions/new , Name `META_PAGE_TOKEN`, paste the token as the Secret, **Add secret**.
7. In the app's dashboard: App settings > Basic, Privacy Policy URL `https://www.yardswaps.com/privacy`, Category Business, Save. Then switch the app to **Live** (the "Publish" / App Mode toggle at the top) so posts are public.
Then tell the project thread "token added": it runs one test post to each platform.

## Renewal
Current token: Page token for page 1291163214083476 from Meta app "YardSwaps Reels" (id 2302671600666026), set 2026-11-01, expires about 2026-12-31. Every run checks the expiry: under 14 days left it adds a warning to the run summary, and under 7 days the run fails so GitHub emails the repo admin (it still posts that run). To renew, redo steps 3 to 6 and replace the secret. The token also stops early if the Facebook password changes, the app is removed, or the account loses admin of the Page.
