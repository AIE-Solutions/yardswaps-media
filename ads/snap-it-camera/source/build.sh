#!/bin/bash
# "Snap it, camera" ad. Usage: build.sh [out dir]  (both sizes; ~3 min)
# Opener: the real listing photo in a phone camera screen (handheld drift <=1.035x, focus tap, shutter), pulled back
# into the phone of the real sell-flow recording of that same photo (motion/silent/yardswaps-pressure-washer-replaced-*.mp4,
# 5.8-13.9 s), end card, music bed + SFX from the ElevenLabs kit (grant, nothing bought).
set -e
B=$(cd "$(dirname "$0")" && pwd); O=${1:-$B/out}; mkdir -p "$O"; T=$(mktemp -d)
P=/mnt/project-files/yardswaps-campaign; E=$P/assets/elevenlabs; MUS=$E/music/yardswaps-music-punch-124bpm.mp3
python3 $B/endcard.py $B/fonts $T/endcard.png
python3 -c "from PIL import Image; Image.open('$T/endcard.png').crop((0,430,1080,1510)).save('$T/endcard-1x1.png')"
for R in 9x16 1x1; do
  mkdir -p $T/fr-$R
  ffmpeg -loglevel error -y -ss 4.0 -t 10.2 -i $P/assets/motion/silent/yardswaps-pressure-washer-replaced-$R.mp4 -vf fps=30 $T/fr-$R/%04d.png
  RATIO=$R python3 $B/render.py $T/fr-$R $B/photos/hotsy-pressure-washer.jpg $B/fonts $T/raw-$R.mp4
  EC=$T/endcard.png; [ $R = 1x1 ] && EC=$T/endcard-1x1.png
  bash $B/assemble.sh $T/raw-$R.mp4 $EC $MUS $E/sfx $O/yardswaps-snap-it-camera-$R.mp4
done
python3 $B/wordsheet.py $O/yardswaps-snap-it-camera-9x16.mp4 $O/words-vs-screen.jpg
