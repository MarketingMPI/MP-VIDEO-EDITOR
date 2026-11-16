#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-jpmorgan"
T=0.6
ffmpeg -y -loglevel error \
 -i s1.mp4 -i s2.mp4 -i s3.mp4 -i s4.mp4 -i s5.mp4 -i s6.mp4 -i s7.mp4 -i s8.mp4 \
 -filter_complex "\
[0:v]settb=AVTB,fps=60[v0];[1:v]settb=AVTB,fps=60[v1];[2:v]settb=AVTB,fps=60[v2];[3:v]settb=AVTB,fps=60[v3];[4:v]settb=AVTB,fps=60[v4];[5:v]settb=AVTB,fps=60[v5];[6:v]settb=AVTB,fps=60[v6];[7:v]settb=AVTB,fps=60[v7];\
[v0][v1]xfade=transition=fade:duration=${T}:offset=6.4[x1];\
[x1][v2]xfade=transition=fadeblack:duration=${T}:offset=14.8[x2];\
[x2][v3]xfade=transition=fade:duration=${T}:offset=25.2[x3];\
[x3][v4]xfade=transition=smoothleft:duration=${T}:offset=34.617[x4];\
[x4][v5]xfade=transition=fade:duration=${T}:offset=43.033[x5];\
[x5][v6]xfade=transition=fade:duration=${T}:offset=52.45[x6];\
[x6][v7]xfade=transition=fadeblack:duration=${T}:offset=59.85[vout]" \
 -map "[vout]" -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 -pix_fmt yuv420p -r 60 video_montagem.mp4
echo "MONTAGEM OK"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 video_montagem.mp4
