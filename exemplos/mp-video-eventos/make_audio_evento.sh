#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-eventos"
D="C:/Users/phenr/Videos/Evento MFO"

# Total = 47.65s. SEM whooshes/chime. So trilha classica + ambiente sutil do evento.

ffmpeg -y -loglevel error -ss 40 -t 48 -i "$D/Event 2.MOV" -vn -af "highpass=f=120,lowpass=f=6000,afftdn=nf=-20,volume=0.10,loudnorm=I=-30" -ac 2 -ar 48000 amb.wav

ffmpeg -y -loglevel error \
 -i trilha_evento.wav \
 -i amb.wav \
 -filter_complex "\
[0:a]atrim=0:47.65,asetpts=PTS-STARTPTS,volume=1.0,afade=t=out:st=44.65:d=3[mus];\
[1:a]atrim=0:47.65,asetpts=PTS-STARTPTS,volume=0.5[amb];\
[mus][amb]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11,alimiter=limit=0.92,aresample=48000[aout]" \
 -map "[aout]" -c:a pcm_s24le audio_evento.wav
echo "AUDIO SEM SFX OK"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 audio_evento.wav
