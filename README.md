# MP VIDEO EDITOR

**Como a Meu Patrimônio edita vídeos gravados de verdade: processo, skills, ferramentas e exemplos reais.**

Este repositório é o **manual de edição de vídeo** da MP. Ele cobre tudo que é filmagem real:
depoimentos de clientes, montagens de evento, anúncios gravados no celular, cortes de live e
aulas de onboarding. É o irmão do [MP MOTIONS](https://github.com/MarketingMPI/MP-MOTIONS), que
cuida dos vídeos animados em código.

Não é um repositório de vídeos prontos (vídeos, áudios e modelos pesados ficam fora do git). É o
que permite **refazer o processo inteiro** em outra máquina, por outra pessoa ou por outro agente
de IA.

> Não existe programa de edição (Premiere, CapCut etc.). Toda a edição é feita por um agente de IA
> (Hermes/Claude) rodando **ffmpeg**, guiado pelas **skills** desta pasta. A pessoa só aprova.

---

## 1. O que este editor faz

| Tipo de vídeo | Exemplo real | Skill que conduz |
|---|---|---|
| **Depoimento de cliente** (1 pessoa, 9:16) | Cliente 01 e 02, evento MFO | `ffmpeg-video-editing` |
| **Depoimento multiclipe** (várias respostas viram um monólogo) | Herdeira | `ffmpeg-video-editing` → `references/seamless-multiclip-testimonial.md` |
| **Montagem de evento** (vários clipes + transições + trilha) | Eventos MFO, JP Morgan, Salume | `ffmpeg-video-editing` → `references/event-montage.md` |
| **Anúncio falado pra câmera** (lote, celular) | Ads Mais Retorno, XP Inc, Polo Capital | `editar-ads-simples` |
| **Cortes de live** (achar os melhores trechos de 60–90 min) | Live Mais Retorno, Crédito Privado | `ffmpeg-video-editing` → `long-video-cut-identification.md` + `screen-share-live-layouts.md` |
| **Aula / onboarding** (horizontal, limpa, sem legenda) | Onboarding MP PRO | `ffmpeg-video-editing` → `references/clean-onboarding.md` |
| **Transcrever um lote de vídeos** | aulas, gravações | `video-batch-transcription` |
| **Baixar vídeo privado do Vimeo** | aulas de plataforma | `vimeo-private-download` |
| **Locução sintética PT-BR** (quando precisa narrar) | — | `voicestudio-local-tts` |

O que entra em cada edição (quando faz sentido): correção de cor (inclusive HDR do iPhone → SDR),
limpeza de voz com IA (RNNoise), corte de respiros, legenda queimada, sticker de headline estilo
Instagram, punch-ins (zoom dinâmico), trilha de piano baixinha, vinheta de encerramento e
normalização de volume para Reels (−14 LUFS).

---

## 2. As ferramentas

| Ferramenta | Para quê | Custo |
|---|---|---|
| **ffmpeg 9 (build full)** | todo o trabalho: corte, cor, áudio, legenda, render | grátis |
| **Whisper** (filtro `whisper` do ffmpeg, modelo `ggml-large-v3-turbo.bin`) | transcrição PT-BR para legendas e para achar trechos | grátis, roda local |
| **RNNoise** (`arnndn`, modelo `std.rnnn`) | remove ruído da voz (~20 dB melhor que filtro comum) | grátis |
| **Python + Pillow + numpy** | stickers, vinhetas, máscaras, trilha de piano gerada em código | grátis |
| **Node + sharp** | converter logos SVG → PNG com transparência | grátis |
| **Fonte Campton** | toda legenda/texto da marca MP | licença da MP, **não versionada aqui** |

Os modelos pesados (Whisper 1,6 GB e RNNoise) não ficam no git. Baixe com:

```sh
sh ferramentas/baixar-modelos.sh
```

---

## 3. As skills (o "cérebro" do processo)

As cópias oficiais estão em [`skills/`](skills/). Cada uma tem um `SKILL.md` com o passo a passo e
uma lista de **armadilhas já resolvidas** (para nunca errar duas vezes a mesma coisa).

| Skill | Quando dispara |
|---|---|
| `ffmpeg-video-editing` | **a principal**: qualquer edição de filmagem real. Tem 10 guias em `references/` |
| `editar-ads-simples` | lote de anúncios falados pra câmera (corte de respiros + legenda + sticker) |
| `video-batch-transcription` | transcrever vários vídeos de uma vez |
| `vimeo-private-download` | quando o `yt-dlp` não baixa um link do Vimeo |
| `voicestudio-local-tts` | gerar narração PT-BR local |

Para usar numa máquina com Hermes: copie `ffmpeg-video-editing` e `editar-ads-simples` para
`%LOCALAPPDATA%\hermes\skills\creative\` e as outras três para `%LOCALAPPDATA%\hermes\skills\media\`.

---

## 4. Como editar um vídeo novo (resumo)

> Passo a passo completo em [`docs/01-processo.md`](docs/01-processo.md).

```
 1. INVESTIGAR   ffprobe: resolução, fps, HDR?, rotação, início do áudio
 2. ASSISTIR     extrair frames e olhar: onde está o rosto, o que cortar
 3. MEDIR        volume (LUFS), pico, ruído
 4. CORTAR       decidir o trecho e mostrar a decisão antes de seguir
 5. MONTAR       cor → enquadramento/zoom → legenda → sticker/logo → áudio
                 (cada etapa testada num pedaço curto antes do render completo)
 6. RENDERIZAR   em segundo plano, qualidade alta, segmentos separados + concat
 7. CONFERIR     0 erros no decode, −14 LUFS, frames olhados um a um
 8. ENTREGAR     cópia em Downloads + master guardado em out/
```

Para começar uma pasta de trabalho nova já com as ferramentas dentro:

```sh
sh scripts/novo-projeto.sh mp-video-nome-do-projeto
```

---

## 5. Regras da casa (preferências já confirmadas)

1. **Vertical 1080×1920** para Reels/Stories; áudio **−14 LUFS**, pico ≤ −1 dBTP.
2. **Legenda branca uniforme em Campton**, contorno sutil, terço inferior. Sem cor por palavra,
   sem itálico, **sem travessão (—)**.
3. **Sem logo por padrão.** Só coloca se pedirem.
4. **Trilha = só piano clássico suave e baixo.** Nada de cordas, synth, efeitos de transição ou
   som ambiente do evento. Para variar entre vídeos, troca a melodia, não o instrumento.
5. **Câmera frontal vem espelhada**: aplicar `hflip` (o logo da camisa tem que ler certo).
6. **Nunca ampliar uma câmera pequena até pixelar.** Em live com câmeras miúdas, empilhar as duas.
7. **Um corte por vez, com aprovação** antes de seguir para o próximo.
8. **Tudo é conferido por medição e por imagem**, não no "acho que ficou bom".

Detalhes de identidade em [`docs/02-identidade-e-preferencias.md`](docs/02-identidade-e-preferencias.md).

---

## 6. Estrutura

```
mp-video-editor/
├─ README.md                          este arquivo
├─ docs/
│  ├─ 01-processo.md                  o pipeline completo, etapa por etapa
│  ├─ 02-identidade-e-preferencias.md marca, legenda, trilha, MP PRO
│  ├─ 03-ambiente-windows.md          instalação e armadilhas do Windows
│  ├─ 04-qa-e-entrega.md              checklist de conferência e entrega
│  └─ 05-projetos-realizados.md       o que já foi feito e onde está
├─ skills/                            as skills de IA que executam o processo
├─ ferramentas/                       scripts reutilizáveis, organizados por etapa
│  ├─ cortes/  legendas/  graficos/  trilha/  audio/
│  ├─ montagem/  render/  transcricao/  aula-onboarding/
│  └─ baixar-modelos.sh               baixa Whisper + RNNoise
├─ exemplos/                          os scripts reais de cada projeto já entregue
└─ scripts/novo-projeto.sh            cria uma pasta de trabalho nova
```

---

## 7. Pré-requisitos

- Windows + git-bash, **ffmpeg 9 full** (com `whisper`, `libass`, `zscale`), Python 3 com
  `pillow` e `numpy`, Node.js (só para `sharp`)
- Modelos baixados com `ferramentas/baixar-modelos.sh`
- Fonte Campton instalada ou copiada para `fonts/` do projeto (licença própria da MP)

---

*Material interno da Meu Patrimônio Investimentos. Os vídeos editados e as imagens das pessoas
filmadas são de responsabilidade da MP e não fazem parte deste repositório.*
