#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-jpmorgan"
D="C:/Users/phenr/Videos/Evento MFO - Menina do JP Morgan"

TM="zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p"
COL="eq=contrast=1.06:saturation=1.07:gamma=1.02,unsharp=5:5:0.5:5:5:0.0,format=yuv420p"

vcrop() { echo "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z=$1:x='iw*$2-(iw/zoom/2)':y='ih*$3-(ih/zoom/2)':d=1:s=1080x1920:fps=60"; }
enc() { ffmpeg -y -loglevel error "$@" -an -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 -pix_fmt yuv420p -r 60; }

hbox() {
  local src="$1" ss="$2" t="$3" out="$4"
  ffmpeg -y -loglevel error -ss "$ss" -t "$t" -i "$src" -filter_complex \
   "[0:v]${TM},eq=contrast=1.06:saturation=1.07:gamma=1.02[c];[c]split[a][b];\
    [a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28[bg];\
    [b]scale=1080:-2,unsharp=5:5:0.5:5:5:0.0[fg];\
    [bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]" \
   -map "[v]" -an -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 -pix_fmt yuv420p -r 60 "$out"
}

echo "== s1: IMG_0949 abertura consultor + slide Historia FO 7s [vert] =="
enc -ss 2 -t 7 -i "$D/IMG_0949.MOV" -vf "${TM},$(vcrop 1.10 0.5 0.44),${COL}" s1.mp4

echo "== s2: IMG_0964 palestrante camisa branca + slide 9s [vert] =="
enc -ss 3 -t 9 -i "$D/IMG_0964.MOV" -vf "${TM},$(vcrop 1.10 0.5 0.44),${COL}" s2.mp4

echo "== s3: IMG_0957 palestrante JP (blazer verde) + slide lideranca 11s [box] =="
hbox "$D/IMG_0957.MOV" 42 11 s3.mp4

echo "== s4: IMG_0961 palestrante em pe 10s [box] =="
hbox "$D/IMG_0961.MOV" 55 10 s4.mp4

echo "== s5: IMG_0957 JP outro momento (apontando timeline) 9s [box] =="
hbox "$D/IMG_0957.MOV" 20 9 s5.mp4

echo "== s6: IMG_0961 plateia/almoco 10s [box] =="
hbox "$D/IMG_0961.MOV" 245 10 s6.mp4

echo "== s7: IMG_0964 senhora elegante 8s [vert] =="
enc -ss 72 -t 8 -i "$D/IMG_0964.MOV" -vf "${TM},$(vcrop 1.15 0.5 0.42),${COL}" s7.mp4

echo "== s8: IMG_0961 encerramento mesa cheia 11s [box] =="
hbox "$D/IMG_0961.MOV" 276 11 s8.mp4

echo "SEGMENTOS OK"
for s in s1 s2 s3 s4 s5 s6 s7 s8; do echo -n "$s: "; ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 $s.mp4; done
