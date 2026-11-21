#!/bin/bash
# v3 storefront ad, about 13 s, built for Meta (sound off, text in the safe zone, motion from frame 0).
# Usage: RATIO=9x16-paid|4x5|1x1 [D1 D2 D3 D4 = scene seconds, TAG=v3.1] build-v3.sh <clipdir with y1.mp4 y2.mp4 (vertical Gen-4 Turbo clips)> <out dir>
# y1 (3.0 s) "Your yard." + wordmark + AI label -> y2 (2.6 s) "On one page." -> real app storefront on a phone (5.4 s)
# -> end card (4.0 s). Assets per size from layout-v3.py (v3-<RATIO>/).
set -e
B=$(cd "$(dirname "$0")" && pwd); C=${1:?clipdir}; O=${2:-$B/out-v3}; mkdir -p "$O"; cd "$O"
RATIO=${RATIO:-9x16-paid}; A=$B/v3-$RATIO; D1=${D1:-3.0}; D2=${D2:-2.6}; D3=${D3:-5.4}; D4=${D4:-4.0}; TAG=${TAG:-v3}; M=${MUSIC:-$B/../../music/v2/yardswaps-music-road-124bpm.mp3}
read H PX PY PW PH < <(python3 -c "import json;z=json.load(open('$A/phone.json'));p=z['phone'];print(z['H'],p['x'],p['y'],p['w'],p['h'])")
N="fps=30,format=yuv420p,setsar=1"; GRADE="eq=saturation=1.02:contrast=1.02:brightness=0.01"
# full-frame opener: cover 1080xH from the vertical clip (centre crop), then the line, the wordmark and the AI label from frame 0
seg() { # <clip> <dur> <caption.png> <out>
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$3" -loop 1 -i $A/brand.png -loop 1 -i $A/ai.png -filter_complex \
   "[0:v]scale=1080:$H:force_original_aspect_ratio=increase,crop=1080:$H,$GRADE,$N[a];\
    [1:v]format=rgba,fade=out:st=$(python3 -c "print($2-0.45)"):d=0.3:alpha=1[t];[2:v]format=rgba[b];[3:v]format=rgba[l];\
    [a][t]overlay=0:0:shortest=1[v1];[v1][b]overlay=0:0:shortest=1[v2];[v2][l]overlay=0:0:shortest=1,$N[v]" \
   -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$4"
}
seg "$C/y1.mp4" $D1 $A/cap-a.png a1.mp4
seg "$C/y2.mp4" $D2 $A/cap-b.png a2.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/stage-store.png -i $B/rec/storefront-8s.mp4 -loop 1 -framerate 30 -i $A/phone-mask.png -filter_complex \
   "[1:v]scale=$PW:$PH,format=rgba[p];[2:v]format=gray[m];[p][m]alphamerge[pm];[0:v][pm]overlay=$PX:$PY:shortest=1,$N[v]" -map "[v]" -t $D3 -an -c:v libx264 -crf 16 -preset medium a3.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/endcard.png -vf "$N" -t $D4 -c:v libx264 -crf 16 -preset medium a4.mp4
python3 - <<'PY' > xf.txt
import subprocess
d=[float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","a%d.mp4"%i]).decode()) for i in range(1,5)]; X=0.3
f=[]; prev="0:v"; off=0
for i in range(1,len(d)):
    off += d[i-1]-X
    out = "v%d"%i if i<len(d)-1 else "vx"
    f.append("[%s][%d:v]xfade=transition=fade:duration=%s:offset=%.3f[%s]"%(prev,i,X,off,out)); prev=out
print(";".join(f)+";[vx]format=yuv420p[v]")
PY
ffmpeg -hide_banner -loglevel error -y $(for i in 1 2 3 4; do echo -i a$i.mp4; done) -filter_complex "$(cat xf.txt)" -map "[v]" -c:v libx264 -crf 20 -preset slow video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4); FO=$(python3 -c "print(round($D-1.5,2))")
case "$RATIO" in 4x5) DEF=yardswaps-storefront-$TAG-paid-4x5.mp4 ;; 1x1) DEF=yardswaps-storefront-$TAG-paid-1x1.mp4 ;; *) DEF=yardswaps-storefront-$TAG-paid-9x16.mp4 ;; esac
OUT=${OUT:-$DEF}
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -stream_loop -1 -i "$M" -filter_complex "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st=$FO:d=1.5,acompressor=threshold=-28dB:ratio=2.5:attack=20:release=400:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=9[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
echo "$OUT $RATIO duration $D"
