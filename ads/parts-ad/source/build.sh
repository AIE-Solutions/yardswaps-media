#!/bin/bash
# "Snap the part" (9:16). Usage: build.sh <clipdir with a.mp4 b.mp4 c.mp4, or empty for stills> <out dir>
# Openers: three idle items (clips from Runway Gen-4 Turbo if present, else the real photos with a slow push).
# App: the real sell-flow recording of the same cylinders (motion/silent/yardswaps-surplus-parts-labels-9x16.mp4, 4.85-14.15 s).
set -e
B=$(cd "$(dirname "$0")" && pwd); C=${1:-}; O=${2:-$B/out}; mkdir -p "$O"; cd "$O"
APP=${APP:-/mnt/project-files/yardswaps-campaign/assets/motion/silent/yardswaps-surplus-parts-labels-9x16.mp4}
M=$B/music-workshop-26s.mp3
N="fps=30,format=yuv420p,setsar=1"; GRADE="eq=saturation=0.96:contrast=1.03"; X=0.3
pick() { [ -n "$C" ] && [ -f "$C/$1.mp4" ] && echo "$C/$1.mp4" || echo "$B/photos/$2"; }
bash $B/opener.sh "$(pick a a-cylinders.jpg)" 3.3 o1.mp4
bash $B/opener.sh "$(pick b b-micrometer.jpg)" 3.0 o2.mp4
bash $B/opener.sh "$(pick c c-spray-trailer.jpg)" 3.0 o3.mp4
seg() { # <src> <dur> <caption.png> <out>
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$3" -filter_complex \
   "[0:v]$GRADE,$N[a];[1:v]format=rgba,fade=in:st=0.35:d=0.4:alpha=1,fade=out:st=$(python3 -c "print($2-0.55)"):d=0.3:alpha=1[t];\
    [a][t]overlay=x=0:y='max(0\,22*(1-(t-0.35)/0.5))':eval=frame:shortest=1,$N[v]" -map "[v]" -t $2 -an -c:v libx264 -crf 16 -preset medium "$4"
}
seg o1.mp4 3.3 $B/c1.png a1.mp4
seg o2.mp4 3.0 $B/c2.png a2.mp4
seg o3.mp4 3.0 $B/c3.png a3.mp4
ffmpeg -hide_banner -loglevel error -y -ss 4.85 -t 9.3 -i "$APP" -vf "scale=1080:1920,$N" -an -c:v libx264 -crf 16 -preset medium a4.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i $B/endcard.png -vf "$N" -t 4.8 -c:v libx264 -crf 16 -preset medium a5.mp4
python3 - <<'PY' > xf.txt
import subprocess
d=[float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","a%d.mp4"%i]).decode()) for i in range(1,6)]; X=0.3
f=[]; prev="0:v"; off=0
for i in range(1,len(d)):
    off += d[i-1]-X
    out = "v%d"%i if i<len(d)-1 else "vx"
    f.append("[%s][%d:v]xfade=transition=fade:duration=%s:offset=%.3f[%s]"%(prev,i,X,off,out)); prev=out
print(";".join(f)+";[vx]format=yuv420p[v]")
PY
ffmpeg -hide_banner -loglevel error -y $(for i in 1 2 3 4 5; do echo -i a$i.mp4; done) -filter_complex "$(cat xf.txt)" -map "[v]" -c:v libx264 -crf 20 -preset slow video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4); FO=$(python3 -c "print(round($D-1.8,2))")
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -i "$M" -filter_complex "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,afade=t=in:d=0.2,afade=t=out:st=$FO:d=1.8,acompressor=threshold=-28dB:ratio=2.5:attack=20:release=400:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=9[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart yardswaps-snap-the-part-9x16.mp4
echo "duration $D"
