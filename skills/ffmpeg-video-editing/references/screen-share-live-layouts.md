# Lives com screen-share: preservação de qualidade e layouts 9:16

Use esta referência ao transformar lives/webinars 16:9 com tela compartilhada e webcams laterais em cortes verticais.

## Gate de qualidade antes de escolher o layout

Meça o crop nativo da webcam antes de ampliá-lo. Não julgue apenas pelo frame final reduzido no preview.

- Webcam grande (aprox. 500–700 px de largura na fonte 1280×720): pode virar talking-head vertical com fundo desfocado.
- Webcam pequena de screen-share (aprox. 140–240 px): **nunca ampliar para preencher 1080 px**. Um upscale de 4–7× destrói detalhe facial e foi rejeitado pelo usuário.
- Para webcam pequena, limite o upscale visual usando uma janela de 360–500 px de largura ou duas janelas empilhadas com bastante contexto interno.
- Antes do render completo, exporte um frame real já na resolução final e confirme nitidez, cabeça inteira, ausência de bordas pretas e nametag íntegro.

## Árvore de decisão

### 1. A tela compartilhada é relevante à fala
Use **relatório herói**:

- Crop do conteúdo sem navegador, taskbar e webcams.
- Relatório no topo, normalmente 1020–1060 px de largura.
- Webcam pequena do orador como PiP arredondado de 360–500 px, sem tentar preencher o quadro.
- Legendas no espaço inferior e logo no rodapé.
- Se houver headline sticker, reduza-o e valide que não cobre o cabeçalho do relatório. O conteúdo deve começar abaixo do sticker; em páginas roladas, aceite apenas cortes inevitáveis do material-fonte, nunca cortes criados pela composição.

Receita de máscara arredondada:

```text
[src]crop=224:170:X:Y,scale=360:274,format=rgba[camraw];
[mask]format=gray[m];
[camraw][m]alphamerge,scale=460:-1[cam]
```

Preserve a proporção do crop e da máscara. Uma máscara validada nesta live foi 360×274.

### 2. A tela compartilhada não é relevante à fala
Use **duas câmeras empilhadas**, nunca o zoom full-screen da webcam pequena:

- Gabriel/orador ou host em cima; convidado/ouvinte embaixo, conforme a dinâmica.
- Fundo sólido escuro.
- Janelas finais idênticas, por exemplo 940×600, com gap suficiente.
- Legenda sobre a base da câmera inferior (`MarginV` perto de 400–430), sem colidir com a logo.
- Nametags completos são preferíveis; se o nametag pequeno ficar cortado, remova-o por inteiro em vez de mostrar um fragmento.

### 2b. A live já está em duas câmeras grandes lado a lado

As câmeras grandes de uma fonte 1280×720 (aprox. 500–700 px de largura por
participante) permitem duas composições seguras:

- **Um orador conduz todo o arco:** isole sua câmera e use talking-head vertical,
  com uma cópia desfocada da mesma câmera preenchendo o fundo. Valide que o crop
  contém cabeça, torso/gestos e nametag; essa fonte suporta a ampliação, ao
  contrário de uma webcam pequena de screen-share.
- **Há alternância de fala ou as reações do ouvinte importam:** mantenha os dois
  participantes empilhados. Host em cima e convidado embaixo é uma geometria
  estável para uma série de cortes.

Se o modo da fonte não muda durante o clipe, preserve a proporção de cada câmera
com `scale=940:-1` em vez de forçar 940×600. Isso mantém as laterais e os nametags
completos. Posições validadas em 1080×1920: primeira câmera perto de `y=300`,
segunda perto de `y=900`; a área abaixo da segunda recebe a legenda e a logo.
Use a normalização fixa 940×600 somente quando for necessário reconciliar fases
com geometrias de fonte diferentes.

### 3. A live muda de screen-share para câmeras grandes no meio
Trate em fases:

1. Localize a troca por frames de 1s e refine o segundo exato.
2. Renderize cada fase só-vídeo com crops próprios.
3. Force cada janela para a mesma geometria final:

```text
scale=940:600:force_original_aspect_ratio=increase,crop=940:600
```

4. Use os mesmos `overlay x/y` nas duas fases.
5. Concatene as fases com concat demuxer.
6. Aplique áudio, sticker, legendas e logo apenas depois, sobre o vídeo unificado.

## Dense reports, scrolling pages, and legibility

A screen-share crop that is good at one timestamp may cut the key data after the
presenter scrolls. Validate the SAME crop on at least the beginning, numerical
reveal, and ending of the selected segment.

- Crop whitespace and app chrome aggressively, but keep every label needed to
  interpret the numbers. Prefer a tighter common crop over shrinking the whole
  desktop into the Reel.
- For a four-column comparison, verify all column headings, bottoms, and the
  largest percentages after scaling to the final 1080×1920 canvas.
- The visible report may change while the audio continues. That is acceptable
  only when the changing page still supports the spoken point; otherwise switch
  to stacked cameras rather than showing unrelated material.
- A temporary headline sticker must end above the report. Test it on a real
  opening frame; reducing the sticker is better than hiding the report title.
- Avoid ending on the first words of the next thought (for example, “aí eu
  pedi…”). Trim at the last complete claim, then rebuild/remove the trailing
  subtitle block.
- Count the closing vinheta in the requested duration. With a 4.0s vinheta and a
  0.8s crossfade, the final duration is `content + 3.2s`; keep the spoken segment
  short enough that the delivered file still meets the limit.

## PTS ao combinar vídeo com fundo lavfi

Quando o fundo `color` começa em t=0 e o vídeo foi aberto com `-ss`, os timestamps podem não se sobrepor; o resultado fica vazio, mostrando somente o fundo. Sempre normalize cada crop:

```text
setpts=PTS-STARTPTS
```

Faça isso antes de cada overlay.

## Checklist visual obrigatório

- [ ] Nenhuma webcam pequena foi ampliada para full-screen.
- [ ] Rosto e cabeça inteiros; sem corte no topo.
- [ ] Sem borda preta lateral ou faixa residual do nametag anterior.
- [ ] Nametag inteiro ou totalmente removido.
- [ ] Relatório sem navegador/taskbar e com seus dados principais legíveis.
- [ ] Sticker não cobre o relatório, o rosto ou o cabeçalho.
- [ ] Legenda não colide com nametag/logo.
- [ ] Frame do início, frame central, troca de layout e crossfade final verificados.
- [ ] Entrega validada com `ffmpeg -v error -i arquivo.mp4 -f null -`.
