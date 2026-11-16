#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-jpmorgan"
D="C:/Users/phenr/Videos/Evento MFO - Menina do JP Morgan"

# Total video ~69.87s. Trilha classica + ambiente sutil do evento (burburinho do IMG_0961).

ffmpeg -y -loglevel error -ss 240 -t 70 -i "$D/IMG_0961.MOV" -vn -af "highpass=f=120,lowpass=f=6000,afftdn=nf=-20,volume=0.12,loudnorm=I=-30" -ac 2 -ar 48000 amb.wav

ffmpeg -y -loglevel error \
 -i trilha_jp.wav \
 -i amb.wav \
 -filter_complex "\
[0:a]atrim=0:69.87,asetpts=PTS-STARTPTS,volume=1.0,afade=t=in:st=0:d=2.5,afade=t=out:st=66:d=3.8[mus];\
[1:a]atrim=0:69.87,asetpts=PTS-STARTPTS,volume=0.5,afade=t=in:st=0:d=3,afade=t=out:st=66:d=3.8[amb];\
[mus][amb]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11,alimiter=limit=0.92,aresample=48000[aout]" \
 -map "[aout]" -c:a pcm_s24le audio_jp.wav
echo "AUDIO OK"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 audio_jp.wav
