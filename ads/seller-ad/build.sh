#!/bin/bash
# Seller ad (Nov 21 2026), about 16 s: five real new listings with a hard cut on the beat, the real app listing the
# first one (the same Cat 950G photo is the upload), the light end card. Music only, no voice, no AI-generated shots.
# Usage: RATIO=9x16-paid|4x5|9x16-shorts build.sh [out dir]   (run layout.py and apprec.py first)
# 9x16-shorts = the 9x16-paid cut with the end card inside the YouTube Shorts safe box (out/9x16-shorts/endcard.png).
set -e
B=$(cd "$(dirname "$0")" && pwd); RATIO=${RATIO:-9x16-paid}
case "$RATIO" in 9x16-shorts) L=9x16-paid; CARD=$B/out/9x16-shorts/endcard.png ;; *) L=$RATIO; CARD=$B/out/$RATIO/endcard.png ;; esac
A=$B/out/$L; O=${1:-$B/out/build-$RATIO}; mkdir -p "$O"; cd "$O"
M=${MUSIC:-$B/../../music/v2/yardswaps-music-clean-120bpm.mp3}; FX=$B/source/music   # ElevenLabs Music (Nov 2026 beds), 120 bpm = 2 beats per opener cut
eval "$(python3 -c "
import json; z=json.load(open('$A/layout.json')); x0,y0,x1,y1=z['box']; p=z['phone']
print(f\"H={z['H']} CAPY={z['capY']} BW={x1-x0} BH={y1-y0} CX={(x0+x1)//2} CY={(y0+y1)//2} PX={p['x']} PY={p['y']} PW={p['w']} PH={p['h']}\")")"
N="fps=30,format=yuv420p,setsar=1"; GRADE="eq=saturation=1.03:contrast=1.03:brightness=0.01"
BT=0.5; D1=$(python3 -c "print(3*$BT)"); D2=$(python3 -c "print(2*$BT)"); DE=2.6
POP="format=rgba,scale=w='trunc(iw*(1+0.18*max(0,1-t/0.12))/2)*2':h=-2:eval=frame"
# A real listing photo, whole: fitted inside the photo box (never cropped), slow push to 1.035x that grows into the
# box margins, over a blurred, darkened copy of itself; caption pops in; logo pill from frame 0.
shot() { # <photo> <dur> <cap.png> <out>
  ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -t $2 -i "$1" -loop 1 -framerate 30 -t $2 -i "$3" -loop 1 -framerate 30 -t $2 -i $A/brand-big.png -filter_complex \
   "[0:v]split[s0][s1];[s0]scale=1080:$H:force_original_aspect_ratio=increase,crop=1080:$H,boxblur=40:8,eq=brightness=-0.10:saturation=0.85,$N[bg];\
    [s1]scale=w=$((BW*1000/1035)):h=$((BH*1000/1035)):force_original_aspect_ratio=decrease,$GRADE,format=rgba,scale=w='trunc(iw*(1+0.035*t/$2)/2)*2':h=-2:eval=frame[fg];\
    [1:v]$POP[c];[2:v]format=rgba[b];\
    [bg][fg]overlay=x='$CX-overlay_w/2':y='$CY-overlay_h/2':eval=frame[a];[a][c]overlay=x='(W-w)/2':y='$CAPY-h/2'[v1];[v1][b]overlay=0:0,$N[v]" \
   -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$4"
}
P=$B/source/photos
shot $P/1-loader-cat-950g.jpg $D1 $A/cap1.png s1.mp4
shot $P/2-crane-tadano-gr800xl.jpg $D2 $A/cap2.png s2.mp4
shot $P/3-roller-dynapac-ca602pd.jpg $D2 $A/cap3.png s3.mp4
shot $P/4-pallet-racking-lot.jpg $D2 $A/cap4.png s4.mp4
shot $P/5-instapak-packer.jpg $D2 $A/cap5.png s5.mp4
# The phone: the real app recording masked into the phone on the light stage, one headline per segment.
read DA T1 T2 T3 < <(python3 -c "import json;m=json.load(open('$B/source/app-seller.json'));s=m['segs'];print(m['dur'],s[1]['t'],s[2]['t'],s[3]['t'])")
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/stage.png -i $B/source/app-seller.mp4 -loop 1 -framerate 30 -i $A/phone-mask.png \
  -loop 1 -framerate 30 -i $A/head1.png -loop 1 -framerate 30 -i $A/head2.png -loop 1 -framerate 30 -i $A/head3.png -loop 1 -framerate 30 -i $A/head4.png -filter_complex \
  "[1:v]scale=$PW:$PH,format=rgba[p];[2:v]format=gray,scale=$PW:$PH[m];[p][m]alphamerge[pm];[0:v][pm]overlay=$PX:$PY[a];\
   [a][3:v]overlay=0:0:enable='lt(t,$T1)'[h1];[h1][4:v]overlay=0:0:enable='between(t,$T1,$T2-0.001)'[h2];\
   [h2][5:v]overlay=0:0:enable='between(t,$T2,$T3-0.001)'[h3];[h3][6:v]overlay=0:0:enable='gte(t,$T3)',$N[v]" \
  -map "[v]" -t $DA -an -c:v libx264 -crf 16 -preset medium s6.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $CARD -vf "fade=in:d=0.15,$N" -t $DE -c:v libx264 -crf 16 -preset medium s7.mp4
ffmpeg -hide_banner -loglevel error -y $(for i in 1 2 3 4 5 6 7; do echo -i s$i.mp4; done) -filter_complex "concat=n=7:v=1:a=0,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 20 -preset slow video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4); FO=$(python3 -c "print(round($D-1.5,2))")
case "$RATIO" in 4x5) OUT=yardswaps-sellers-new-listings-4x5.mp4 ;; 9x16-shorts) OUT=yardswaps-sellers-new-listings-shorts-9x16.mp4 ;; *) OUT=yardswaps-sellers-new-listings-9x16.mp4 ;; esac
# whoosh 0.12 s before each hard cut between photos and into the phone; a tap on each real tap in the app recording
eval "$(python3 -c "
import json; m=json.load(open('$B/source/app-seller.json')); d1,d2=$D1,$D2
cuts=[d1+i*d2-0.12 for i in range(5)]; ph=d1+4*d2; taps=[ph+t for t in m['taps']]
print('CUTS=\"'+' '.join(str(int(c*1000)) for c in cuts)+'\"'); print('TAPS=\"'+' '.join(str(int(t*1000)) for t in taps)+'\"')")"
IN=""; F=""; LBL=""; k=2
for c in $CUTS; do IN="$IN -i $FX/whoosh.mp3"; F="$F[$k:a]adelay=$c|$c,volume=0.35[x$k];"; LBL="$LBL[x$k]"; k=$((k+1)); done
for t in $TAPS; do IN="$IN -i $FX/tap.mp3"; F="$F[$k:a]adelay=$t|$t,volume=0.5[x$k];"; LBL="$LBL[x$k]"; k=$((k+1)); done
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -i "$M" $IN -filter_complex \
 "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,afade=t=out:st=$FO:d=1.5[m];$F[m]${LBL}amix=inputs=$((k-1)):normalize=0:duration=first,\
  acompressor=threshold=-24dB:ratio=2.5:attack=15:release=300:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9,atrim=0:$D[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
rm -f s[0-9].mp4 video.mp4
echo "$OUT $RATIO duration $D"
