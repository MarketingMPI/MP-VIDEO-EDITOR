#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-salume"
T=0.5
ffmpeg -y -loglevel error \
 -i s1.mp4 -i s2.mp4 -i s3.mp4 -i s4.mp4 -i s5.mp4 -i s6.mp4 -i s7.mp4 -i s8.mp4 -i s9.mp4 -i s10.mp4 \
 -filter_complex "\
[0:v]fps=60,settb=1/60[v0];[1:v]fps=60,settb=1/60[v1];[2:v]fps=60,settb=1/60[v2];[3:v]fps=60,settb=1/60[v3];[4:v]fps=60,settb=1/60[v4];[5:v]fps=60,settb=1/60[v5];[6:v]fps=60,settb=1/60[v6];[7:v]fps=60,settb=1/60[v7];[8:v]fps=60,settb=1/60[v8];[9:v]fps=60,settb=1/60[v9];\
[v0][v1]xfade=transition=fade:duration=${T}:offset=8.5[x1];\
[x1][v2]xfade=transition=fade:duration=${T}:offset=15.65[x2];\
[x2][v3]xfade=transition=smoothleft:duration=${T}:offset=24.183[x3];\
[x3][v4]xfade=transition=fadeblack:duration=${T}:offset=30.716[x4];\
[x4][v5]xfade=transition=fade:duration=${T}:offset=38.216[x5];\
[x5][v6]xfade=transition=fade:duration=${T}:offset=46.716[x6];\
[x6][v7]xfade=transition=fade:duration=${T}:offset=54.249[x7];\
[x7][v8]xfade=transition=smoothright:duration=${T}:offset=62.749[x8];\
[x8][v9]xfade=transition=fadeblack:duration=${T}:offset=70.249[vout]" \
 -map "[vout]" -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 -pix_fmt yuv420p -r 60 video_montagem.mp4
echo "MONTAGEM OK"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 video_montagem.mp4
