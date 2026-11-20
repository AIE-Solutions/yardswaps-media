#!/bin/bash
# Storefront ad, about 26 s. Usage: RATIO=9x16|9x16-paid|4x5|1x1 build.sh <clipdir with a.mp4 b.mp4 c.mp4, or empty for the stills> <out dir>
# Three idle units in a dealer yard (Runway Gen-4 Turbo clips from the 4:3 stills if present, else the stills with a slow
# push) with one lower-left line each, then the real app on a big phone (the storefront with the same three units at the
# top, then the Dealer plan card), then the light end card. The per-size assets come from layout.py (r<RATIO>/).
# 9x16-paid (Meta Reels, Stories): the line is on screen from frame 0 and every word sits between 15 and 62 percent of the height.
set -e
B=$(cd "$(dirname "$0")" && pwd); C=${1:-}; O=${2:-$B/out}; mkdir -p "$O"; cd "$O"
RATIO=${RATIO:-9x16}; A=$B/r$RATIO; S=$B/../parts-ad/source; M=${MUSIC:-$B/../../music/v2/yardswaps-music-road-124bpm.mp3}
read H BY PX PY PW PH < <(python3 -c "import json;z=json.load(open('$A/phone.json'));p=z['phone'];print(z['H'],z['bandY'],p['x'],p['y'],p['w'],p['h'])")
case "$RATIO" in *paid*) T0=0; ;; *) T0=0.5; ;; esac
N="fps=30,format=yuv420p,setsar=1"; GRADE="eq=saturation=0.96:contrast=1.03"; X=0.3
pick() { [ -n "$C" ] && [ -f "$C/$1.mp4" ] && echo "$C/$1.mp4" || echo "$B/stills/$2"; }
H=$H Y=$BY bash $B/opener.sh "$(pick a grapple-truck-4x3.jpg)" 4.2 o1.mp4
H=$H Y=$BY bash $B/opener.sh "$(pick b skytrak-telehandler-4x3.jpg)" 4.0 o2.mp4
H=$H Y=$BY bash $B/opener.sh "$(pick c f350-supercab-4x3.jpg)" 3.8 o3.mp4
seg() { # <src> <dur> <caption.png> <out>
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$3" -filter_complex \
   "[0:v]$GRADE,$N[a];[1:v]format=rgba,fade=in:st=$T0:d=0.4:alpha=1,fade=out:st=$(python3 -c "print($2-0.55)"):d=0.3:alpha=1[t];\
    [a][t]overlay=x=0:y='max(0\,22*(1-(t-$T0)/0.5))':eval=frame:shortest=1,$N[v]" -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$4"
}
seg o1.mp4 4.2 $A/c1.png a1.mp4
seg o2.mp4 4.0 $A/c2.png a2.mp4
seg o3.mp4 3.8 $A/c3.png a3.mp4
phone() { # <stage.png> <src> <dur> <out> [loop]
  ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i "$1" ${5:+-loop 1 -framerate 30} -i "$2" -loop 1 -framerate 30 -i $A/phone-mask.png -filter_complex \
   "[1:v]scale=$PW:$PH,format=rgba[p];[2:v]format=gray[m];[p][m]alphamerge[pm];[0:v][pm]overlay=$PX:$PY:shortest=1,$N[v]" -map "[v]" -t $3 -an -c:v libx264 -crf 16 -preset medium "$4"
}
phone $A/stage-store.png $B/rec/storefront-8s.mp4 7.6 a4.mp4
phone $A/stage-plans.png $B/rec/plans-dealer.png 3.6 a5.mp4 loop
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $A/endcard.png -vf "$N" -t 4.4 -c:v libx264 -crf 16 -preset medium a6.mp4
python3 - <<'PY' > xf.txt
import subprocess
d=[float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","a%d.mp4"%i]).decode()) for i in range(1,7)]; X=0.3
f=[]; prev="0:v"; off=0
for i in range(1,len(d)):
    off += d[i-1]-X
    out = "v%d"%i if i<len(d)-1 else "vx"
    f.append("[%s][%d:v]xfade=transition=fade:duration=%s:offset=%.3f[%s]"%(prev,i,X,off,out)); prev=out
print(";".join(f)+";[vx]format=yuv420p[v]")
PY
ffmpeg -hide_banner -loglevel error -y $(for i in 1 2 3 4 5 6; do echo -i a$i.mp4; done) -filter_complex "$(cat xf.txt)" -map "[v]" -c:v libx264 -crf 20 -preset slow video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4); FO=$(python3 -c "print(round($D-1.8,2))")
case "$RATIO" in 9x16-paid) DEF=yardswaps-storefront-paid-9x16.mp4 ;; 4x5) DEF=yardswaps-storefront-paid-4x5.mp4 ;; 1x1) DEF=yardswaps-storefront-paid-1x1.mp4 ;; *) DEF=yardswaps-storefront-9x16.mp4 ;; esac
OUT=${OUT:-$DEF}
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -stream_loop -1 -i "$M" -filter_complex "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,afade=t=in:d=0.4,afade=t=out:st=$FO:d=1.8,acompressor=threshold=-28dB:ratio=2.5:attack=20:release=400:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=9[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
echo "$OUT ${RATIO} duration $D"
