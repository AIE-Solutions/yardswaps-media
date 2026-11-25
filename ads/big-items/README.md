# "Too big to ship? List it free." (seller ad, Nov 24 2026)

Seller-first ad about listing big, hard-to-ship items across trades: pallet racking,
a walk-in cooler, a condenser, an engine, a conveyor. All five are real YardSwaps
listings (photos from the live listings API, see `src/listings.json`).

- Camera moves: Runway Seedance 2.5 Flash image-to-video on the real listing photo
  (720p, 3:4, no audio). Only the first 1-2.5 s of each clip is used so the whole
  item stays in frame. The cooler clip draws a reflection after ~2 s, so only 0-1.3 s is used.
- Voice: ElevenLabs eleven_v4, voice Justin Case (`audio/vo.mp3`, take A).
- Music: Eleven Music v2.5 via Runway, 20 s instrumental (`audio/music.mp3`), ducked to 0.22.
- App shots: the real app recording (surplus-parts listing flow), never a mock screen.
- End card: light ad-builder look, logo + wordmark + yardswaps.com, no VO.
- Loudness: about -14.4 LUFS integrated, true peak -1.5 dBFS.

Copy follows MESSAGING.md (sellers: list it free, the AI writes the listing, no selling fee).
No category count, no promise of views or sales, no faces or plates.

Build: `python3 build.py 9x16|4x5|1x1` (needs `clips/` from project files).
Outputs: `out/yardswaps-too-big-to-ship-{9x16,4x5,1x1}.mp4`, 15.5 s each.
Project files: `yardswaps-campaign/assets/ads/big-items/`.
