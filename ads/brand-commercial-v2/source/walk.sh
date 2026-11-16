#!/bin/bash
# Clean iPhone walkthrough: real app recording in a big phone, one line per step, no pop-ups.
# usage: walk.sh <frames_dir> <out.mp4>
set -e
F=$1; OUT=$2; D=$(dirname $0); T=$(mktemp -d)
seg(){ # name start count
  ffmpeg -y -loglevel error -framerate 30 -start_number $2 -i $F/%04d.jpg -frames:v $3 \
    -vf "scale=744:1474:flags=lanczos,format=yuv420p" -c:v libx264 -crf 14 -r 30 $T/$1.mp4; }
seg A 24 60; seg B 195 80; seg C 372 54; seg D 534 60
du(){ ffprobe -v error -show_entries format=duration -of csv=p=0 $1; }
X=0.3
dA=$(du $T/A.mp4); dB=$(du $T/B.mp4); dC=$(du $T/C.mp4)
o1=$(python3 -c "print(round($dA-$X,3))"); o2=$(python3 -c "print(round($dA+$dB-2*$X,3))"); o3=$(python3 -c "print(round($dA+$dB+$dC-3*$X,3))")
ffmpeg -y -loglevel error -i $T/A.mp4 -i $T/B.mp4 -i $T/C.mp4 -i $T/D.mp4 -filter_complex \
 "[0][1]xfade=transition=fade:duration=$X:offset=$o1[x1];[x1][2]xfade=transition=fade:duration=$X:offset=$o2[x2];[x2][3]xfade=transition=fade:duration=$X:offset=$o3,format=yuv420p" \
 -c:v libx264 -crf 14 $T/screen.mp4
L=$(du $T/screen.mp4)
c1=$o1; c2=$o2  # caption changes at the screen crossfades
ffmpeg -y -loglevel error -loop 1 -i $D/appbg.png -i $T/screen.mp4 -loop 1 -i $D/bezel.png \
 -loop 1 -t $(python3 -c "print($c1+0.3)") -i $D/w1.png \
 -loop 1 -t $(python3 -c "print($c2-$c1+0.3)") -i $D/w2.png \
 -loop 1 -t $(python3 -c "print($L-$c2)") -i $D/w3.png -filter_complex \
 "[0]format=rgba,trim=duration=$L[bg];[bg][1]overlay=168:330:shortest=1[p];[p][2]overlay=0:0[ph];\
  [3]format=rgba,fade=in:st=0:d=0.3:alpha=1,fade=out:st=$c1:d=0.3:alpha=1[w1];\
  [4]format=rgba,fade=in:st=0:d=0.3:alpha=1,fade=out:st=$(python3 -c "print(round($c2-$c1,3))"):d=0.3:alpha=1,setpts=PTS+$c1/TB[w2];\
  [5]format=rgba,fade=in:st=0:d=0.3:alpha=1,setpts=PTS+$c2/TB[w3];\
  [ph][w1]overlay=0:0:eof_action=pass[a];[a][w2]overlay=0:0:eof_action=pass[b];[b][w3]overlay=0:0:eof_action=pass,format=yuv420p[v]" \
 -map "[v]" -t $L -r 30 -c:v libx264 -crf 16 -pix_fmt yuv420p $OUT
rm -rf $T; echo "walk $L s"
