#!/bin/bash
# "Viral format" storefront ad, about 12 s: hook text on screen from frame 0, hard cuts on the beat of the 124 bpm track,
# big centred captions that pop in, slow push on every shot, the real storefront on a phone, end card.
# Optional: SPEED_FULL / SPEED_BAND play the clips faster (2 = twice the camera travel per shot), TAG names the outputs.
# viral4: BT=0.5 (the 120 bpm ElevenLabs bed), the live /dealers screen after the storefront phone (s6b),
# and a sound mix (gravel steps under the opener, a whoosh on each cut, a tap when a screen appears). VO=<mp3> adds a voiceover.
# Usage: RATIO=9x16-paid|4x5|1x1 build-viral4.sh <clipdir with y1 y2 (9:16) and a b c (4:3)> <out dir (default out-viral)>
set -e
B=$(cd "$(dirname "$0")" && pwd); C=${1:?clipdir}; O=${2:-$B/out-viral}; mkdir -p "$O"; cd "$O"
RATIO=${RATIO:-9x16-paid}; A=$B/vr-$RATIO; M=${MUSIC:-$B/../../music/v4/yardswaps-music-storefront-120bpm.mp3}; TAG=${TAG:-viral4}; FX=$B/../../music/v4/sfx
read H PX PY PW PH < <(python3 -c "import json;z=json.load(open('$A/phone.json'));p=z['phone'];print(z['H'],p['x'],p['y'],p['w'],p['h'])")
read CAPY BANDY CAPBANDY < <(python3 -c "import json;z=json.load(open('$A/viral.json'));print(z['capY'],z['bandY'],z['capBandY'])")
N="fps=30,format=yuv420p,setsar=1"; GRADE="eq=saturation=1.03:contrast=1.03:brightness=0.01"
BT=${BT:-0.5}; b() { python3 -c "print(round($1*$BT,3))"; }
D1=$(b 3); D2=$(b 2); D6=$(b ${B6:-6}); D6B=$(b ${B6B:-3}); D7=$(b ${B7:-6})
POP="format=rgba,scale=w='trunc(iw*(1+0.18*max(0,1-t/0.12))/2)*2':h=-2:eval=frame"
# full-frame shot from a vertical clip: cover, slow push, caption pops in centred, wordmark + AI label from frame 0
full() { # <clip> <dur> <cap.png> <label.png> <out>
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$3" -loop 1 -i $A/brand.png -loop 1 -i "$4" -filter_complex \
   "[0:v]setpts=PTS/${SPEED_FULL:-1},scale=1080:$H:force_original_aspect_ratio=increase,crop=1080:$H,scale=w='trunc(1080*(1+0.07*t/$2)/2)*2':h=-2:eval=frame,crop=1080:$H,$GRADE,$N[a];\
    [1:v]$POP[c];[2:v]format=rgba[b];[3:v]format=rgba[l];\
    [a][c]overlay=x='(W-w)/2':y='$CAPY-h/2':shortest=1[v1];[v1][b]overlay=0:0:shortest=1[v2];[v2][l]overlay=0:0:shortest=1,$N[v]" \
   -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$5"
}
# 4:3 shot (real unit, whole machine in frame): blurred cover behind, the clip as a 1080-wide band with a slow push, caption near it
band() { # <clip> <dur> <cap.png> <out>
  # band height follows the clip (a clip cropped free of photo padding is wider than 4:3), capped at 810, centred in the 810 slot
  local BH; BH=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$1" | python3 -c "import sys;w,h=map(int,sys.stdin.read().split(','));print(min(810,2*round(1080*h/w/2)))")
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$3" -loop 1 -i $A/brand.png -filter_complex \
   "[0:v]setpts=PTS/${SPEED_BAND:-1},split[s0][s1];[s0]scale=1080:$H:force_original_aspect_ratio=increase,crop=1080:$H,boxblur=40:8,eq=brightness=-0.08:saturation=0.9,$N[bg];\
    [s1]scale=w='trunc(1080*(1+0.06*t/$2)/2)*2':h=-2:eval=frame,crop=1080:$BH,$GRADE,$N[bd];\
    [1:v]$POP[c];[2:v]format=rgba[b];\
    [bg][bd]overlay=0:$BANDY+(810-$BH)/2:shortest=1[a];[a][c]overlay=x='(W-w)/2':y='$CAPBANDY-h/2':shortest=1[v1];[v1][b]overlay=0:0:shortest=1,$N[v]" \
   -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$4"
}
full "$C/y1.mp4" $D1 $A/cap1.png $A/${AILABEL:-blank}.png s1.mp4
full "$C/y2.mp4" $D2 $A/cap2.png $A/${AILABEL:-blank}.png s2.mp4
band "$C/a.mp4" $D2 $A/cap3.png s3.mp4
band "$C/b.mp4" $D2 $A/cap4.png s4.mp4
band "$C/c.mp4" $D2 $A/cap5.png s5.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/stage-store.png -i ${REC:-$B/rec/storefront-8s.mp4} -loop 1 -framerate 30 -i $A/phone-mask.png -filter_complex \
   "[1:v]scale=$PW:$PH,format=rgba[p];[2:v]format=gray[m];[p][m]alphamerge[pm];[0:v][pm]overlay=$PX:$PY:shortest=1,$N[v]" -map "[v]" -t $D6 -an -c:v libx264 -crf 16 -preset medium s6.mp4
# s6b: the live /dealers page (real screen, cut above the price row), slow push, pops in
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/stage-dealers.png -vf "scale=w='trunc(1080*(1+0.04*t/$D6B)/2)*2':h=-2:eval=frame,crop=1080:$H,$N" -t $D6B -c:v libx264 -crf 16 -preset medium s6b.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/${ENDCARD:-endcard.png} -vf "fade=in:d=0.15,$N" -t $D7 -c:v libx264 -crf 16 -preset medium s7.mp4
ffmpeg -hide_banner -loglevel error -y $(for i in 1 2 3 4 5 6 6b 7; do echo -i s$i.mp4; done) -filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v]concat=n=8:v=1:a=0,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 20 -preset slow video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4); FO=$(python3 -c "print(round($D-1.5,2))")
case "$RATIO" in 4x5) DEF=yardswaps-storefront-$TAG-paid-4x5.mp4 ;; 1x1) DEF=yardswaps-storefront-$TAG-paid-1x1.mp4 ;; *) DEF=yardswaps-storefront-$TAG-paid-9x16.mp4 ;; esac
OUT=${OUT:-$DEF}
# cut times in ms: whoosh lands 0.12 s before each hard cut between yard shots, tap when the phone and the /dealers screen appear
ms() { python3 -c "print(int(round(($1)*1000)))"; }
C1=$(ms "$D1-0.12"); C2=$(ms "$D1+$D2-0.12"); C3=$(ms "$D1+2*$D2-0.12"); C4=$(ms "$D1+3*$D2-0.12"); T1=$(ms "$D1+4*$D2"); T2=$(ms "$D1+4*$D2+$D6")
VOIN=""; VOMIX=""; NIN=5
if [ -n "$VO" ]; then VOIN="-i $VO"; VOMIX="[6:a]adelay=${VO_DELAY:-300}|${VO_DELAY:-300},volume=${VO_VOL:-1.0}[vo];"; NIN=6; fi
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -i "$M" -i $FX/gravel-steps.mp3 -i $FX/whoosh.mp3 -i $FX/tap.mp3 -i $FX/tap.mp3 $VOIN -filter_complex \
 "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,afade=t=out:st=$FO:d=1.5,volume=${MUSIC_VOL:-1.0}[m];\
  [2:a]atrim=0:$D1,afade=t=out:st=$(python3 -c "print($D1-0.3)"):d=0.3,volume=1.6[g];\
  [3:a]asplit=4[w1][w2][w3][w4];[w1]adelay=$C1|$C1,volume=0.35[x1];[w2]adelay=$C2|$C2,volume=0.35[x2];[w3]adelay=$C3|$C3,volume=0.35[x3];[w4]adelay=$C4|$C4,volume=0.35[x4];\
  [4:a]adelay=$T1|$T1,volume=0.5[t1];[5:a]adelay=$T2|$T2,volume=0.5[t2];$VOMIX\
  [m][g][x1][x2][x3][x4][t1][t2]$( [ -n "$VO" ] && echo "[vo]")amix=inputs=$( [ -n "$VO" ] && echo 9 || echo 8):normalize=0:duration=first,\
  acompressor=threshold=-24dB:ratio=2.5:attack=15:release=300:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9,atrim=0:$D[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
echo "$OUT $RATIO duration $D"
