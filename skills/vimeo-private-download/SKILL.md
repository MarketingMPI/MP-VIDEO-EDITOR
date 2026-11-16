---
name: vimeo-private-download
description: Use when yt-dlp fails on a Vimeo link; browser to HLS.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vimeo, video, download, yt-dlp, hls, browser]
    related_skills: [ffmpeg-video-editing, video-batch-transcription]
---

# Baixar vídeo privado/não listado do Vimeo

## When to Use

Use quando **qualquer** destes sintomas aparecer num link do Vimeo:

- O link é do formato `https://vimeo.com/<ID>/<HASH>` (não listado, com hash de acesso).
- `yt-dlp` responde *"The web client only works when logged-in"*.
- `curl` na config do player leva **403**.
- O link colado pelo usuário traz `?turnstile=...` na query.

Não use para vídeos públicos comuns do Vimeo/YouTube — nesses o `yt-dlp` direto resolve.
O conteúdo baixado deve ser material ao qual o usuário tem acesso legítimo.

O usuário fala português — responda em pt-BR.

## Por que o caminho direto falha

- `yt-dlp https://vimeo.com/<ID>/<HASH>` → *"The web client only works when logged-in"*.
- `yt-dlp --extractor-args "vimeo:client=android"` → **trava indefinidamente** (não espere; mate e siga).
- `curl .../config?h=<HASH>` → **403** (bot protection; é por isso que o link que o usuário cola às vezes traz `?turnstile=...`).

O que funciona: abrir o **player** num navegador real, ler o `var config = {...}` embutido na página e entregar o manifesto HLS ao yt-dlp.

## Procedimento

### 1. Abrir o player e salvar a config

Use `player.vimeo.com`, **não** `vimeo.com` (a config só está embutida no player):

```python
# browser_exec
import os, time
new_tab("https://player.vimeo.com/video/<ID>?h=<HASH>")
wait_for_load(); time.sleep(4)
print(page_info())   # o title já revela o nome do vídeo
ws = os.environ["BH_AGENT_WORKSPACE"]
# Preferir ler o objeto vivo: o player atual expõe window.playerConfig e o regex no HTML costuma falhar
r = js("window.playerConfig ? JSON.stringify(window.playerConfig) : null")
if not r:
    r = js("""(() => {
      const html = document.documentElement.innerHTML;
      const m = html.match(/var config = (\\{.+?\\});/s) || html.match(/window\\.playerConfig = (\\{.+?\\});/s);
      return m ? m[1] : "NOCONFIG:" + location.href;
    })()""")
open(os.path.join(ws, "cfg.json"), "w", encoding="utf-8").write(str(r))
```

O mesmo `config` traz `request.text_tracks` (legendas automáticas, ex. `pt-x-autogen`) — confira antes de planejar ASR.

**Vídeo embutido numa área de membros (Memberkit etc.):** a URL do player (com `?h=` quando houver) está no `src` do `<iframe>` da página da aula — abra a aula logada, leia `[...document.querySelectorAll('iframe')].map(f=>f.src)` e use esse URL aqui. Se o player responder "We couldn't verify the security of your connection" (Turnstile), o vídeo é restrito ao domínio; liste-o como pendente de verificação manual em vez de insistir em loop.

Sempre **`new_tab`**, nunca `goto_url` reaproveitando aba: a aba compartilhada pode migrar sozinha para outra página (já aconteceu de cair num `file:///...dev.html` local). Confirme em `page_info()` que a URL é a do player antes de confiar na config.

Não chame `capture_screenshot()` nessa página — o player do Vimeo faz `Page.captureScreenshot` estourar os 60s do daemon. `page_info()` basta.

### 2. Extrair a URL do manifesto

O regex captura lixo depois do JSON → `json.loads` falha com *"Extra data"*. Use `raw_decode`:

```python
# execute_code
import json
d, _ = json.JSONDecoder().raw_decode(open(CFG, encoding="utf-8").read())
first = list(d["request"]["files"]["hls"]["cdns"].values())[0]
u = first.get("avc_url") or first.get("url")
open(URLFILE, "w").write(u)
v = d.get("video", {})
print(v.get("title"), v.get("duration"), v.get("width"), v.get("height"))
```

Guarde `duration` — é o que valida o download no fim.

Antes de escolher o `-f`, liste as renditions reais do master playlist (precisa dos headers; sem eles vem 403):

```python
import urllib.request
req = urllib.request.Request(u, headers={
    "Referer": "https://player.vimeo.com/",
    "Origin": "https://player.vimeo.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0 Safari/537.36"})
for line in urllib.request.urlopen(req, timeout=60).read().decode().splitlines():
    if "RESOLUTION" in line:
        print(line.split("RESOLUTION=")[1].split(",")[0])
```

### 3. Baixar

`--batch-file` com o arquivo da URL evita que a query string gigante quebre o shell:

```bash
export PATH="$HOME/.local/bin:$PATH" && cd ~/Videos/vimeo && \
yt-dlp --referer "https://player.vimeo.com/" --add-header "Origin:https://player.vimeo.com" \
  -f "bv*[height<=720]+ba/b" --merge-output-format mp4 -N 8 --no-progress \
  -o "<Nome Sem Acento>.%(ext)s" --batch-file "$LOCALAPPDATA/hermes/cache/scratch/hls_url.txt"
```

- `--no-progress` é obrigatório: sem ele o log de fragmentos gera ~200k caracteres de ruído.
- Rode em `background=true, notify=true` — 1h de vídeo leva 3–5 min.
- Nomeie o arquivo sem acentos, preservando o número da série (`4 - Reuniao de Orcamento Conceito.mp4`).
- Sanitize o título para nome de arquivo Windows: `/ \ : * ? " < > |` são proibidos. Um título como `New Recording - 24/08/2023, 10:03:43` vira `New Recording - 2023-08-24 10-03-43`.
- Títulos repetidos dentro de uma série são normais (vários vídeos podem se chamar `Reunião de Orçamento Realizado`). O prefixo numérico do título é o que os distingue — nunca o descarte; a `duration` confirma que são vídeos diferentes.

**Escolha do `-f` pela rendition, não por hábito:** `-f "bv*[height<=720]+ba/b"` serve para a série 16:9 de 1280x720. Gravações de tela aparecem em formatos atípicos (ex.: 1366x574) onde um teto por altura pode descartar a melhor faixa — quando o topo do master já está no alvo ou abaixo dele, use `-f "bv*+ba/b"` e deixe o yt-dlp pegar o melhor.

### 4. Verificar antes de dizer que terminou

```bash
cd "$HOME/Videos/vimeo" && ffprobe -v error \
  -show_entries format=duration,size -show_entries stream=codec_type,codec_name,width,height \
  -of default=nw=1 "<arquivo>.mp4"
```

A `duration` tem que bater com a da config. Enquanto existirem `.part` / `.fNNN.mp4` na pasta, o download ainda está correndo.

`--no-progress` somado a `| tail -N` segura **toda** a saída até o processo sair: durante o download o log do processo em background volta vazio. Log vazio aí não significa falha — não reinicie o download por causa disso. A única verificação confiável é a pasta (`ls -la`) e o `ffprobe` no arquivo final.

Um vídeo de 2h leva ~8–10 min; os de ~1h, 3–5 min. Dimensione o `sleep` antes de checar, em vez de ficar sondando.

## Armadilhas do shell (Windows/bash)

- `~` **não** expande dentro de aspas: `ffprobe "~/Videos/.."` e `"$HOME/Videos/.."` falham com *No such file* para o ffprobe nativo. Faça `cd "$HOME/Videos/vimeo"` e passe o nome relativo.
- `ls -b` escapa os espaços com `\` — então `ls -b | grep "New Recording"` **não casa** e parece (falsamente) que o arquivo não existe. Para localizar arquivo com espaço no nome use `ls -la | grep <palavra>` ou um teste direto `[ -f "$f" ]`.

## Como reportar ao usuário

O usuário manda os links **um por vez** e espera o resultado antes do próximo. Depois de cada vídeo, entregue em poucas linhas:

1. Caminho absoluto do arquivo.
2. Resolução + codecs, duração (e que ela bate com a do original), tamanho.
3. A tabela acumulada da série até ali (`#`, arquivo, duração, tamanho) e o total em GB.

Não narre o download nem repita o log do yt-dlp. Quando a notificação de fim do processo em background chegar depois de você já ter validado com `ffprobe`, confirme em uma linha que o exit 0 é consistente com o que já foi verificado — sem refazer a checagem nem repetir a tabela.

## Validade dos links

O manifesto é assinado e expira em poucas horas (`exp=` na URL). Para cada vídeo novo, refaça o passo 1 — não reaproveite URL antiga.
