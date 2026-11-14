# "Every shop has one" v2 (9:16, 34.5 s)

The improved cut of the brand commercial, for organic Reels, Shorts, TikTok and YouTube. Not a paid ad. Music only, no voice. Made on the ElevenLabs startup grant with no spend.

| Time | Shot | Line on screen |
|---|---|---|
| 0.0-3.0 | Row of trade shops at sunrise, one bay door glowing | Every shop has one. |
| 3.0-5.6 | Unplugged fryer in a restaurant back room | The fryer from the old menu. |
| 5.6-8.3 | Two generators, the older one half-tarped behind, bird on top | The backup for the backup. |
| 8.3-11.0 | MIG welder used as a shelf | The welder that became a shelf. |
| 11.0-13.9 | The Hotsy washer in a corner, a bigger newer washer behind it | The washer the bigger one replaced. |
| 13.9-20.1 | Real app recording listing that same Hotsy, at 2x | (app captions) |
| 20.1-23.6 | Handshake next to the Hotsy, the buyer takes the handle (music lifts here) | Someone close by needed it. |
| 23.6-26.4 | The swept empty spot with wheel marks | You get the space back. |
| 26.4-29.7 | Gloved hand fueling a work pickup at golden hour | And extra cash flow for the business. |
| 29.7-34.5 | Light end card: wordmark, "Every shop has one. List it free.", store badges, yardswaps.com | |

What changed from v1:
- Every scene re-shot as a crisp full-frame keyframe (Nano Banana Pro, 9:16 2K) and then animated with Veo 3.1 start frame, locked off. No letterbox, no dark shots, no made-up badges, no passers-by.
- The Hotsy scene is generated from the real listing photo, so the same washer appears in its scene, in the app and in the handshake.
- New beats: a buyer handshake on the music lift, and the fuel-up "extra cash flow" close.
- On-screen lines are Space Grotesk Bold 88 px, lower-left with a blue bar, about 3x the v1 size, kept clear of the Reels/TikTok bottom UI.
- 0.3 s dissolves between every shot; new instrumental (ElevenLabs Music v2.5, take B) that lifts at about 20 s, normalized to -14 LUFS.

Rules checked: idle gear only, nothing running or driving. No real app screen redrawn. The trailer plate in the handshake is blurred. Generated people only, no real users. No AI label on the video, so turn on each platform's AI-content toggle when posting.

Sources: ElevenLabs flow 22NMjd5hLj8O4e90WoQ5; clips and music in `narration/brand-commercial-v2/`.
Rebuild: `source/build.sh narration/brand-commercial-v2 narration/brand-commercial-v2/music-b.mp3 <yardswaps-pressure-washer-replaced-9x16.mp4>` (captions from `source/captions.py`).
