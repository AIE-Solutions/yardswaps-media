#!/bin/bash
# assemble.sh <raw.mp4> <endcard.png> <music.mp3> <sfx dir> <out.mp4>
# raw + 3.6 s end card (0.3 s fade), music bed (-14 LUFS, TP -1.5) and SFX at the on-screen events.
set -e
RAW=$1; EC=$2; MUS=$3; S=$4; OUT=$5; T=$(mktemp -d)
RD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$RAW")
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i "$EC" -vf "fps=30,format=yuv420p,setsar=1" -t 3.6 -c:v libx264 -crf 14 $T/ec.mp4
OFF=$(python3 -c "print(round($RD-0.3,3))")
ffmpeg -hide_banner -loglevel error -y -i "$RAW" -i $T/ec.mp4 -filter_complex "[0:v]setsar=1[a];[a][1:v]xfade=transition=fade:duration=0.3:offset=$OFF,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 19 -preset slow $T/v.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/v.mp4); FO=$(python3 -c "print(round($D-1.6,2))")
# name:time:gain  (focus tap, shutter, pull-back, price tap, publish tap, published)
EV="tap:0.88:0.55 camera-shutter:2.26:0.95 swipe:2.92:0.4 tap:7.82:0.55 tap:8.95:0.55 listing-published:9.12:0.85"
IN=""; FC=""; i=2; MIX="[m]"
for e in $EV; do n=${e%%:*}; r=${e#*:}; t=${r%%:*}; g=${r#*:}; ms=$(python3 -c "print(int($t*1000))")
  IN="$IN -i $S/yardswaps-sfx-$n.wav"; FC="$FC[$i:a]volume=$g,adelay=$ms|$ms[s$i];"; MIX="$MIX[s$i]"; i=$((i+1)); done
N=$((i-1))
ffmpeg -hide_banner -loglevel error -y -i $T/v.mp4 -i "$MUS" $IN -filter_complex \
 "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,volume=0.75,afade=t=in:d=0.25,afade=t=out:st=$FO:d=1.6[m];$FC${MIX}amix=inputs=$N:normalize=0:duration=first,loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.84:level=false[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
cp $T/v.mp4 "${OUT%.mp4}-silent.mp4"
echo "$OUT $D s"
