# Synthetic narration + motion-smoothness QA (narrated MP ads)

For any MP video with a TTS voice-over (code-rendered Reels via lemo-opuscar, or a
narrated edit) and for any "o vídeo dá engasgos / parece travando" complaint.
Reference implementations: `C:/Users/phenr/lemo-opuscar/films/mppro-criativo-01/tools/`
(`linegen.py`, `assemble.py`, `judder.py`, `where.py`, `camprobe.mjs`, `render_hq.mjs`, `master.sh`).

## Voice-over (PT-BR, commercial)

1. Engine: VoiceStudio API (`http://127.0.0.1:3900`, app must be open, `/health` = ok) with
   **VoxCPM2** (Apache-2.0 weights, 48 kHz). OmniVoice weights are non-commercial: never in ads.
2. **One API call per line, never the whole script then split.** The model runs sentences
   together and ASR word-ends are early, so splitting chops the last syllable (heard as
   "weird sentence endings").
3. Lock the timbre: multipart `POST /generate` with `engine=voxcpm2`, `language=pt`,
   `ref_audio`+`ref_text` (clean ~3 s of an approved synthetic take), `effect_preset=raw`,
   `denoise=false`, `seed`. Two seeds per line.
4. Pick per line: ASR text matches the script AND the envelope decays to ≤ −60 dB in the last
   ~75 ms. Re-seed takes the model truncated (tail still at −30/−40 dB).
5. Assemble: pad zeros, trim head at −42 dB, tail only below −55 dB + 120 ms, 90 ms cosine
   fade-out. No time-stretch (per-line takes are already calm; stretching smears tails).
6. Loanwords/acronyms phonetic in the spoken text ("fí beised", "ême pê pró"), correct
   spelling only in subtitles. Changing one sentence = regenerate only that line (rename old
   candidates first).
7. ~10 s CPU per 1 s audio: run in background. If the backend dies mid-batch, restart the app
   and resume line by line.

## Motion smoothness (measure, then fix)

- Measure the delivered file: per-frame mean abs diff of downscaled gray frames (`judder.py`)
  → repeated frames, spikes, alternating move/still frames, and frozen stretches
  (diff < 0.12 for > 0.5 s). `where.py` shows which region changes.
- Fixes, by impact:
  1. Camera velocity jumps (keyframe spline stopping dead next to fast moves): Gaussian-smooth
     the camera path in time (σ ≈ 0.17 s) within each hard-cut group.
  2. Frozen stretches read as a hang: keep a slow camera drift, ambient dust/particles, and
     linear Ken Burns on stills/end cards so nothing is ever perfectly still.
  3. Fast moves strobe at 30 fps: real motion blur (average n sub-frames, 180° shutter), never
     letting sub-frames cross a hard cut.
  4. Alternating move/still frames = slow fade of a dark gradient quantising in 8-bit: don't
     fade/smooth lighting across a hard cut.
  5. Overshoot easings on big rotations end in a specular snap: use ease-in-out.
- Max quality: lossless intermediate (PNG → libx264rgb -qp 0) and ONE final encode (x264
  slower CRF 12, BT.709, aq-mode 3, light grain vs banding, −14 LUFS, AAC 320k).

## Delivery habit

Copy to `~/Videos/<project>/`, keep each previous delivery there as `<name>_vN.mp4`, and
re-verify (judder + frame sheet + ffprobe) on the delivered MP4 itself.
