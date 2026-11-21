# How to use YardSwaps, v3 (website walkthrough, Nov 21 2026)

Replaces the silent Oct 2 video on yardswaps.com/how-it-works once Alan approves
and the "Storefront plan" rename (app PR #438) is merged. Earlier versions stay
where they are; nothing was deleted.

- `yardswaps-how-it-works-v3.mp4`: 1920x1080, 30 fps, 2:05, H.264 + AAC, -16 LUFS
- `yardswaps-how-it-works-v3.jpg`: poster, 1280x720
- `yardswaps-how-it-works-v3.en.vtt`: captions (one cue per spoken sentence)
- `timeline.json`: segment and voice start times; the site's chapter starts come from here

Voice: Justin Case (ElevenLabs, voice DtQLDxHbTiQTpVVanTy1, eleven_v4), lines in
`narration/how-it-works-v3/lines.tsv`, made by the narration workflow.
Music: `music/v2/yardswaps-music-lofi-90bpm.mp3` (ElevenLabs Music, Nov 15), looped and ducked under the voice.

## Remaking it
1. Record: Expo web on :8081 with the mocked API, `MOCK=./mockwt node recwt.js sell|buy|store`
   (source/rec; needs the Hotsy photos and the scratch recording setup from the Motion thread).
   The hero listing is the real Hotsy listing photo plus a close-up crop of its brand decal for the label tip.
2. `python3 source/build.py` composes the frames (phone + headline + magnified callouts + tap rings),
   one segment per voice line; a segment is never shorter than its line, clips play at 1x, only pauses are cut.
3. `python3 source/mix.py` adds voice + music and writes the captions.

Rules applied: same real item start to finish, whole item in frame, slow pace, words match the
screen, no category count, no promise of views or sales, storefront offer without a deadline.
