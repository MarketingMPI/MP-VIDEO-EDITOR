#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-cliente01"
SRC="C:/Users/phenr/Videos/Evento MFO/Cliente 01.MOV"

# Audio 29.0 -> 102.5s (73.5s). Voz tratada + trilha duckada PELA voz.
ffmpeg -y -loglevel error \
 -ss 29.0 -to 102.5 -i "$SRC" \
 -i trilha.wav \
 -filter_complex "\
[0:a]highpass=f=90,lowpass=f=9000,afftdn=nf=-24,acompressor=threshold=-20dB:ratio=3:attack=8:release=200,equalizer=f=180:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=2:g=2,loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[voz_mix][voz_sc];\
[1:a]atrim=0:73.5,asetpts=PTS-STARTPTS,volume=0.30,afade=t=in:st=0:d=2.5,afade=t=out:st=69.5:d=3.5[bg];\
[bg][voz_sc]sidechaincompress=threshold=0.03:ratio=10:attack=5:release=350[bg_duck];\
[voz_mix][bg_duck]amix=inputs=2:weights=1 1:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95,aresample=48000[aout]" \
 -map "[aout]" -c:a pcm_s16le audio_final.wav
echo "AUDIO OK"
