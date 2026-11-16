#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-eventos"
D="C:/Users/phenr/Videos/Evento MFO"

LOOK_SDR="eq=contrast=1.06:saturation=1.06:gamma=1.02,unsharp=5:5:0.5:5:5:0.0,format=yuv420p"
TM="zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p"
LOOK_HDR="eq=contrast=1.05:saturation=1.05:gamma=1.02,format=yuv420p"

base() { echo "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"; }
# reframe zoompan: $1=zoom $2=cx $3=cy $4=fps
rf() { echo "zoompan=z=$1:x='iw*$2-(iw/zoom/2)':y='ih*$3-(ih/zoom/2)':d=1:s=1080x1920:fps=$4"; }

enc() { ffmpeg -y -loglevel error "$@" -an -c:v libx264 -profile:v high -level 4.2 -preset veryslow -crf 12 -pix_fmt yuv420p -r 60; }

echo "== seg1: Event 4 (abertura, zoom mesa/TV) 6s =="
enc -ss 2 -t 6 -i "$D/Event 4.mp4" -vf "$(base),$(rf 1.35 0.5 0.32 30),${LOOK_SDR}" seg1.mp4

echo "== seg2: Event 5 (palestra) 9s =="
enc -ss 30 -t 9 -i "$D/Event 5.mp4" -vf "$(base),$(rf 1.20 0.52 0.42 30),${LOOK_SDR}" seg2.mp4

echo "== seg3: Event 6 (painel Family Office) 9s =="
enc -ss 24 -t 9 -i "$D/Event 6.mp4" -vf "$(base),$(rf 1.25 0.50 0.46 30),${LOOK_SDR}" seg3.mp4

echo "== seg4: Event 2 (networking) 10s [HDR] =="
enc -ss 45 -t 10 -i "$D/Event 2.MOV" -vf "${TM},$(base),$(rf 1.12 0.50 0.50 60),${LOOK_HDR}" seg4.mp4

echo "== seg5: Event 1 (entrega brinde) 2.6s =="
enc -ss 0.2 -t 2.6 -i "$D/Event 1.MOV" -vf "$(base),$(rf 1.12 0.52 0.46 30),${LOOK_SDR}" seg5.mp4

echo "== seg6: Event 3 (close troféu coruja, slow 0.72x) ~4.5s [HDR] =="
enc -ss 4.2 -t 4.05 -i "$D/Event 3.MOV" -vf "${TM},$(base),$(rf 1.15 0.50 0.42 60),setpts=PTS/0.72,${LOOK_HDR}" seg6.mp4

echo "== seg7: Event 2 (fecho) 9s [HDR] =="
enc -ss 118 -t 9 -i "$D/Event 2.MOV" -vf "${TM},$(base),$(rf 1.32 0.50 0.56 60),${LOOK_HDR}" seg7.mp4

echo "SEGMENTOS v2 OK"
for s in seg1 seg2 seg3 seg4 seg5 seg6 seg7; do
  echo -n "$s: "; ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 $s.mp4
done
