# Talking-head ad clips with Instagram-style headline sticker

Class of work: a batch of short vertical **talking-head promo/ad clips** (e.g.
`COPY NN_VSNN.MOV`) for a live/webinar, where the same person delivers slight
variations of one script. Edit is deliberately LIGHT: cut the respiros to make it
dynamic, burn subtitles, and add ONE headline that must look like an organic
Instagram post, NOT an ad. Validated on the MP × Mais Retorno "Ads Live" batch.

These source clips are typically **720×1280 30fps H.264 bt709 (already SDR)** — no
HDR tonemap is needed. “Already SDR” does **not** mean “never grade”: when the
user asks to improve color, or the contact sheet is visibly flat, apply a
restrained per-location SDR grade and validate it side by side on a real frame.
For neutral indoor phone footage, this chain was validated as a natural starting
point without clipping highlights:

```text
eq=contrast=1.03:saturation=1.03:gamma=1.015:brightness=-0.003
```

Outdoor footage with changing sun may tolerate slightly more saturation/contrast
(~1.03–1.055), but skin and sky must stay natural. Preserve the source resolution;
do not upscale merely to claim higher quality.

## Golden order (one clip)
1. **Probe** (confirm 720p/SDR) + **extract audio for ASR** + **silencedetect** +
   **grab one `hflip` frame** — all in one call.
2. Disparar **transcrição do ORIGINAL** em background (decide a headline a partir
   do gancho da fala) e, em paralelo, montar a expressão de corte dos silêncios.
3. Render an **intermediate `cutNN.mp4`** = silence-cut + (no flip yet) at CRF 18,
   `-c:a pcm_s16le`. Then **transcribe the CUT clip** for perfectly-synced subs.
4. Build the **headline sticker PNG** from the speech hook, and **test its
   y-position on a real `hflip` frame** with vision before committing.
5. Build the **ASS subtitles** from the cut-clip SRT (2-3 word Reels blocks).
6. **Final single-pass render FROM THE ORIGINAL** (max quality): apply the SAME
   silence-cut KEEP expr + `hflip` + the validated light SDR grade (when used) +
   sticker overlay + subtitles + audio in ONE graph. This avoids a second
   generation-loss encode of the intermediate.
7. Integrity check + copy to Downloads.

## hflip is the DEFAULT for front-camera MP clips
Every clip in the batch was recorded mirrored (selfie/front cam) — the "Meu
Patrimônio" chest logo and background reads BACKWARDS. Add `,hflip` to the video
chain by default and confirm the logo reads correctly on a frame via vision. The
user explicitly asked for this correction; apply it up front on every clip.

## Silence-cut (tirar os respiros, deixar dinâmico)
```
ffmpeg -hide_banner -i asr.wav -af "silencedetect=noise=-30dB:d=0.35" -f null - 2>&1 | grep silence_
```
For each detected `[start,end]` pause, remove the MIDDLE keeping ~0.12s of pad on
each side (so cuts don't sound robotic). Drop any residual span < 0.05s. Build one
`between()` OR-chain and invert it — this KEEP expr is reused verbatim in both the
intermediate cut and the final render:
```
KEEP="not(between(t\,A1\,B1)+between(t\,A2\,B2)+...)"
ffmpeg ... -filter_complex \
 "[0:v]select='$KEEP',setpts=N/FRAME_RATE/TB,hflip[v];\
  [0:a]aselect='$KEEP',asetpts=N/SR/TB[a]" -map "[v]" -map "[a]" ...
```
Typical yield on a ~60s clip: ~5s removed → dynamic without feeling chopped. Build
the expr in Python (list of pairs → string); escape commas as `\,` inside
`between()` for the bash-passed filter.

## Instagram Stories headline sticker (parece post, não anúncio)
The user/Gabriel wanted a headline "using an official Instagram font so it looks
like a normal post, not an ad." The winning style (confirmed via clarify): **white
rounded boxes, one per line, black text** — the Stories "highlight" text sticker.
- **Font: Segoe UI Bold** (`C:/Windows/Fonts/segoeuib.ttf`) — a close stand-in for
  Instagram Sans. (Campton is for the SUBTITLES, not the sticker.)
- Build it with Pillow at 3× supersample, rounded_rectangle per line, then
  downscale LANCZOS. See `scripts/make_ig_sticker.py`.
- **Text = the speech hook**, proposed from the transcription (the user chose
  "proponho o texto com base na fala"). One sticker can be reused across VS
  variants that share the same hook; a different COPY with a different hook gets
  its own sticker.
- **ALTERNATE the box color between versions** so a batch of similar clips does
  not all look identical. The user asked for this explicitly ("mude um pouco a
  cor do bloco de texto, se não fica tudo igual"). Confirmed rotation, all still
  reading as native Stories text stickers:
  1. white box + black text (`bg=(255,255,255)`, `fg=(15,15,15)`) — default,
  2. dark box + white text (`bg=(24,24,24)` = #181818, `fg=(255,255,255)`),
  3. MP green box + white text (`bg=(0,80,60)` = #00503c, `fg=(255,255,255)`).
  Vision-check white text stays legible on the dark/green boxes. `make_ig_sticker.py`
  takes `BG`/`FG` for exactly this.
- **Timing:** appears from 0 and **alpha-fades out right after the hook ends**
  (~5–6s), via `[sticker]format=rgba,fade=t=out:st=5.2:d=0.4:alpha=1` +
  `overlay=...:enable='between(t,0,5.6)'`.
- **Position is per-clip.** `y=H*0.11` works for a mid-framed subject, but tight
  selfie framings (face high in frame) need `y=H*0.015`–`0.06` so the sticker sits
  ABOVE the head. ALWAYS composite it on a real frame and check with vision that it
  clears the face/hair before rendering.

## Subtitles + audio (same MP conventions)
- Subtitles: uniform white **Campton**, 2-3 word blocks, `\fad(90,90)`, lower
  third, from the CUT-clip SRT (synced). ASS style used here: `Fontsize 44`,
  `Outline 2.6`, `Shadow 1.6`, `MarginV 150` at PlayRes 720×1280.
- **Proofread the SRT for homophones before burning.** whisper-pt mishears
  domain words: it wrote "vendendo no **machismo**" where the speaker said
  "**achismo**" (selling on guesswork). Burning that in would be embarrassing.
  Do a quick `.replace()` pass in the ASS-builder Python (e.g.
  `srt=srt.replace("machismo","achismo")`) and grep the final ASS to confirm the
  bad token is gone and the correction is present. Corrections seen on the MP PRO
  × XP Inc batch (Gabriel, live do Rafael Marques): `MPPRO`→`MP PRO`, `AOC`→`AUC`
  (assets sob custódia), `improvínio`→`improviso`, `meu patrimônio`→`Meu
  Patrimônio`, `consultores de investimento`→`consultores de investimentos`.
- Audio (voice only, no music bed). The validated MP chain denoises HARD with
  **RNNoise** (beats afftdn-only) and normalizes in a SEPARATE second pass so the
  loudnorm measurement is clean. Two passes on the CUT clip's audio:
  1. Treat → `aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,arnndn=m=std.rnnn,`
     `highpass=f=85,lowpass=f=9500,equalizer=f=180:t=q:w=1.2:g=-1.5,`
     `equalizer=f=3200:t=q:w=1.0:g=1.5,`
     `acompressor=threshold=0.10:ratio=2.2:attack=15:release=180:makeup=1.0,`
     `pan=stereo|c0=c0|c1=c0` → `treated.wav` (`pcm_s24le`).
  2. Normalize → `loudnorm=I=-14:TP=-2.0:LRA=6` → `audio_master.wav`
     (`pcm_s24le -ar 48000`). Confirm with `loudnorm=print_format=summary`
     (lands ~ -14 LUFS / -2 dBTP; TP -2.0 is the settled target, safer than -1.5).
  Then map `audio_master.wav` as the audio input in the final render.
  (`std.rnnn` lives in the workspace, NOT the `fonts/` dir — see the SKILL.md
  fontsdir pitfall.)

## Max-quality final render (user asked "maior qualidade possível")
`-c:v libx264 -profile:v high -preset veryslow -crf 14 -pix_fmt yuv420p
-x264-params "keyint=60:min-keyint=30" -c:a aac -b:a 256k -movflags +faststart`,
rendered in ONE pass from the ORIGINAL (not from the intermediate cut). Verify
`ffmpeg -v error -i out.mp4 -f null -` prints nothing, then copy to Downloads.
