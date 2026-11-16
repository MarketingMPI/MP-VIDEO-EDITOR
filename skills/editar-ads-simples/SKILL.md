---
name: editar-ads-simples
description: "Editar ads verticais MP: cortes, legenda, headline sticker."
---

# Editar Ads Simples (MP — anúncios verticais para live/campanha)

Edição LEVE e rápida de vídeos de anúncio verticais (fala direto pra câmera,
gravados no celular) para Meu Patrimônio: cortar respiros/silêncios pra ficar
dinâmico, legenda estilo Reels, e uma HEADLINE em estilo sticker de texto do
Instagram (parece post orgânico, não anúncio). Validado na campanha "Ads Live
Mais Retorno" (MP PRO) — 11 vídeos, 5 COPYs.

## Quando usar
- Lote de ads verticais 720x1280 / 1080x1920, uma pessoa falando pra câmera.
- Pedido do tipo "edição simples: legenda, cortes pra tirar os respiros, deixar
  dinâmica" + "headline com fonte oficial do Instagram pra parecer post normal".
- NÃO confundir com testemunhal/evento (esse é `mp-client-testimonial-video`).
  Este aqui é mais leve: sem trilha, sem punch-ins, sem correção de cor pesada.

## Preferências do usuário (confirmadas, não relearnar)
- **hflip SEMPRE**: os vídeos vêm ESPELHADOS (câmera frontal). O logo "Meu
  Patrimônio" na camisa/polo fica invertido ("oinômirtaP"). Aplicar `hflip` em
  TODOS. Confirmar num frame com vision antes de renderizar.
- **Headline = sticker de texto do Instagram Stories**: caixinhas arredondadas
  POR LINHA, fonte Segoe UI Bold (`C:/Windows/Fonts/segoeuib.ttf`, imita a
  Instagram Sans). Texto = o GANCHO da fala (transcrever primeiro, propor o
  texto). Aparece de 0 até o fim do gancho e SAI COM FADE. Fica no terço
  superior, ACIMA da cabeça, sem cobrir o rosto (validar posição por vision).
- **ALTERNAR a cor do bloco entre versões** pra não ficar tudo igual: branco
  (BG 255,255,255 / texto 15,15,15), preto (BG 24,24,24 / texto branco), verde
  MP (BG 0,80,60 = #00503c / texto branco). Ex.: VS01 branco, VS02 preto, VS03
  verde, VS04 branco.
- **Legenda**: Campton branca UNIFORME estilo Reels (2-3 palavras/bloco),
  contorno/sombra sutil, terço inferior. Fontes em `~/Downloads/campton full/`.
  SEM cores por palavra, SEM itálico. Corrigir erros do whisper à mão (ex.:
  "achismo" que sai como "machismo"; "MPPRO" vira "MP PRO").
- **Áudio**: normalizar a -14 LUFS (Reels). **Render qualidade máxima**: CRF 14,
  preset veryslow, AAC 256k, DIRETO DO ORIGINAL (um só encode).
- **Entregar** os finais em `C:\Users\phenr\Downloads` com nome
  `COPY0N_VS0M_editado.mp4`.

## Pré-requisitos
- ffmpeg 9 full (whisper + libass + zscale). Modelo whisper:
  `ggml-large-v3-turbo.bin` (copiar de `~/mp-video-cliente01/` ou baixar do HF).
- Pasta de trabalho: `~/mp-ads-maisretorno/` (assets/ com as .otf Campton).
- ffmpeg é programa Windows nativo sob MSYS: passar caminhos `C:/...`
  forward-slash nos args (NÃO `/c/...`); `cd` a caminho MSYS é ok.

## Pipeline por vídeo (a ordem que funciona)
1. **Probe**: `ffprobe` codec/res/fps/duration. (Ads costumam ser 720x1280 30fps
   H264 SDR bt709 — sem HDR, edição leve.)
2. **Extrair áudio p/ ASR** e **detectar silêncios**:
   ```
   ffmpeg -y -i "IN.MOV" -vn -af "highpass=f=85,lowpass=f=7500,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5" -ac 1 -ar 16000 asr.wav
   ffmpeg -i asr.wav -af "silencedetect=noise=-30dB:d=0.35" -f null - 2>&1 | grep silence_
   ```
3. **Transcrever o ORIGINAL** (background) pra decidir a headline:
   `whisper=model=...:language=pt:format=srt:destination=out.srt:max_len=32:queue=90:use_gpu=false`
4. **Montar expressão de corte**: remover o MIOLO de cada pausa mantendo 0.12s de
   folga em cada ponta (pad). Silêncio inicial (start=0): aparar do 0. Ver
   scripts/build_cut.py.
5. **Cortar (select/aselect num só passe)** pra preservar sync — gera cutNN.mp4
   (encode leve crf18 medium, áudio pcm). NÃO aplicar hflip aqui ainda.
6. **Transcrever o CORTADO** (background) para SRT em sync perfeito com o corte.
7. **Gerar sticker** (Pillow, scripts/make_sticker.py) com o gancho, na cor da
   vez. Validar posição num frame REAL (com hflip) por vision; ajustar y%
   (0.015 a 0.06) conforme a altura do rosto.
8. **Gerar legenda ASS** (scripts/srt_to_ass.py) — Campton branca, blocos de 2-3
   palavras. Corrigir erros do whisper.
9. **Render final DIRETO DO ORIGINAL** (corte + hflip + sticker + legenda +
   áudio -14 LUFS), CRF14 veryslow AAC256k. Ver scripts/render_final.sh.
10. **Verificar integridade** (`ffmpeg -v error -i out -f null -` = 0 erros),
    copiar pra Downloads, conferir frame final por vision (logo correto? sticker
    ok? legenda ok?).

## Pitfalls (todos já resolvidos)
- Esquecer o hflip = logo espelhado. O usuário PEGA isso na hora. hflip sempre.
- Sticker cobrindo o cabelo em enquadramento fechado: baixar o y% e validar por
  vision ANTES de renderizar (não assumir 0.11 fixo).
- Whisper erra palavra/proper noun: revisar SRT do corte antes de queimar.
- Timestamps do whisper só ficam confiáveis se transcrever a versão JÁ CORTADA
  (não remapear os tempos do original).
- Render em 2 gerações (cortar depois reencodar com legenda) perde qualidade: o
  render final lê o ORIGINAL e aplica corte+tudo num só encode CRF14.
- `float` no agrupamento de palavras da legenda: usar int() nos tempos.

## Assets reutilizáveis
- Pasta de trabalho persiste em `~/mp-ads-maisretorno/` (modelo whisper, fontes,
  stickers). Scripts parametrizados em scripts/.
