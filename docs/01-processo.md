# 01 · O processo de edição, etapa por etapa

Este é o fluxo que funciona em **todo** tipo de vídeo. Os comandos completos e testados estão em
[`skills/ffmpeg-video-editing/references/ffmpeg-recipes.md`](../skills/ffmpeg-video-editing/references/ffmpeg-recipes.md).

> Regra de ouro: **testar cada etapa num trecho curto (5–10 s) e olhar o resultado antes de
> renderizar o vídeo inteiro.** Um render completo leva minutos; um erro descoberto no final custa
> o render todo de novo.

---

## 1. Investigar o arquivo

```sh
ffprobe -v error -show_streams -of json "C:/caminho/video.MOV"
```

O que procurar:

- **Resolução, fps e rotação.** Celular costuma gravar 4K 60 fps.
- **HDR?** Se `color_transfer` for `arib-std-b67` (HLG) ou `smpte2084` (PQ), o vídeo é HDR e
  **precisa** de conversão para SDR, senão as cores saem lavadas.
- **`start_time` do áudio e do vídeo.** Se forem diferentes, leia
  `references/av-sync-and-transcript-reconciliation.md` antes de cortar, ou a boca sai fora de sincronia.

## 2. Assistir pelos frames

Extrair JPGs em vários momentos e olhar: onde está o rosto, se alguém passa na frente, onde
começa o conteúdo útil, se a imagem está espelhada.

```sh
ffmpeg -ss 12 -i video.MOV -frames:v 1 -vf "drawgrid=w=iw/10:h=ih/10:t=2:c=red@0.6" f12.jpg
```

A grade ajuda a medir a posição do rosto em % para o reenquadramento 9:16.

## 3. Medir o áudio

```sh
ffmpeg -i video.MOV -af loudnorm=print_format=summary -f null - 2>&1 | tail -12
```

Anotar volume integrado (LUFS), pico (dBTP; acima de 0 = estourado) e LRA (acima de ~12 = precisa
de compressor). Gravação de evento costuma vir muito baixa (−31 a −38 LUFS); sobe tranquilo.

## 4. Cortar com decisão

Tirar bastidores, pergunta do entrevistador, começo obstruído. **Dizer ao usuário o que vai ser
cortado** para ele poder vetar. Em live longa, usar a transcrição por blocos
(`references/long-video-cut-identification.md`) para listar os melhores trechos com tempo exato.

Para anúncios: `ferramentas/cortes/build_cut.py` monta a expressão que remove **o meio** de cada
pausa, mantendo 0,12 s de folga em cada ponta (cortar a pausa inteira soa robótico).

## 5. Montar, na ordem

1. **Cor** · HDR → SDR: `zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p`
   + leve `eq=contrast=1.06:saturation=1.05:gamma=1.02`. Luz alaranjada de janela e LED verde de
   festa têm correções próprias (ver SKILL.md, seção Pitfalls).
2. **Enquadramento / zoom** · `zoompan` com curva de zoom suave nos momentos de ênfase
   (`ferramentas/montagem/zoom_punchin.py`). Rosto centralizado, pouco espaço acima da cabeça.
3. **Legenda** · Whisper → SRT → revisão manual dos erros → ASS em Campton
   (`ferramentas/legendas/`). Transcrever o trecho **já cortado**, não o arquivo inteiro.
4. **Sticker / logo / vinheta** · `ferramentas/graficos/`. Posição do sticker conferida num frame
   real de cada vídeo (o rosto muda de altura).
5. **Áudio** · RNNoise + EQ + compressor + `loudnorm=I=-14`; trilha de piano com ducking
   (`sidechaincompress`) por baixo da voz (`ferramentas/audio/tratar_voz_e_trilha.sh`).

## 6. Renderizar

- Render pesado **sempre em segundo plano** (foreground estoura o tempo e deixa MP4 corrompido).
- Anúncios: um encode só, direto do original, CRF 14 `veryslow`, AAC 256k.
- Depoimentos/montagens: renderizar cada segmento num MP4 próprio e juntar com o
  **concat demuxer** (`-f concat -safe 0 -i lista.txt -c copy`). Todos os segmentos com áudio a 48 kHz.
- Transições suaves (vinheta MP PRO) com `xfade` + `acrossfade`, 0,8 s.

## 7. Conferir

Ver [`04-qa-e-entrega.md`](04-qa-e-entrega.md).

## 8. Entregar

Copiar para `C:\Users\phenr\Downloads` **e** manter o master em `out/` do projeto (a pasta Downloads
é sincronizada pelo OneDrive e arquivos já sumiram de lá).

---

## Guias específicos (dentro da skill principal)

| Situação | Guia |
|---|---|
| Comandos prontos (cor, áudio, legenda, zoom, concat) | `references/ffmpeg-recipes.md` |
| Montagem de evento com transições e trilha | `references/event-montage.md` |
| Várias respostas → um depoimento contínuo | `references/seamless-multiclip-testimonial.md` |
| Achar cortes numa live longa | `references/long-video-cut-identification.md` |
| Live com tela compartilhada e câmeras pequenas | `references/screen-share-live-layouts.md` |
| Lote de anúncios falados | `references/talking-head-ad-clips.md`, `references/social-ad-vertical-batch.md` |
| Aula/onboarding horizontal e limpa | `references/clean-onboarding.md` |
| Narração sintética e "vídeo travando" | `references/narration-and-motion-qa.md` |
| Áudio fora de sincronia | `references/av-sync-and-transcript-reconciliation.md` |
