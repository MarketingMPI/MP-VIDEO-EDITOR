#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-herdeira"
D="C:/Users/phenr/Videos/Herdeira - MFO - Depoimento"

TM="zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p"
RF="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z=1.22:x='iw*0.5-(iw/zoom/2)':y='ih*0.56-(ih/zoom/2)':d=1:s=1080x1920:fps=30"
GRADE="colorchannelmixer=1.06:0:0:0:0:0.85:0:0:0:0:1.05:0,colorbalance=rs=-0.04:bs=0.03:rh=-0.03,eq=contrast=1.07:saturation=1.02:gamma=1.03,unsharp=5:5:0.4:5:5:0.0,format=yuv420p"

# so video (sem audio), 30fps mantido. Corta os trechos de fala.
venc() { ffmpeg -y -loglevel error -ss "$2" -to "$3" -i "$D/$1.MOV" -vf "${TM},${RF},${GRADE}" -an -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 -pix_fmt yuv420p -r 30 "$4"; }

echo "== v1: IMG_0241 apresentacao 28.0->68.0 =="
venc IMG_0241 28.0 68.0 v1.mp4
echo "== v2: IMG_0242 decisao MP 7.0->42.0 =="
venc IMG_0242 7.0 42.0 v2.mp4
echo "== v3: IMG_0244 construcao patrimonio 13.6->67.2 =="
venc IMG_0244 13.6 67.2 v3.mp4
echo "== v4: IMG_0243 fecho 0.0->14.4 =="
venc IMG_0243 0.0 14.4 v4.mp4

echo "SEGMENTOS OK"
for v in v1 v2 v3 v4; do echo -n "$v: "; ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 $v.mp4; done
