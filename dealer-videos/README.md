# Dealer inventory videos

Every Dealer plan on YardSwaps includes one short video a month of one of the
dealer's real listings (one during the free trial, then one per calendar month
once paid). The app decides who is due, picks the listing and writes the script
from the listing's own facts (`apps/web/lib/dealer-videos.ts` in the
Marketplace repo). This folder is the worker that makes the video.

`render.py`, run by `.github/workflows/dealer-videos.yml` every 3 hours:

1. `POST /api/dealer-videos/worker/claim` with `Authorization: Bearer
   DEALER_VIDEO_WORKER_SECRET` queues anything due and returns one job (or
   `job: null`).
2. Downloads up to 6 of the listing's photos, drops any with a face, blurs
   number-like text (plates, phone and street numbers).
3. Voices each script line with ElevenLabs text-to-speech, voice "Justin
   Case", model `eleven_multilingual_v2` (generally available: output we
   sell never comes from a beta model). About 150 characters a video.
4. Screenshots the dealer's public storefront for the end card.
5. Renders 1080x1920 at 30 fps: the whole item fitted over a blurred copy of
   the same photo, a slow push in that never passes 1.035x, one caption per
   spoken line (Space Grotesk, slate, the price line in blue), the storefront
   end card, a track from `music/trend` (ours, made with ElevenLabs Music)
   kept low. No AI label on the video; the dealer uses each platform's AI
   toggle when they post it.
6. Uploads through `/worker/<id>/upload` (a presigned POST) and reports to
   `/worker/<id>/complete`. The app checks the file, marks it ready and
   emails the dealer, who adds it to the listing in one tap.

A failed render is reported and retried up to 3 times. The log shows job and
listing ids only; the job carries no contact details.

The voice never speaks as a buyer or as the dealer and never promises views
or sales: it reads the listing's title, hours or miles, price, place and the
dealer's name.

## Switching it on

Two secrets, both typed in by Alan:

- Railway, web service: `DEALER_VIDEO_WORKER_SECRET` = a long random value.
- This repo, Settings > Secrets > Actions: `DEALER_VIDEO_WORKER_SECRET` = the
  same value. `ELEVENLABS_API_KEY` is already set.

Without them every run stops at its first step.

## Local test

    python3 dealer-videos/render.py --sample <folder of .jpg>

renders `dealer-videos/out/sample.mp4` with a sample script (silent voice
unless `ELEVENLABS_API_KEY` is set). Needs ffmpeg, opencv-python-headless,
pillow, numpy; tesseract and playwright are optional.
