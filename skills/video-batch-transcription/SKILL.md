---
name: video-batch-transcription
description: Use when transcribing a batch of videos to text.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [transcription, ffmpeg, whisper, video, asr]
    related_skills: [youtube-content, ffmpeg-video-editing]
---

# Batch video → text (local ASR)

## When to Use

Use when the ask is "assista aos vídeos e me resuma", "pegue o conteúdo dessas aulas",
"transcreva esses cortes" — i.e. the deliverable depends on what is SAID across a set of
videos (course, lives, cortes) and there is no usable caption track. The output is one `.txt`
per video that you then read and synthesize. Do not describe a video you never transcribed.
For a single YouTube URL whose captions are public, use the platform transcript instead.

**Check for an existing transcript first.** Platform auto-captions (YouTube, Kiwify
`video.subtitles[]`, a `.vtt` declared in the HLS master playlist) are free and instant. Only
fall through to ASR when `subtitles[]` comes back empty and the master `.m3u8` declares no
`SUBTITLES` group. A platform setting saying "legendas automáticas ativas" does **not** mean a
fetchable file exists — check the payload, not the toggle.

**YouTube (inclusive não listado): puxe a legenda automática em lote antes de qualquer ASR.**

```bash
yt-dlp --skip-download --write-auto-subs --write-subs --sub-langs "pt-orig,pt" --sub-format vtt \
  --no-progress --ignore-errors --sleep-requests 1.5 --sleep-subtitles 3 \
  --print-to-file "%(id)s	%(upload_date)s	%(availability)s	%(duration)s	%(channel)s	%(title)s" meta.tsv \
  -o "%(id)s.%(ext)s" -a ids.txt
```

- Peça só `pt-orig,pt`: `pt.*` também baixa `pt-PT` etc. e dispara **HTTP 429**; os sleeps evitam o bloqueio.
- O `meta.tsv` dá data de upload e `unlisted/public` de graça — evidência útil para datar conteúdo.
- VTT automático repete cada linha em janelas rolantes: deduplique linhas consecutivas e agrupe por blocos de ~30 s com `[hh:mm:ss]` antes de ler.
- Só os vídeos sem legenda vão para ASR: `yt-dlp -f ba -x --audio-format wav --postprocessor-args "ExtractAudio:-ar 16000 -ac 1"`.
- Arquivo cujo nome começa com `-` (IDs do YouTube podem) quebra `ls *.vtt`; conte com `ls -- *.vtt` ou em Python.

## 1. Build the job list first

Write one JSON with `{id, titulo, agrupador, url, wav}` per video before downloading anything.
Every later stage reads that file, so a crash never loses the mapping between a `.wav` and the
lesson or clip it came from. Number the outputs `01.wav`, `02.wav`… in presentation order.

## 2. Pull AUDIO ONLY, from the smallest rendition, with retries

```python
cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error",
       "-reconnect","1","-reconnect_streamed","1","-reconnect_delay_max","10",
       "-i", url, "-vn","-ar","16000","-ac","1","-c:a","pcm_s16le", wav]
```

- **Prefer an HLS rendition over the single big MP4, and take the lowest one** (`-240p.m3u8`):
  the audio stream is identical across renditions, and segmented downloads survive a dropped
  TLS handshake that kills a one-shot MP4 fetch.
- **Loop up to ~5 attempts per file**, accepting only when `os.path.getsize(wav) > 100_000`.
  Some files only land on the 2nd or 4th try; a single-pass script silently ships a short list.
- 16 kHz mono PCM is exactly what the ASR wants, so this step doubles as the decode step.
- On an HLS master with a separate audio group add `-map 0:a:0` so only audio segments are fetched.
- **Download in parallel (~6 workers, ThreadPoolExecutor) when the ASR runs concurrently**: one
  sequential HLS pull runs ~8x realtime and becomes the bottleneck; signed HLS URLs also expire
  in a few hours, so fetch everything early, longest first.
- **Write to `<id>.part.wav` and `os.replace` to `<id>.wav` only on success.** A transcriber that
  polls the folder will otherwise pick up (or a killed run will leave) a truncated WAV that looks
  final. If you kill a downloader, delete its partial output immediately.
- Do not `ffprobe` the remote MP4 just to collect durations — it is slow and fails often. Take
  duration from the written WAV (`frames / framerate`).

## 3. Transcribe from an ARRAY, not a path

```bash
uv venv .venv && uv pip install --python .venv faster-whisper
```

```python
import wave, numpy as np
from faster_whisper import WhisperModel

with wave.open(path, "rb") as w: raw = w.readframes(w.getnframes())
audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
segs, info = model.transcribe(audio, language="pt", beam_size=1, vad_filter=True,
                              condition_on_previous_text=False)
txt = " ".join(s.text.strip() for s in segs)
```

**Feed the numpy array, never the filename.** Passing a path routes decoding through PyAV,
whose `av.open()` signature drifts between releases and takes the whole batch down; the WAV is
already in the format the model wants, so the stdlib `wave` module removes that dependency.

Settings that matter: `language="pt"` (never autodetect per file — a quiet intro gets
misdetected), `beam_size=1` + `int8` for CPU throughput, `vad_filter=True` to skip silence, and
`condition_on_previous_text=False` so one bad segment does not poison the rest.

Model choice: `small` is the floor for usable Brazilian Portuguese with financial jargon;
`tiny` garbles numbers and product names. With VAD + int8 + beam 1 on 8 CPU threads, expect
~8–10x realtime (1h of audio ≈ 6–8 min). One process already saturates the CPU — a second
parallel transcriber does not speed things up.

A queue-driven transcriber that re-reads the job JSON each loop lets you append new items
(e.g. YouTube videos without captions) while it is running.

## 4. Make the run resumable and background it

Wrap the transcription script in a driver that re-runs it a few times with a sleep between
passes, where the inner script **skips any input that already has a non-empty `.txt`**. That
single rule means a timeout, a still-downloading file, or a dependency error costs only the
current item and the next pass resumes. Launch the driver with `background=true, notify=true`
and redirect to a log file — a 40-minute foreground call will time out.

Write a header into every transcript so the synthesis stage never reopens the audio:

```
# {agrupador} - {titulo}
# duracao_audio={segundos}s
```

## 5. Read them in chunks, then synthesize

Total text is large (~180 KB for 3h). Print the transcripts in batches of ~40 KB per call
rather than one dump that gets truncated mid-file. Build the deliverable's structure
(module → item → duration) from the headers programmatically and the substance from the bodies.
Sum durations in code and state the real total; never estimate it.

## Pitfalls

- **A platform's "auto subtitles: active" flag is not a transcript.** Verify the actual
  `subtitles[]` payload or the `.m3u8` before planning around it, or you either build an ASR
  pipeline you did not need or promise captions that do not exist.
- **Report what the audio actually says.** The transcripts are the evidence for the summary; if
  a video failed to download, say so and exclude it rather than inferring content from its title.
- Keep the finished `.txt` files outside the scratch dir (pruned in 24h) when the user may ask
  follow-up questions about the same videos later.
