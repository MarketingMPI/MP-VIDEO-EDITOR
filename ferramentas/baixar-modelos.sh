#!/bin/sh
# Baixa os modelos pesados que NAO ficam no git:
#   - Whisper large-v3-turbo (transcricao PT-BR, ~1,6 GB)
#   - RNNoise std.rnnn (limpeza de voz do filtro arnndn)
# Uso: sh ferramentas/baixar-modelos.sh [pasta_destino]   (padrao: ./modelos)
set -e
DEST="${1:-modelos}"
mkdir -p "$DEST"

if [ ! -s "$DEST/ggml-large-v3-turbo.bin" ]; then
  echo "Baixando Whisper large-v3-turbo (~1,6 GB)..."
  curl -L --fail -o "$DEST/ggml-large-v3-turbo.bin" \
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin?download=true"
else
  echo "Whisper ja existe em $DEST"
fi

if [ ! -s "$DEST/std.rnnn" ]; then
  echo "Baixando RNNoise std.rnnn..."
  curl -L --fail -o "$DEST/std.rnnn" \
    "https://raw.githubusercontent.com/richardpl/arnndn-models/master/std.rnnn"
else
  echo "std.rnnn ja existe em $DEST"
fi

ls -l "$DEST"
echo "Pronto. No ffmpeg use: whisper=model=$DEST/ggml-large-v3-turbo.bin  e  arnndn=model=$DEST/std.rnnn"
