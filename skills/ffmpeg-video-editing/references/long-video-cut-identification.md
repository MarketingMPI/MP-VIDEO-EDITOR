# Identifying cut points in a LONG recording (live/webinar → follow-up clips)

Use when the user hands you a long recording (a live, webinar, MP PRO session,
30–90 min) and asks you to **find the best moments** to cut into short
follow-up clips *before* any editing. This is a content-analysis pass, not a
render pass. Validated on the ~69 min "Diagnóstico com IA / Live MP PRO"
(Gabriel × Lucas Paulino, Mais Retorno), 720p SDR 30fps.

## Why not just transcribe the whole file in one shot
The ffmpeg `whisper` filter drifts / goes non-monotonic across a long file, so
one whole-file pass gives you timestamps you cannot trust to seek a cut. The
existing SKILL.md pitfall ("trim the exact segment FIRST") solves this for
*captioning a known clip* — but here you do NOT yet know where the clips are.
So you need reliable timestamps across the ENTIRE file. Solution: segment the
audio into fixed windows, transcribe each window (timestamps restart at 0 per
window), then add the window offset back.

## Workflow (the order that works)

1. **Probe** for duration + format: `ffprobe -v error -show_entries
   format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate`.
   Note runtime — decides how many chunks.

2. **Extract + segment audio in ONE pass** (16 kHz mono is all whisper needs;
   pass a NATIVE `C:/Users/...` path, MSYS `/c/...` fails):
   ```bash
   ffmpeg -hide_banner -loglevel error \
     -i "C:/Users/phenr/Downloads/<video>.mp4" \
     -vn -ac 1 -ar 16000 \
     -f segment -segment_time 600 -reset_timestamps 1 \
     "chunks/chunk_%02d.wav"
   ```
   `-segment_time 600` = 10-min windows. `-reset_timestamps 1` makes each chunk
   start at 0. A 69-min file → chunk_00..chunk_06 (last one short).

3. **Transcribe every chunk in a background loop** (reuse a local
   `ggml-large-v3-turbo.bin` — copy one from a sibling `mp-*` project dir rather
   than re-downloading ~1.6 GB). Run with `background=true,
   notify_on_complete=true` and read finished `.srt`s as they land; don't block:
   ```bash
   for i in 00 01 02 03 04 05 06; do
     ffmpeg -hide_banner -loglevel error -i "chunks/chunk_$i.wav" \
       -af "whisper=model=ggml-large-v3-turbo.bin:language=pt:format=srt:destination=srt/chunk_$i.srt:queue=90" \
       -f null -
     echo "== chunk_$i done =="
   done
   ```
   Each chunk takes ~1 min; a 7-chunk file finishes in ~7–8 min. Start reading
   chunk_00 while the rest process.

4. **Convert local → global timestamp:** `global = chunk_index * 600 + local`.
   Chunk_03 at local 00:50 = 30:50 global. Do this math when you quote a cut.

5. **Read transcripts, map the arc, propose cuts.** Skim each SRT, note the
   structural blocks (intro/promo, apresentação, cases, fecho), then pick
   self-contained 1:00–1:30 moments each with a hook + one clear thesis. Present
   as a TABLE: `# | timestamp (global mm:ss–mm:ss) | duration | tema/gancho`,
   flag your strongest picks, and offer a suggested posting order. Then cut ONE
   at a time on the user's go-ahead — do not batch-render before approval.

## What makes a good follow-up cut (this user's live-content taste)
- **Skip the promo bookends** (MP PRO pitch at the open/close) — flag them as
  "não recomendo cortar", don't propose them as clips.
- Strongest clips are **analogies + personal hooks**, not raw data dumps:
  e.g. "comecei a usar IA quando minha filha nasceu", médico × fisioterapeuta,
  a analogia do hotel, exercício físico. Concrete number cases (700 janelas / 36%
  bateu o CDI, Monte Carlo / Doutor Estranho) are strong too but rank them below
  the human/analogy moments for opening a series.
- Each cut must stand alone: open on a hook, land one idea, no dangling "como eu
  falei antes".

## Second pass — "faltou algum corte?" (coverage-gap scan)

After several cuts are already delivered, the user often asks whether any strong
moment is still untapped. Don't eyeball a 69-min transcript by hand — scan it in
code (`execute_code` / a Python heredoc). Validated approach:

1. **Parse every `srt/chunk_*.srt` into `(global_seconds, text)`** using the
   `global = chunk_index*600 + local` math above.
2. **List the intervals ALREADY covered** by delivered cuts as
   `(start_s, end_s, label)` tuples (recover each cut's global window from your
   own notes / the raw-segment extraction commands).
3. **Slide a ~90 s window across the whole file, skipping any window whose center
   is inside a covered interval**, and score each remaining window by density of
   "strong-moment" signal words. A signal list that worked:
   `imagina, analogia, é como, por exemplo, R$, milhão/milhões, mil, %, caso,
   história, efeito, uau, impacto, erro, nunca, sempre, diferença, o cliente,
   fechar, venda, converte`. Print windows scoring above a threshold with their
   global `mm:ss` start + a text preview.
4. **Manually inspect the top candidates** (dump the full transcript of each
   promising window) and rank them the same way as the first pass (human/analogy
   > number-case), dropping any that merely re-setup a cut you already made.
5. **Present the balance:** a table of what's DONE (label, tema, duração) plus a
   short list of the remaining strong moments with a recommendation, then let the
   user pick which (if any) to cut next.

This turns "did I miss anything?" into a deterministic answer instead of a vibe.

## Delivery format for these clips
Same MP video defaults as the umbrella: 1080×1920 vertical, uniform white Campton
subtitles, NO logo, soft classical-piano bed only, -14 LUFS. State this to the
user when you present the cut list so expectations are set before rendering.
