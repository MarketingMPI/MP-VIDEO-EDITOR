# 02 · Identidade e preferências

Tudo aqui foi pedido ou aprovado (ou recusado) em edições reais. Não reabrir sem pedido.

## Formato

- **Reels/Stories:** 1080×1920, 30 ou 60 fps, H.264 `yuv420p`, `+faststart`.
- **Aula/onboarding:** mantém o formato horizontal original, sem legenda, sem música, sem logo.
- **Áudio:** −14 LUFS integrado, pico ≤ −1 dBTP, AAC 48 kHz (192–256 kbps).

## Legenda

- Fonte **Campton** (Bold/SemiBold), **branca uniforme**, contorno escuro sutil + sombra leve,
  terço inferior, blocos de 2–3 palavras nos anúncios.
- **Recusado:** palavras-chave em verde, pergunta do entrevistador em itálico.
- **Sem travessão (—)**: usar vírgula, dois-pontos ou ponto.
- Corrigir à mão os erros do Whisper e confirmar nomes próprios antes de queimar
  (ex.: "achismo" sai "machismo"; "MPPRO" → "MP PRO").
- No Windows, o ASS precisa usar o nome PostScript da fonte (`Campton-Bold`) e conferir no log do
  ffmpeg (`fontselect`) que não caiu em Arial.

## Sticker de headline (anúncios)

- Imita o texto de Stories do Instagram: caixinha arredondada **por linha**, Segoe UI Bold.
- Texto = o gancho da fala. Aparece do início até o fim do gancho e sai com fade.
- Alternar a cor entre versões: **branco** (fundo 255,255,255 / texto 15,15,15), **preto**
  (24,24,24 / branco), **verde MP** (#00503c / branco).

## Trilha

- **Só piano clássico suave** (clima Satie/Gymnopédie), **bem baixo**.
- **Recusado:** synth/pad brilhante, cordas/violoncelo cinematográficos ("ficou horroroso"),
  efeitos de transição (whoosh), som ambiente do evento.
- Para variar entre vídeos: outra melodia de piano (`ferramentas/trilha/`), nunca outro instrumento.
- A música nunca some no meio do vídeo.

## Logo

- **Sem logo por padrão.** Quando pedido:
  - coruja branca MP com sombra, topo central;
  - **MP PRO** (cortes de live): logo dourada no rodapé central, `scale=360:-1`;
  - **Family Office Club**: discreta, rodapé central, ~290 px.

## Vinheta MP PRO (cortes de live)

- 1080×1920, fundo degradê radial preto (#262626 → #0a0a0a), logo dourada #E4D6A7, botão
  dourado com texto escuro "Faça sua inscrição agora", subtítulo "Formação + comunidade para consultores".
- Entra com crossfade de 0,8 s (nunca corte seco). Gerador: `ferramentas/graficos/make_vinheta_mppro.py`.

## Enquadramento

- Rosto centralizado, pouco espaço acima da cabeça, cabeça nunca cortada.
- Câmera frontal: `hflip` sempre (logo na camisa tem que ler certo).
- Câmera pequena de live: **não ampliar até pixelar**. Empilhar as duas câmeras ou usar o
  relatório da tela como destaque.
