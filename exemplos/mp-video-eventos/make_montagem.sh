#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-eventos"

# Duracoes dos segmentos (s): seg1=6 seg2=9 seg3=9 seg4=10 seg5=4.5 seg6=6 seg7=9
# Transicoes xfade de 0.6s entre cada par. offset acumulado.
T=0.6

# offsets de cada xfade (fim do seg anterior - T, acumulado)
# seg1 dur6 -> off1 = 6 - 0.6 = 5.4
# apos xf1, timeline ate = 5.4 + 9 = 14.4 ; off2 = 14.4 - 0.6 = 13.8
# +9 = 22.8 ; off3 = 22.2
# +10 = 32.2 ; off4 = 31.6
# +4.5 = 36.1 ; off5 = 35.5
# +6 = 41.5 ; off6 = 40.9

ffmpeg -y -loglevel error \
 -i seg1.mp4 -i seg2.mp4 -i seg3.mp4 -i seg4.mp4 -i seg5.mp4 -i seg6.mp4 -i seg7.mp4 \
 -filter_complex "\
[0:v]settb=AVTB,fps=60[v0];[1:v]settb=AVTB,fps=60[v1];[2:v]settb=AVTB,fps=60[v2];[3:v]settb=AVTB,fps=60[v3];[4:v]settb=AVTB,fps=60[v4];[5:v]settb=AVTB,fps=60[v5];[6:v]settb=AVTB,fps=60[v6];\
[v0][v1]xfade=transition=fade:duration=${T}:offset=5.4[x1];\
[x1][v2]xfade=transition=fadeblack:duration=${T}:offset=13.833[x2];\
[x2][v3]xfade=transition=fade:duration=${T}:offset=22.233[x3];\
[x3][v4]xfade=transition=smoothleft:duration=${T}:offset=31.633[x4];\
[x4][v5]xfade=transition=fade:duration=${T}:offset=33.633[x5];\
[x5][v6]xfade=transition=fade:duration=${T}:offset=38.65[vout]" \
 -map "[vout]" -c:v libx264 -profile:v high -level 4.2 -preset veryslow -crf 12 -pix_fmt yuv420p -r 60 video_montagem.mp4

echo "MONTAGEM OK"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 video_montagem.mp4
