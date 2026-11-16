#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-cliente01"
SRC="C:/Users/phenr/Videos/Evento MFO/Cliente 01.MOV"

# Voz com RNNoise (denoise neural, ~20dB de reducao) + polimento.
# Trilha classica baixa, abertura discreta (0-6.7s so trilha), voz entra em 6.7s.

ffmpeg -y -loglevel error \
 -ss 35.7 -to 102.5 -i "$SRC" \
 -i trilha_classica.wav \
 -filter_complex "\
[0:a]highpass=f=80,arnndn=model=std.rnnn,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=8:release=200,equalizer=f=180:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=2:g=2,loudnorm=I=-14:TP=-1.5:LRA=11,adelay=6700|6700,apad=whole_dur=73.5,asplit=2[voz_mix][voz_sc];\
[1:a]atrim=0:73.5,asetpts=PTS-STARTPTS,volume=0.16,afade=t=in:st=0:d=3.0,afade=t=out:st=69.0:d=4.0[bg];\
[bg][voz_sc]sidechaincompress=threshold=0.03:ratio=8:attack=8:release=450[bg_duck];\
[voz_mix][bg_duck]amix=inputs=2:weights=1 1:normalize=0,alimiter=limit=0.95:level=disabled,aresample=48000[aout]" \
 -map "[aout]" -c:a pcm_s16le audio_final4.wav
echo "AUDIO4 OK"
