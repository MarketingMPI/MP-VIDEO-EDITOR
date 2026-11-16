#!/usr/bin/env bash
# Render final DIRETO DO ORIGINAL (um so encode, qualidade maxima).
# corte(select/aselect) + hflip + sticker(fade) + legenda ASS + audio -14 LUFS.
#
# Uso:
#   IN="C:/.../COPY0N_VS0M.MOV"   OUT="COPY0N_VS0M_editado.mp4"
#   KEEP='not(between(t\,...)+...)'   (do build_cut.py)
#   STK=sticker0N.png   ASS=legendas0N.ass
#   STK_Y=0.04          # y% do sticker (0.015..0.06 conforme altura do rosto)
#   STK_OUT=5.3         # segundo em que o sticker some (fim do gancho + fade)
#   bash render_final.sh
set -e
STK_FADE=$(python -c "print(max(0.0, ${STK_OUT}-0.4))")
ffmpeg -y -loglevel error -i "$IN" -i "$STK" -filter_complex "\
[0:v]select='$KEEP',setpts=N/FRAME_RATE/TB,hflip[vc];\
[1:v]format=rgba,fade=t=out:st=${STK_FADE}:d=0.4:alpha=1[st];\
[vc][st]overlay=x=(W-w)/2:y=H*${STK_Y}:enable='between(t,0,${STK_OUT})'[vst];\
[vst]subtitles=${ASS}:fontsdir=assets[vout];\
[0:a]aselect='$KEEP',asetpts=N/SR/TB,highpass=f=80,afftdn=nf=-22,acompressor=threshold=-20dB:ratio=3:attack=8:release=200,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95,aresample=48000[aout]" \
-map "[vout]" -map "[aout]" -c:v libx264 -profile:v high -level 4.1 -preset veryslow -crf 14 \
-pix_fmt yuv420p -x264-params "keyint=60:min-keyint=30" -c:a aac -b:a 256k -ar 48000 \
-movflags +faststart "$OUT"
echo "render exit=$?"
ffmpeg -v error -i "$OUT" -f null - && echo "INTEGRIDADE_OK (0 erros)"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
