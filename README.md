# YardSwaps media

- `MESSAGING.md`: the one-page messaging guide. Every post, caption, ad, email and agent prompt follows it.
- `reels/`: the Reels library and the free daily poster for Instagram and Facebook (see reels/README.md). Keep this folder; never delete it when clearing a week.
- `week-YYYY-MM-DD/`: that week's YouTube files, read by raw URL. Each Monday batch replaces last week's folder.
- Agent PRs (`claude/*` branches) merge on their own once marked ready for review and every check passes (`.github/workflows/agent-automerge.yml`). Labels `needs-approval`, `hold` or `do-not-merge` stop it; PRs that change `.github/workflows/` still need a manual merge.
