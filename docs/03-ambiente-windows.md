# 03 · Ambiente Windows

## O que precisa estar instalado

| Item | Versão usada | Observação |
|---|---|---|
| ffmpeg | 9.0.1 full | precisa dos filtros `whisper`, `arnndn`, `subtitles` (libass), `zscale`. Conferir: `ffmpeg -h filter=whisper` |
| Python | 3.x | `pip install pillow numpy scipy` |
| Node.js | 20+ | só para `npm install sharp` (SVG → PNG) |
| git-bash | — | todos os scripts `.sh` rodam nele |

Modelos (fora do git): `sh ferramentas/baixar-modelos.sh` baixa para `modelos/`:

- `ggml-large-v3-turbo.bin` (~1,6 GB) do repositório `ggerganov/whisper.cpp` no Hugging Face
- `std.rnnn` do repositório `richardpl/arnndn-models`

Fonte Campton: copiar os `.otf` para uma pasta `fonts/` **só com fontes** dentro do projeto.

## Armadilhas que já custaram tempo

1. **Caminhos.** O ffmpeg é programa Windows: nos argumentos use `C:/Users/...` (barra normal),
   nunca `/c/Users/...`. Já o `cd` do bash aceita `/c/...`.
2. **`fontsdir` só com fontes.** Se a pasta tiver o `std.rnnn` junto, o libass tenta abrir como
   fonte e enche o log de erro.
3. **Render pesado em primeiro plano estoura o tempo** e deixa um MP4 sem o índice final
   (ffprobe não lê duração). Rodar em segundo plano.
4. **Fonte `color` do ffmpeg é infinita**: dar `d=` e `r=` e usar `shortest=1` no overlay, senão
   o render nunca termina.
5. **`-ss` + fundo `color`**: aplicar `setpts=PTS-STARTPTS` em cada trecho de vídeo antes do
   overlay, senão o vídeo some e só aparece o fundo.
6. **SVG → PNG**: `cairosvg` não funciona no Windows (falta a cairo). Usar `sharp` no Node.
7. **Locale pt-BR**: o `printf "%.1f"` reclama de número com vírgula vindo do ffprobe. É cosmético.
8. **Whisper em arquivo longo desalinha os tempos.** Cortar o trecho antes, ou transcrever em
   blocos e somar o deslocamento de cada bloco.
