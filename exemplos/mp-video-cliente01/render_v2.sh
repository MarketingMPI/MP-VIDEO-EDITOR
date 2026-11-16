#!/bin/bash
set -e
cd "/c/Users/phenr/mp-video-cliente01"

SRC="C:/Users/phenr/Videos/Evento MFO/Cliente 01.MOV"

# --- TEMPOS ---
# Audio continuo: 29.0s -> 102.5s do original  = 73.5s total
# Segmento A (still): novo 0 -> 6.7s   (corresponde a audio 29.0 -> 35.7)
# Segmento B (live):  novo 6.7 -> 73.5 (corresponde a audio 35.7 -> 102.5, dur 66.8s)
A_SRC=29.0
A_DUR=6.7
B_SS=35.7
B_TO=102.5

# Zoom Ken Burns no still (lento, 1.06 -> 1.14) centrado no rosto
KB="1.06+0.0002*on"

# Zoom do depoimento (fase B): base 1.13 + punch-ins (tempo T = on/60 no seg B)
ZB="1.13+0.15*exp(-pow((on/60-9.6)/3.0,2))+0.12*exp(-pow((on/60-29.6)/3.2,2))+0.19*exp(-pow((on/60-40.6)/2.8,2))+0.22*exp(-pow((on/60-60.6)/3.2,2))"

VF_COL="zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p,eq=contrast=1.06:saturation=1.05:gamma=1.02"

ffmpeg -y -loglevel error \
 -loop 1 -framerate 60 -t $A_DUR -i hero_4k.png \
 -ss $B_SS -to $B_TO -i "$SRC" \
 -ss $A_SRC -to $B_TO -i "$SRC" \
 -i trilha.wav \
 -i assets/logo_mp_shadow.png \
 -filter_complex "\
[0:v]scale=2160:3840,zoompan=z='${KB}':x='iw*0.53-(iw/zoom/2)':y='ih*0.47-(ih/zoom/2)':d=1:s=1080x1920:fps=60,setpts=PTS-STARTPTS[segA];\
[1:v]${VF_COL},zoompan=z='${ZB}':x='iw*0.53-(iw/zoom/2)':y='ih*0.50-(ih/zoom/2)':d=1:s=1080x1920:fps=60,setpts=PTS-STARTPTS[segB];\
[segA][segB]concat=n=2:v=1:a=0[vid];\
[vid]subtitles=legendas_v2.ass:fontsdir=assets[vsub];\
[vsub][4:v]overlay=x=(W-w)/2:y=70:format=auto[vlogo];\
[vlogo]fade=t=in:st=0:d=0.6,fade=t=out:st=72.5:d=1.0[vout];\
[2:a]highpass=f=90,lowpass=f=9000,afftdn=nf=-24,acompressor=threshold=-20dB:ratio=3:attack=8:release=200,equalizer=f=180:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=2:g=2,loudnorm=I=-15:TP=-1.5:LRA=11,asplit=2[voz1][voz2];\
[3:a]atrim=0:73.5,asetpts=PTS-STARTPTS,volume=0.14,afade=t=in:st=0:d=2.5,afade=t=out:st=69.5:d=3.5[bg];\
[voz1][bg]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=400[ducked];\
[voz2][ducked]amix=inputs=2:weights=1 1:normalize=0,alimiter=limit=0.95,aresample=48000[aout]" \
 -map "[vout]" -map "[aout]" \
 -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 19 -pix_fmt yuv420p \
 -x264-params "keyint=120:min-keyint=60" \
 -c:a aac -b:a 192k -ar 48000 \
 -movflags +faststart \
 "Cliente01_MP_editado_v2.mp4"

echo "RENDER V2 OK"
ls -la Cliente01_MP_editado_v2.mp4
