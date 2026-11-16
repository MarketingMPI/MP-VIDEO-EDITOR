#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-cliente02"
SRC="C:/Users/phenr/Videos/Evento MFO/Cliente 02.MOV"

# Depoimento: 24.6 -> 40.2s (15.6s). Voz deslocada para comecar em 5.5s (apos still).
# Abertura (0-5.5s) = so trilha classica baixa. Total = 5.5 + 15.6 = 21.1s.
# Voz com RNNoise (denoise neural). Loudnorm -14 (audio original estava baixo, -20 LUFS).

ffmpeg -y -loglevel error \
 -ss 24.6 -to 40.2 -i "$SRC" \
 -i trilha_classica.wav \
 -filter_complex "\
[0:a]highpass=f=80,arnndn=model=std.rnnn,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=8:release=200,equalizer=f=180:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=2:g=2,loudnorm=I=-14:TP=-1.5:LRA=11,adelay=5500|5500,apad=whole_dur=21.1,asplit=2[voz_mix][voz_sc];\
[1:a]atrim=0:21.1,asetpts=PTS-STARTPTS,volume=0.16,afade=t=in:st=0:d=2.5,afade=t=out:st=17.5:d=3.0[bg];\
[bg][voz_sc]sidechaincompress=threshold=0.03:ratio=8:attack=8:release=450[bg_duck];\
[voz_mix][bg_duck]amix=inputs=2:weights=1 1:normalize=0,alimiter=limit=0.85:level=disabled,aresample=48000[aout]" \
 -map "[aout]" -c:a pcm_s16le audio_c02.wav
echo "AUDIO C02 OK"
