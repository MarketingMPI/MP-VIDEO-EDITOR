#!/bin/sh
# Cria uma pasta de trabalho nova para uma edicao, com as ferramentas copiadas.
# Uso: sh scripts/novo-projeto.sh mp-video-nome [pasta_pai]
#   pasta_pai padrao: $HOME
set -e
NOME="$1"
[ -z "$NOME" ] && { echo "Uso: sh scripts/novo-projeto.sh mp-video-nome [pasta_pai]"; exit 1; }
PAI="${2:-$HOME}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
P="$PAI/$NOME"
[ -e "$P" ] && { echo "Ja existe: $P"; exit 1; }

mkdir -p "$P"/out "$P"/frames "$P"/fonts "$P"/assets "$P"/srt
cp -r "$REPO/ferramentas" "$P/ferramentas"
rm -f "$P/ferramentas/README.md"

# modelos: reaproveita os ja baixados no repo, se existirem
if [ -s "$REPO/modelos/std.rnnn" ]; then cp "$REPO/modelos/std.rnnn" "$P/assets/"; fi

# fontes Campton (licenca MP, fora do git): copia das pastas conhecidas desta maquina
# (a pasta do Downloads perdeu os pesos Bold/SemiBold no OneDrive; os projetos tem o jogo completo)
for CAMPTON in "$CAMPTON_DIR" "$HOME/mp-live-maisretorno/fonts" "$HOME/mp-video-cliente01/assets" "$HOME/Downloads/campton full"; do
  [ -n "$CAMPTON" ] && [ -d "$CAMPTON" ] && cp -n "$CAMPTON"/Campton*.otf "$P/fonts/" 2>/dev/null || true
done
[ -f "$P/fonts/CamptonBold.otf" ] || echo "Aviso: CamptonBold.otf nao encontrada. Defina CAMPTON_DIR=/caminho/das/fontes."

cat > "$P/NOTAS.md" <<EOF
# $NOME

- Fonte(s) do video:
- Tipo: depoimento | montagem de evento | anuncio | corte de live | aula
- Trecho escolhido / decisoes de corte:
- Entregas (out/ e Downloads):
EOF

echo "Projeto criado em: $P"
echo "Proximo passo: ffprobe no video bruto (docs/01-processo.md, etapa 1)."
[ -s "$P/assets/std.rnnn" ] || echo "Aviso: rode 'sh ferramentas/baixar-modelos.sh' no repo para ter o std.rnnn e o Whisper."
