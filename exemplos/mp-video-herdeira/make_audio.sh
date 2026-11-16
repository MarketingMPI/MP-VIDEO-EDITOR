#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-herdeira"
D="C:/Users/phenr/Videos/Herdeira - MFO - Depoimento"

# Trata a voz de cada trecho: highpass, denoise neural (RNNoise), EQ presenca, de-esser leve,
# compressor, loudnorm por trecho. Depois concatena com crossfade curto (corte suave).
# Voz muito baixa (-31 a -38 LUFS) -> loudnorm puxa para -16.
voz() {
  local src="$1" ss="$2" to="$3" out="$4"
  ffmpeg -y -loglevel error -ss "$ss" -to "$to" -i "$D/$src.MOV" -vn \
   -af "highpass=f=90,arnndn=model=std.rnnn,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=2:g=2.5,equalizer=f=7500:t=q:w=3:g=-3,acompressor=threshold=-20dB:ratio=3:attack=8:release=180,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" \
   -ac 2 -ar 48000 "$out"
}

voz IMG_0241 28.0 68.0 a1.wav
voz IMG_0242 7.0 42.0 a2.wav
voz IMG_0244 13.6 67.2 a3.wav
voz IMG_0243 0.0 14.4 a4.wav

echo "vozes tratadas"
for a in a1 a2 a3 a4; do echo -n "$a: "; ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 $a.wav; done
