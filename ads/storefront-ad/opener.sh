#!/bin/bash
# opener.sh <photo.jpg|clip.mp4> <seconds> <out.mp4>  (env H = frame height, Y = band top)
# The whole item in frame: the 4:3 source at full 1080 width in a band inside the 1080xH frame, over a blurred, darkened copy.
# A still gets a slow push (1.00 -> 1.035, under the 1.04 cap). A clip (Runway Gen-4 Turbo from the same still) plays as is.
set -e
SRC=$1; T=$2; OUT=$3; FR=30; N=$(python3 -c "print(int($T*$FR))"); H=${H:-1920}; Y=${Y:-300}
W0=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$SRC"); H0=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$SRC")
BH=$(python3 -c "print(int(round(1080*$H0/$W0/2))*2)")
BGF="scale=1080:$H:force_original_aspect_ratio=increase,crop=1080:$H,boxblur=30:4,eq=brightness=-0.22:saturation=0.8"
case "$SRC" in
 *.mp4|*.mov)
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -filter_complex "[0:v]split[a][b];[a]$BGF[bg];[b]scale=1080:$BH[band];[bg][band]overlay=0:$Y,fps=$FR,format=yuv420p,setsar=1[v]" -map "[v]" -t $T -an -c:v libx264 -crf 16 -preset medium "$OUT" ;;
 *)
  ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate $FR -i "$SRC" -filter_complex "[0:v]split[a][b];[a]$BGF[bg];[b]scale=2160:-2,zoompan=z='1+0.035*on/$N':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x$BH:fps=$FR[band];[bg][band]overlay=0:$Y,format=yuv420p,setsar=1[v]" -map "[v]" -t $T -an -c:v libx264 -crf 16 -preset medium "$OUT" ;;
esac
echo "$OUT band=1080x$BH y=$Y"
