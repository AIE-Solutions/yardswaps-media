#!/bin/bash
# Build the YardSwaps brand commercial (9:16). Usage: build.sh <clipdir> <music.mp3> <music_offset_s>
set -e
B=$(cd "$(dirname "$0")" && pwd); C=$1; M=$2; MOFF=${3:-0}
WASH=/home/user/yardswaps-media/narration/idle-gear-montage-v2/clip1-washer-v2.mp4
APP=/mnt/project-files/yardswaps-campaign/assets/motion/silent/yardswaps-pressure-washer-replaced-9x16.mp4
mkdir -p $B/out && cd $B/out
N="fps=30,format=yuv420p,setsar=1"
GRADE="eq=saturation=0.92:contrast=1.03"
seg() { # src start dur overlay out
  ffmpeg -hide_banner -loglevel error -y -i "$1" -loop 1 -i "$4" -filter_complex \
   "[0:v]trim=$2:$(python3 -c "print($2+$3)"),setpts=PTS-STARTPTS,scale=1080:1920,$N[a];[1:v]format=rgba,fade=in:st=0.25:d=0.35:alpha=1,fade=out:st=$(python3 -c "print($3-0.4)"):d=0.35:alpha=1[t];[a][t]overlay=shortest=1,$N[v]" \
   -map "[v]" -t $3 -an -c:v libx264 -crf 17 -preset medium "$5"
}
seg $C/s1.mp4 0.2 3.4 ../t1.png a1.mp4
seg $C/s2.mp4 0.2 2.6 ../t2.png a2.mp4
seg $C/s3.mp4 0.2 2.6 ../t3.png a3.mp4
seg $C/s4.mp4 0.2 2.6 ../t4.png a4.mp4
seg $WASH 0.0 3.0 ../t5.png a5.mp4
# real app: source 2.4-15.4 s at 2x = 6.5 s
ffmpeg -hide_banner -loglevel error -y -i $APP -filter_complex "[0:v]trim=2.4:15.4,setpts=(PTS-STARTPTS)/2,$N[v]" -map "[v]" -an -c:v libx264 -crf 17 -preset medium a6.mp4
seg $C/s7.mp4 0.2 3.2 ../t7.png a7.mp4
seg $C/s8.mp4 0.2 3.2 ../t8.png a8.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i ../endcard.png -vf "$N,fade=in:st=0:d=0.4:color=0xF6F6F8" -t 4.5 -c:v libx264 -crf 17 -preset medium a9.mp4
# join with short dissolves between cinematic shots
ffmpeg -hide_banner -loglevel error -y -i a1.mp4 -i a2.mp4 -i a3.mp4 -i a4.mp4 -i a5.mp4 -i a6.mp4 -i a7.mp4 -i a8.mp4 -i a9.mp4 -filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v]concat=n=9:v=1:a=0,$N[v]" -map "[v]" -c:v libx264 -crf 17 -preset medium video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4)
FO=$(python3 -c "print(round($D-1.5,2))")
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -i "$M" -filter_complex "[1:a]atrim=$MOFF:$(python3 -c "print($MOFF+$D)"),asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st=$FO:d=1.5,acompressor=threshold=-30dB:ratio=3:attack=20:release=500:makeup=4,loudnorm=I=-14:TP=-1.5:LRA=9[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart final.mp4
echo "$D"
