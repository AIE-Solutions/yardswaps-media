#!/bin/bash
# "Every shop has one" v2 (9:16). Usage: build.sh <clipdir with s1-s8.mp4> <music.mp3> <app recording.mp4>
set -e
B=$(cd "$(dirname "$0")" && pwd); C=$(cd "$1" && pwd); M=$(realpath "$2"); APP=$(realpath "$3")
mkdir -p $B/out && cd $B/out
N="fps=30,format=yuv420p,setsar=1"
GRADE="eq=saturation=0.96:contrast=1.03"
X=0.3   # dissolve length
# seg <src> <start> <dur> <caption.png> <out> [extra video filter]
seg() {
  local EXTRA=${6:+,$6}
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$4" -filter_complex \
   "[0:v]trim=$2:$(python3 -c "print($2+$3)"),setpts=PTS-STARTPTS,scale=1080:1920$EXTRA,$GRADE,$N[a];\
    [1:v]format=rgba,fade=in:st=0.35:d=0.4:alpha=1,fade=out:st=$(python3 -c "print($3-0.55)"):d=0.3:alpha=1[t];\
    [a][t]overlay=x=0:y='max(0\,22*(1-(t-0.35)/0.5))':eval=frame:shortest=1,$N[v]" \
   -map "[v]" -t $3 -an -c:v libx264 -crf 16 -preset medium "$5"
}
seg $C/s1.mp4 0.2 3.3 ../t1.png a1.mp4
seg $C/s2.mp4 0.2 3.0 ../t2.png a2.mp4
seg $C/s3.mp4 0.2 3.0 ../t3.png a3.mp4
seg $C/s4.mp4 0.2 3.0 ../t4.png a4.mp4
seg $C/s5.mp4 0.2 3.3 ../t5.png a5.mp4
# real app recording listing the same washer: source 2.4-15.4 s at 2x = 6.5 s
ffmpeg -hide_banner -loglevel error -y -i "$APP" -filter_complex "[0:v]trim=2.4:15.4,setpts=(PTS-STARTPTS)/2,scale=1080:1920,$N[v]" -map "[v]" -an -c:v libx264 -crf 16 -preset medium a6.mp4
# handshake: blur the trailer plate behind the buyer
seg $C/s6.mp4 0.8 3.9 ../t6.png a7.mp4 "split[m][p];[p]crop=130:110:925:970,boxblur=14:3[pb];[m][pb]overlay=925:970"
seg $C/s7.mp4 0.2 3.1 ../t7.png a8.mp4
seg $C/s8.mp4 0.3 3.6 ../t8.png a9.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i ../endcard.png -vf "$N" -t 4.8 -c:v libx264 -crf 16 -preset medium a10.mp4
# dissolve chain
python3 - <<'PY' > xf.txt
import subprocess
d=[float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","a%d.mp4"%i]).decode()) for i in range(1,11)]; X=0.3
f=[]; prev="0:v"; off=0
for i in range(1,len(d)):
    off += d[i-1]-X
    out = "v%d"%i if i<len(d)-1 else "vx"
    f.append("[%s][%d:v]xfade=transition=fade:duration=%s:offset=%.3f[%s]"%(prev,i,X,off,out)); prev=out
print(";".join(f)+";[vx]format=yuv420p[v]")
PY
ffmpeg -hide_banner -loglevel error -y $(for i in $(seq 1 10); do echo -i a$i.mp4; done) -filter_complex "$(cat xf.txt)" -map "[v]" -c:v libx264 -crf 20 -preset slow video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4)
FO=$(python3 -c "print(round($D-1.8,2))")
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -i "$M" -filter_complex "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,afade=t=in:d=0.2,afade=t=out:st=$FO:d=1.8,acompressor=threshold=-28dB:ratio=2.5:attack=20:release=400:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=9[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart final.mp4
echo "$D"
