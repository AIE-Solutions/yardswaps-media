# "Every shop has one" v2 (9:16, 35.3 s)

The improved cut of the brand commercial, for organic Reels, Shorts, TikTok and YouTube. Not a paid ad. Music only, no voice. Made on the ElevenLabs startup grant with no spend.

| Time | Shot | Line on screen |
|---|---|---|
| 0.0-3.0 | Row of trade shops at sunrise, one bay door glowing | Every shop has one. |
| 3.0-5.6 | Unplugged fryer in a restaurant back room | The fryer from the old menu. |
| 5.6-8.3 | Two generators, the older one half-tarped behind, bird on top | The backup for the backup. |
| 8.3-11.0 | MIG welder used as a shelf | The welder that became a shelf. |
| 11.0-13.6 | The Hotsy washer in a corner, a bigger newer washer behind it | The washer the bigger one replaced. |
| 13.6-21.2 | Clean iPhone walkthrough: the real app lists that same Hotsy in a big phone, near real speed | Snap the washer. Hose and all. / The app writes the listing. / Set a price. Post it free. |
| 20.9-24.7 | Handshake next to the Hotsy, the buyer takes the handle | Someone close by needed it. |
| 24.4-27.5 | The swept empty spot with wheel marks | You get the space back. |
| 27.2-30.8 | Gloved hand fueling a work pickup at golden hour | And extra cash flow for the business. |
| 30.5-35.3 | Light end card: wordmark, "Every shop has one. List it free.", store badges, yardswaps.com | |

What changed from v1:
- Every scene re-shot as a crisp full-frame keyframe (Nano Banana Pro, 9:16 2K) and then animated with Veo 3.1 start frame, locked off. No letterbox, no dark shots, no made-up badges, no passers-by.
- The Hotsy scene is generated from the real listing photo, so the same washer appears in its scene, in the app and in the handshake.
- New beats: a buyer handshake on the music lift, and the fuel-up "extra cash flow" close.
- On-screen lines are Space Grotesk Bold 88 px, lower-left with a blue bar, about 3x the v1 size, kept clear of the Reels/TikTok bottom UI.
- 0.3 s dissolves between every shot; new instrumental (ElevenLabs Music v2.5, take B) that lifts at about 20 s, normalized to -14 LUFS.

iPhone walkthrough cleanup (Alan, Nov 14: "The iPhone walkthrough needs to be cleaned up"):
- Fresh recording of the real app (Expo web, 1179x2334) listing the real Hotsy photo: choose the photo, the AI fills title and category, type 1200, publish, "Your listing is live!".
- Shown in one big phone on light gray, with one two-line caption per step above it. No pop-up callout cards, no word-by-word captions, no 2x speed-up; the AI wait is cut with crossfades instead.
- Walkthrough alone: `iphone-walkthrough-clean-9x16.mp4` (7.6 s).

Rules checked: idle gear only, nothing running or driving. No real app screen redrawn. The trailer plate in the handshake is blurred. Generated people only, no real users. No AI label on the video, so turn on each platform's AI-content toggle when posting.

Sources: ElevenLabs flow 22NMjd5hLj8O4e90WoQ5; clips and music in `narration/brand-commercial-v2/`.
Rebuild:
1. Record: `source/recording/rec_clean.js` (needs lib.js, mock.js, listings.js and hotsy-scan.json from the campaign's video-upgrade recording kit, the app running on Expo web at :8081, and the Hotsy photo as hotsy.jpg). Run `SCANF=hotsy-scan.json UPIMG=r-hotsy.jpg node rec_clean.js`; frames land in raw/clean.
2. Walkthrough: `source/walk.sh raw/clean walk.mp4` (phone and captions from `source/phone.py`; frame ranges for each step are at the top of walk.sh).
3. Commercial: `source/build.sh narration/brand-commercial-v2 narration/brand-commercial-v2/music-b.mp3 walk.mp4` (captions from `source/captions.py`).
