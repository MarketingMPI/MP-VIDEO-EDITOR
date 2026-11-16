#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-cliente01"

SRC="C:/Users/phenr/Videos/Evento MFO/Cliente 01.MOV"
SS=35.7
TO=102.5

# Curva de zoom: base 1.13 + gaussianas nos pontos de enfase (tempo = on/60)
Z="1.13+0.15*exp(-pow((on/60-10.0)/3.0,2))+0.12*exp(-pow((on/60-30.0)/3.2,2))+0.19*exp(-pow((on/60-41.0)/2.8,2))+0.22*exp(-pow((on/60-61.0)/3.2,2))"

VF="zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p,\
eq=contrast=1.06:saturation=1.05:gamma=1.02,\
zoompan=z='${Z}':x='iw*0.53-(iw/zoom/2)':y='ih*0.50-(ih/zoom/2)':d=1:s=1080x1920:fps=60,\
subtitles=legendas.ass:fontsdir=assets"

ffmpeg -y -stats -loglevel error \
 -ss $SS -to $TO -i "$SRC" \
 -i trilha.wav \
 -i assets/logo_mp_shadow.png \
 -filter_complex "\
[0:v]${VF}[base];\
[base][2:v]overlay=x=(W-w)/2:y=70:format=auto[vlogo];\
[vlogo]fade=t=in:st=0:d=0.6,fade=t=out:st=65.8:d=1.0[vout];\
[0:a]highpass=f=90,lowpass=f=9000,afftdn=nf=-24,\
acompressor=threshold=-20dB:ratio=3:attack=8:release=200,\
equalizer=f=180:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=2:g=2,\
loudnorm=I=-14.5:TP=-1.5:LRA=11[voz];\
[1:a]atrim=0:66.8,asetpts=PTS-STARTPTS,volume=0.15,afade=t=in:st=0:d=2,afade=t=out:st=63:d=3.5[bg];\
[voz][bg]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=400[ducked];\
[voz][ducked]amix=inputs=2:weights=1 1:normalize=0,\
alimiter=limit=0.95:level=disabled,aresample=48000[aout]" \
 -map "[vout]" -map "[aout]" \
 -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 19 -pix_fmt yuv420p \
 -x264-params "keyint=120:min-keyint=60" \
 -c:a aac -b:a 192k -ar 48000 \
 -movflags +faststart \
 "Cliente01_MP_editado.mp4"

echo "RENDER OK"
ls -la Cliente01_MP_editado.mp4
