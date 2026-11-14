#!/bin/bash
# Build the YardSwaps story ad "The yard run" (9:16). Usage: build.sh <clipdir>
set -e
B=$(cd "$(dirname "$0")" && pwd); C=$1
APP=/mnt/project-files/yardswaps-campaign/assets/motion/silent/yardswaps-pressure-washer-replaced-9x16.mp4
mkdir -p $B/out && cd $B/out
N="fps=30,format=yuv420p,setsar=1,scale=1080:1920"
G="eq=saturation=0.95:contrast=1.02"
cut() { ffmpeg -hide_banner -loglevel error -y -i "$1" -vf "trim=$2:$3,setpts=PTS-STARTPTS,$N,$G$5" -an -c:v libx264 -crf 17 -preset medium "$4"; }
cut $C/v1.mp4 0.3 4.8 a01.mp4 ",fade=in:st=0:d=0.6"
cut $C/v2.mp4 0.5 4.0 a02.mp4
cut $C/v3.mp4 0.2 5.2 a03.mp4
cut $C/v4.mp4 0.6 4.6 a04.mp4
ffmpeg -hide_banner -loglevel error -y -i $APP -vf "trim=2.4:15.4,setpts=(PTS-STARTPTS)/2,$N" -an -c:v libx264 -crf 17 -preset medium a05.mp4
# v5: blur the buyer truck's rear plate (static camera)
ffmpeg -hide_banner -loglevel error -y -i $C/v5.mp4 -filter_complex "[0:v]trim=0.5:5.0,setpts=PTS-STARTPTS,$N,$G,split[m][b];[b]crop=130:70:625:710,boxblur=14:3[bl];[m][bl]overlay=625:710" -an -c:v libx264 -crf 17 -preset medium a06.mp4
cut $C/v6.mp4 1.0 4.5 a07.mp4
cut $C/v7.mp4 0.5 5.0 a08.mp4
cut $C/v8.mp4 1.0 5.0 a09.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i ../endcard.png -vf "$N,fade=in:st=0:d=0.5:color=0xF6F6F8" -t 5.0 -c:v libx264 -crf 17 -preset medium a10.mp4
ffmpeg -hide_banner -loglevel error -y $(for i in 01 02 03 04 05 06 07 08 09 10; do echo -n "-i a$i.mp4 "; done) \
 -i ../c1.png -i ../c2.png -i ../c3.png -i ../c4.png -i ../c6.png -i ../c7.png -filter_complex \
 "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v][9:v]concat=n=10:v=1:a=0[v0];\
[v0][10:v]overlay=enable='between(t,0.8,3.9)'[v1];[v1][11:v]overlay=enable='between(t,8.6,10.6)'[v2];\
[v2][12:v]overlay=enable='between(t,10.7,15.2)'[v3];[v3][13:v]overlay=enable='between(t,15.5,16.95)'[v4];\
[v4][14:v]overlay=enable='between(t,24.1,26.6)'[v5];[v5][15:v]overlay=enable='between(t,31.9,35.8)',format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 18 -preset medium video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4)
V=$C/vo-a.mp3
# voice phrases: src start, src end, place at
ph() { echo "[1:a]atrim=$1:$2,asetpts=PTS-STARTPTS,adelay=$(python3 -c "print(int($3*1000))")|$(python3 -c "print(int($3*1000))")[p$4];"; }
F="$(ph 0 3.05 0.8 1)$(ph 3.55 5.45 8.6 2)$(ph 6.0 10.45 10.7 3)$(ph 11.1 12.4 15.5 4)$(ph 13.55 18.05 17.4 5)$(ph 18.6 20.9 24.1 6)$(ph 21.2 24.9 31.9 7)$(ph 25.55 26.7 40.5 8)$(ph 27.25 28.38 42.0 9)"
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -i $V -i $C/music-a.mp3 -filter_complex \
 "${F}[p1][p2][p3][p4][p5][p6][p7][p8][p9]amix=inputs=9:normalize=0,apad,atrim=0:$D,volume=1.0,asplit[vo][sc];\
[2:a]atrim=0:$D,asetpts=PTS-STARTPTS,volume=0.55,afade=t=in:d=0.5,afade=t=out:st=$(python3 -c "print(round($D-2.5,2))"):d=2.5[mu];\
[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=600[mud];\
[vo][mud]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart final.mp4
echo $D
