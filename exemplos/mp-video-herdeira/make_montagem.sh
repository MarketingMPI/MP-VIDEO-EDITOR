#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-herdeira"
T=0.4

# VIDEO: xfade encadeado (cortes suaves)
ffmpeg -y -loglevel error \
 -i v1.mp4 -i v2.mp4 -i v3.mp4 -i v4.mp4 \
 -filter_complex "\
[0:v]fps=30,settb=1/30[a];[1:v]fps=30,settb=1/30[b];[2:v]fps=30,settb=1/30[c];[3:v]fps=30,settb=1/30[d];\
[a][b]xfade=transition=fade:duration=${T}:offset=39.633[x1];\
[x1][c]xfade=transition=fade:duration=${T}:offset=74.266[x2];\
[x2][d]xfade=transition=fade:duration=${T}:offset=127.499[vout]" \
 -map "[vout]" -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 -pix_fmt yuv420p -r 30 video_montagem.mp4
echo "VIDEO OK"

# AUDIO: acrossfade encadeado (continuidade da fala)
ffmpeg -y -loglevel error \
 -i a1.wav -i a2.wav -i a3.wav -i a4.wav \
 -filter_complex "\
[0:a][1:a]acrossfade=d=${T}:c1=tri:c2=tri[m1];\
[m1][2:a]acrossfade=d=${T}:c1=tri:c2=tri[m2];\
[m2][3:a]acrossfade=d=${T}:c1=tri:c2=tri[aout]" \
 -map "[aout]" -c:a pcm_s24le audio_montagem.wav
echo "AUDIO OK"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 video_montagem.mp4
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 audio_montagem.wav
