#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-salume"
D="C:/Users/phenr/Videos/Eventos MFO - Salume"

TM="zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p"
COL="eq=contrast=1.06:saturation=1.07:gamma=1.02,unsharp=5:5:0.5:5:5:0.0,format=yuv420p"

# reframe: $1=zoom_ini $2=zoom_fim(kenburns) $3=cx $4=cy $5=fps $6=dur_frames
# usa zoompan com zoom variando linearmente (Ken Burns) => movimento sutil
kb() { echo "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min($1+($2-$1)*on/$6,$2)':x='iw*$3-(iw/zoom/2)':y='ih*$4-(ih/zoom/2)':d=1:s=1080x1920:fps=$5"; }
# estatico com zoom fixo: $1=zoom $2=cx $3=cy $4=fps
zc() { echo "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z=$1:x='iw*$2-(iw/zoom/2)':y='ih*$3-(ih/zoom/2)':d=1:s=1080x1920:fps=$4"; }

enc() { ffmpeg -y -loglevel error "$@" -an -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 -pix_fmt yuv420p -r 60; }

# --- 10 cenas, planos variados, com closes e Ken Burns ---
echo "== s1: IMG_0228 plano geral abertura (Ken Burns leve) 9s =="
enc -ss 33 -t 9 -i "$D/IMG_0228.MOV" -vf "${TM},$(kb 1.06 1.16 0.5 0.42 60 540),${COL}" s1.mp4

echo "== s2: IMG_0223 close consultor MP 8s =="
enc -ss 15 -t 8 -i "$D/IMG_0223.MOV" -vf "${TM},$(zc 1.18 0.48 0.4 60),${COL}" s2.mp4

echo "== s3: IMG_0231 palestrante plano medio 9s =="
enc -ss 8 -t 9 -i "$D/IMG_0231.MOV" -vf "${TM},$(zc 1.10 0.46 0.4 30),${COL}" s3.mp4

echo "== s4: IMG_0231 punch-in close palestrante 7s =="
enc -ss 38 -t 7 -i "$D/IMG_0231.MOV" -vf "${TM},$(kb 1.25 1.36 0.45 0.34 30 210),${COL}" s4.mp4

echo "== s5: IMG_0225 plateia/ambiente 8s =="
enc -ss 12 -t 8 -i "$D/IMG_0225.MOV" -vf "${TM},$(kb 1.06 1.14 0.5 0.46 60 480),${COL}" s5.mp4

echo "== s6: IMG_0234 consultor/palestrante outro angulo 9s =="
enc -ss 18 -t 9 -i "$D/IMG_0234.MOV" -vf "${TM},$(zc 1.14 0.48 0.4 30),${COL}" s6.mp4

echo "== s7: IMG_0232 palestrante gesticulando 8s =="
enc -ss 8 -t 8 -i "$D/IMG_0232.MOV" -vf "${TM},$(kb 1.12 1.22 0.46 0.38 30 240),${COL}" s7.mp4

echo "== s8: IMG_0228 plano geral jantar 9s =="
enc -ss 5 -t 9 -i "$D/IMG_0228.MOV" -vf "${TM},$(kb 1.08 1.18 0.5 0.44 60 540),${COL}" s8.mp4

echo "== s9: IMG_0233 palestrante close 8s =="
enc -ss 18 -t 8 -i "$D/IMG_0233.MOV" -vf "${TM},$(zc 1.22 0.46 0.36 30),${COL}" s9.mp4

echo "== s10: IMG_0234 encerramento amplo (Ken Burns) 10s =="
enc -ss 50 -t 10 -i "$D/IMG_0234.MOV" -vf "${TM},$(kb 1.06 1.16 0.5 0.44 30 300),${COL}" s10.mp4

echo "SEGMENTOS OK"
for s in s1 s2 s3 s4 s5 s6 s7 s8 s9 s10; do echo -n "$s: "; ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 $s.mp4; done
