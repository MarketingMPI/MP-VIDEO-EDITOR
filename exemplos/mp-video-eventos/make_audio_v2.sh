#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-eventos"
D="C:/Users/phenr/Videos/Evento MFO"

# Total = 47.65s. NOVA trilha (cordas cinematograficas) + ambiente sutil. Sem whooshes/chime.

ffmpeg -y -loglevel error -ss 40 -t 48 -i "$D/Event 2.MOV" -vn -af "highpass=f=120,lowpass=f=6000,afftdn=nf=-20,volume=0.10,loudnorm=I=-30" -ac 2 -ar 48000 amb.wav

ffmpeg -y -loglevel error \
 -i trilha_evento_v2.wav \
 -i amb.wav \
 -filter_complex "\
[0:a]atrim=0:47.65,asetpts=PTS-STARTPTS,volume=1.0,afade=t=out:st=44.65:d=3[mus];\
[1:a]atrim=0:47.65,asetpts=PTS-STARTPTS,volume=0.42[amb];\
[mus][amb]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11,alimiter=limit=0.92,aresample=48000[aout]" \
 -map "[aout]" -c:a pcm_s24le audio_evento_v2.wav
echo "AUDIO v2 OK"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 audio_evento_v2.wav
