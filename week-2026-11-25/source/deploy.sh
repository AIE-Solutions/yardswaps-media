#!/bin/bash
# deploy.sh n1 n2 ... : copy a rendered Short (four sizes, silent twins, covers) into the project assets, the Reels
# library and the review page previews; keep final/<id>-16x9.mp4 (silent) for compile.py, delete the rest.
cd "$(dirname "$0")"; C=/mnt/project-files/yardswaps-campaign/assets/motion; M=/home/claude/yardswaps-media/reels/library
P=/tmp/claude-0/-home-claude/765b8cd9-b345-549d-b9fa-6b192160c528/scratchpad/page/v
source <(grep "^declare -A ID" batch18.sh)
for n in "$@"; do id=${ID[$n]}; f=final/yardswaps-$id
  for s in 9x16 4x5 1x1 16x9 16x9-music; do [ -f $f-$s.mp4 ] || { echo "MISSING $f-$s.mp4"; exit 1; }; done
  cp $f-9x16.mp4 $f-4x5.mp4 $f-1x1.mp4 $f-16x9.mp4 $f-16x9-music.mp4 $C/
  cp final/silent/yardswaps-$id-9x16.mp4 final/silent/yardswaps-$id-4x5.mp4 final/silent/yardswaps-$id-1x1.mp4 $C/silent/
  cp final/covers/yardswaps-$id-9x16.jpg $C/thumbnails/yardswaps-$id-cover-reels-9x16.jpg
  cp final/covers/yardswaps-$id-4x5.jpg $C/thumbnails/yardswaps-$id-cover-feed-4x5.jpg
  cp final/covers/yardswaps-$id-16x9.jpg $C/thumbnails/yardswaps-$id-cover-youtube-16x9.jpg
  [ -f $M/yardswaps-$id-9x16.mp4 ] && cp $f-9x16.mp4 $M/
  for s in 9x16 16x9-music; do [ -f $P/yardswaps-$id-$s.mp4 ] && cp $f-$s.mp4 $P/; done
  rm -f $f-9x16.mp4 $f-4x5.mp4 $f-1x1.mp4 $f-16x9-music.mp4 final/silent/yardswaps-$id-*.mp4
  echo "deployed $n $id"
done
