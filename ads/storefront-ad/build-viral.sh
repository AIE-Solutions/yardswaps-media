#!/bin/bash
# "Viral format" storefront ad, about 12 s: hook text on screen from frame 0, hard cuts on the beat of the 124 bpm track,
# big centred captions that pop in, slow push on every shot, the real storefront on a phone, end card.
# Usage: RATIO=9x16-paid|4x5|1x1 build-viral.sh <clipdir with y1 y2 (9:16) and a b c (4:3)> <out dir (default out-viral)>
set -e
B=$(cd "$(dirname "$0")" && pwd); C=${1:?clipdir}; O=${2:-$B/out-viral}; mkdir -p "$O"; cd "$O"
RATIO=${RATIO:-9x16-paid}; A=$B/vr-$RATIO; M=${MUSIC:-$B/../../music/v2/yardswaps-music-road-124bpm.mp3}; TAG=${TAG:-viral}
read H PX PY PW PH < <(python3 -c "import json;z=json.load(open('$A/phone.json'));p=z['phone'];print(z['H'],p['x'],p['y'],p['w'],p['h'])")
read CAPY BANDY CAPBANDY < <(python3 -c "import json;z=json.load(open('$A/viral.json'));print(z['capY'],z['bandY'],z['capBandY'])")
N="fps=30,format=yuv420p,setsar=1"; GRADE="eq=saturation=1.03:contrast=1.03:brightness=0.01"
BT=0.48387; b() { python3 -c "print(round($1*$BT,3))"; }
D1=$(b 3); D2=$(b 2); D6=$(b 8); D7=$(b 6)
POP="format=rgba,scale=w='trunc(iw*(1+0.18*max(0,1-t/0.12))/2)*2':h=-2:eval=frame"
# full-frame shot from a vertical clip: cover, slow push, caption pops in centred, wordmark + AI label from frame 0
full() { # <clip> <dur> <cap.png> <label.png> <out>
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$3" -loop 1 -i $A/brand.png -loop 1 -i "$4" -filter_complex \
   "[0:v]scale=1080:$H:force_original_aspect_ratio=increase,crop=1080:$H,scale=w='trunc(1080*(1+0.07*t/$2)/2)*2':h=-2:eval=frame,crop=1080:$H,$GRADE,$N[a];\
    [1:v]$POP[c];[2:v]format=rgba[b];[3:v]format=rgba[l];\
    [a][c]overlay=x='(W-w)/2':y='$CAPY-h/2':shortest=1[v1];[v1][b]overlay=0:0:shortest=1[v2];[v2][l]overlay=0:0:shortest=1,$N[v]" \
   -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$5"
}
# 4:3 shot (real unit, whole machine in frame): blurred cover behind, the clip as a 1080-wide band with a slow push, caption near it
band() { # <clip> <dur> <cap.png> <out>
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$3" -loop 1 -i $A/brand.png -filter_complex \
   "[0:v]split[s0][s1];[s0]scale=1080:$H:force_original_aspect_ratio=increase,crop=1080:$H,boxblur=40:8,eq=brightness=-0.08:saturation=0.9,$N[bg];\
    [s1]scale=w='trunc(1080*(1+0.06*t/$2)/2)*2':h=-2:eval=frame,crop=1080:810,$GRADE,$N[bd];\
    [1:v]$POP[c];[2:v]format=rgba[b];\
    [bg][bd]overlay=0:$BANDY:shortest=1[a];[a][c]overlay=x='(W-w)/2':y='$CAPBANDY-h/2':shortest=1[v1];[v1][b]overlay=0:0:shortest=1,$N[v]" \
   -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$4"
}
full "$C/y1.mp4" $D1 $A/cap1.png $A/ai.png s1.mp4
full "$C/y2.mp4" $D2 $A/cap2.png $A/ai.png s2.mp4
band "$C/a.mp4" $D2 $A/cap3.png s3.mp4
band "$C/b.mp4" $D2 $A/cap4.png s4.mp4
band "$C/c.mp4" $D2 $A/cap5.png s5.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/stage-store.png -i ${REC:-$B/rec/storefront-8s.mp4} -loop 1 -framerate 30 -i $A/phone-mask.png -filter_complex \
   "[1:v]scale=$PW:$PH,format=rgba[p];[2:v]format=gray[m];[p][m]alphamerge[pm];[0:v][pm]overlay=$PX:$PY:shortest=1,$N[v]" -map "[v]" -t $D6 -an -c:v libx264 -crf 16 -preset medium s6.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/endcard.png -vf "fade=in:d=0.15,$N" -t $D7 -c:v libx264 -crf 16 -preset medium s7.mp4
ffmpeg -hide_banner -loglevel error -y $(for i in 1 2 3 4 5 6 7; do echo -i s$i.mp4; done) -filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v]concat=n=7:v=1:a=0,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 20 -preset slow video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4); FO=$(python3 -c "print(round($D-1.5,2))")
case "$RATIO" in 4x5) DEF=yardswaps-storefront-$TAG-paid-4x5.mp4 ;; 1x1) DEF=yardswaps-storefront-$TAG-paid-1x1.mp4 ;; *) DEF=yardswaps-storefront-$TAG-paid-9x16.mp4 ;; esac
OUT=${OUT:-$DEF}
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -stream_loop -1 -i "$M" -filter_complex "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,afade=t=in:d=0.2,afade=t=out:st=$FO:d=1.5,acompressor=threshold=-28dB:ratio=2.5:attack=20:release=400:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=9[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
echo "$OUT $RATIO duration $D"
