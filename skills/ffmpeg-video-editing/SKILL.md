---
name: ffmpeg-video-editing
description: Edit real footage into polished 9:16 clips with ffmpeg.
---

# ffmpeg Video Editing (real footage → polished social clip)

Turn raw camera/phone footage into a clean vertical (9:16) social clip: HDR→SDR
color, audio cleanup + music bed with ducking, burned subtitles, dynamic
punch-in zooms, logo overlay. All with ffmpeg (no NLE). Built and validated on a
Meu Patrimônio client testimonial; MP branding conventions are baked in below.

## When to use
- Editing interview/testimonial/event footage into a shareable clip.
- Any "corte, correção de cor, áudio, legenda, trilha" request on a video file.
- Recurring at MP: event folders hold many clips (Cliente 0N, Event N).
- **Single testimonial reel** → the MP-specific `mp-client-testimonial-video`
  skill has the full baked pipeline (reusable assets, confirmed preferences).
- **Several SEPARATE answer-takes of ONE speaker → one continuous testimonial**
  (multiple Q&A clips of the same person, joined so it plays like an unbroken
  monologue: reorder by content, drop the questions, soft crossfades) → see
  `references/seamless-multiclip-testimonial.md`.
- **Multi-clip event/institutional montage** (join several clips with
  transitions + music bed + ambient + SFX) → see `references/event-montage.md`
  for the xfade timebase fix, cumulative-offset math, blur-fill for mismatched
  aspect ratios, the ambient/whoosh audio build, the 4K-vertical size/time
  blowup + dual (4K master + 1080) delivery, and the single-already-edited-clip
  (grade + music only) case.
- **Finding the best moments to cut from a LONG recording** (live/webinar/MP PRO
  session, 30–90 min → short follow-up clips) BEFORE editing → see
  `references/long-video-cut-identification.md`. Covers the segment-audio +
  per-chunk whisper + timestamp-offset math that gives trustworthy timestamps
  across a whole long file (the whole-file whisper pass drifts), plus how to
  present the cut list and what makes a good stand-alone clip for this user.
- **Reframing lives with screen-share and tiny webcams** → always load
  `references/screen-share-live-layouts.md` before choosing a crop. It contains
  the quality gate that forbids full-screen upscaling of tiny webcam tiles, the
  report-hero vs stacked-cameras decision tree, multi-mode phase stitching, and
  dense-report legibility checks.
- **Batch of short talking-head promo/ad clips** (`COPY NN_VSNN.MOV` for a
  live/webinar: silence-cut + Instagram-style headline sticker + subtitles, with
  a restrained SDR color grade when requested or visibly helpful; already-SDR
  means no HDR tonemap, not “never grade”) → see
  `references/talking-head-ad-clips.md` and `scripts/make_ig_sticker.py`. Covers
  the silencedetect→KEEP-expr cut, the default `hflip` for mirrored front-camera
  footage, the white-rounded-box Stories sticker (Segoe UI Bold), per-clip
  sticker y-position, and the max-quality single-pass render from the original.

- **Aula/onboarding com slides, edição limpa e sem legendas** → load
  `references/clean-onboarding.md`. Preserve native landscape layout and teaching
  content; do not inherit Reels/music/logo defaults. It covers conservative
  pause trimming, exact frame/sample synchronization and restrained audio cleanup.

- **Narrated ad with a synthetic voice-over (TTS), or any "engasgos / travando"
  complaint** → load `references/narration-and-motion-qa.md`: per-line VoxCPM2
  generation (never split a whole-script take), tail-safe assembly, and the
  measured judder/frozen-frame diagnosis + fixes.

## Golden workflow (the order that works)
1. **Probe first.** `ffprobe -show_streams` — get codec, resolution, fps,
   `rotation`, per-stream `start_time`, and crucially
   `color_transfer`/`color_primaries`. Phone/mirrorless footage is often **4K
   60fps 10-bit HDR (HLG: bt2020 + arib-std-b67)** and MUST be tonemapped or
   colors come out washed/wrong on normal screens. If audio and video have
   different start times, load
   `references/av-sync-and-transcript-reconciliation.md` before using
   `select`/`aselect`; naïve timestamp resets can shift speech out of sync.
2. **Watch the footage via frames.** Extract JPEGs at several timestamps and read
   them with vision. Find: obstructions (someone crossing the lens), the real
   start of usable content, headroom, where the subject's face sits. Use
   `drawgrid=w=W/10:h=H/10` overlaid on a frame + vision to get face position in
   % for reframing.
3. **Measure audio.** `loudnorm=print_format=summary` + `volumedetect`. Note
   Integrated LUFS, True Peak (>0 dBTP = clipping), and LRA (>~12 = needs
   compression).
4. **Cut decisively.** Trim bastidores / obstructed intro. State the editorial
   cut to the user so they can veto.
5. Build color → reframe/punch-ins → subtitles → logo → audio, validating each
   stage on a short clip + vision BEFORE the full slow render.
6. **Render segments separately, then concat** (see pitfalls). Validate integrity
   with `ffmpeg -v error -i out.mp4 -f null -` (must be 0 errors) before delivery.

## Validated recipes
Full copy-paste command blocks live in `references/ffmpeg-recipes.md`. Load it —
it has the exact color chain, audio chain, ASS subtitle styling, zoompan punch-in
expression, and the two-segment concat that ships clean.

Key building blocks:
- **HDR HLG → SDR:** `zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p`
  then a light grade `eq=contrast=1.06:saturation=1.05:gamma=1.02`. `mobius`
  with `npl=250` gave natural skin + controlled whites; validated by vision.
- **Transcription:** ffmpeg 9 has a built-in `whisper` filter. Download a model
  (`ggml-large-v3-turbo.bin` from HuggingFace ggerganov/whisper.cpp),
  `whisper=model=...:language=pt:format=srt:destination=out.srt:queue=90`.
- **Subtitles:** convert SRT→ASS for full control (font, position, per-word
  color). Copy brand `.otf` into an `assets/` dir and pass
  `subtitles=file.ass:fontsdir=assets`.
- **Punch-ins:** `zoompan` (NOT `crop` — crop can't do time-varying size).
  Sum-of-gaussians zoom curve peaked at emphasis moments.
- **Music bed with ducking:** synthesize a royalty-free bed (numpy/scipy) or use
  a licensed track; duck it UNDER the voice with `sidechaincompress` (bed is the
  main input, voice is the sidechain).

## Pitfalls (all hit and fixed this session — do not relearn)
- **ffmpeg is a native Windows program under MSYS bash:** it does NOT understand
  `/c/Users/...` paths in output/args. Pass native `C:/Users/...` forward-slash
  paths. `cd` (a bash builtin) to MSYS paths is fine; the ffmpeg args are not.
- **Whisper timestamps drift over long files.** The filter processes in windows;
  timestamps become non-monotonic across a whole long clip and are useless for
  precise subtitles. FIX: trim the exact segment you'll caption FIRST, then
  transcribe that short file with a large `queue` — timing comes out reliable.
  Also fix transcription errors and proper nouns by hand; confirm names with the
  user before burning them in.
- **zoompan on a looped still explodes the frame count.** `-loop 1 -i img.png`
  feeds many input frames and `zoompan d=402` multiplies EACH by 402 → runaway
  (tens of thousands of frames, never finishes). FIX: give the still
  `-loop 1 -framerate 60 -t DUR` and use `zoompan d=1` (one output per input
  frame). With `d=1`, the `on` variable counts frames, so recompute any
  time-based zoom slope in frames, not seconds.
- **`concat` filter with a looped-still segment can corrupt the H.264 stream**
  (decodes with "Invalid NAL unit size", ~99% error rate, unrecoverable even by
  re-encode). FIX: render each segment to its OWN clean MP4, then join with the
  **concat demuxer** (`-f concat -safe 0 -i list.txt -c copy`). Verify with
  `ffmpeg -v error -i joined.mp4 -f null -`.
- **Sidechain ducking mix bug:** do NOT `amix` the clean voice with a
  `[voice+bed]` chain — that double-counts the voice (~+6 dB, ended at -9.5 LUFS
  clipping). CORRECT graph: `asplit` the treated voice; feed the BED as
  sidechaincompress main input + one voice copy as the sidechain key; then
  `amix` the OTHER voice copy with the ducked bed. Final `loudnorm=I=-14` +
  `alimiter=limit=0.95`.
- **Reusing a filter label twice** (`[voz]...[voz]`) is rejected by ffmpeg 9
  ("matches no streams"). Use `asplit=2[a][b]` and consume each once.
- A still frame chosen for an opening "hero" shot: check via vision it's not a
  blink / mid-word grimace, and that transient people (interviewer) are out of
  frame.
- **Headroom & centering — the user recurringly rejects a loose frame.** A first
  reframe pass often leaves too much empty ceiling above the subject and the
  person off to one side. Pull the frame DOWN (lower `CY` in the zoompan center,
  e.g. 0.5→0.54) and zoom in a touch until the subject is centered with modest
  headroom, head never cropped. Verify on a still + vision before rendering.
- **Warm/orange contraluz footage needs white-balance correction, not just a
  tonemap.** Event/window-backlit clips come out heavily orange (white shirts
  read cream). Cool it and recover blown highlights with
  `tonemap=hable` (recovers window detail better than mobius here) +
  `colorbalance=rh=-0.06:gh=-0.02:bh=0.06:rm=-0.04:bm=0.03` +
  `curves` pulling the red highlight down / blue up. Validate skin looks natural
  (not pale, not orange) and shirt reads white via vision.
- **Colored-LED (party/event) footage has a strong GREEN cast — fix it with the
  green CHANNEL, not colorbalance alone.** Ambient event lighting (green/amber
  LED) contaminates skin and background green/yellow, and it varies clip to clip.
  The effective lever is `colorchannelmixer=1.06:0:0:0:0:0.85:0:0:0:0:1.05:0`
  (pull the green channel down to ~0.85, nudge red/blue up), then a small
  `colorbalance=rs=-0.04:bs=0.03:rh=-0.03` and `eq` to finish. `colorbalance`
  alone (gm/gs/gh negative) under-corrected. Goal is not just \"natural\" but
  CONSISTENT across takes shot under the same shifting LEDs — grade every clip
  with the identical chain and vision-check two of them side by side read the
  same temperature. Note the `colorbalance` midtone param is `rm/gm/bm` (not
  `mm`, which errors \"Option not found\").
- **Very low source audio (-31 to -38 LUFS) lifts fine to -16.** Event/phone
  interview takes can be recorded far too quiet; `loudnorm=I=-16` after the
  RNNoise+EQ+compressor chain brings them to an audible, clean level. Don't be
  shy about the gain — measure each take, they often differ by several LU.
- **Front-camera (selfie) footage is MIRRORED — logo/text reads backwards.** MP
  chest logo and background come out flipped. Add `,hflip` to the video chain by
  default and confirm the logo reads right on a frame via vision. See
  `references/talking-head-ad-clips.md`.
- **A headline/sticker's Y-position is per-clip, not a constant.** A tight selfie
  framing puts the face high in frame, so a sticker at `y=H*0.11` that worked on
  one clip covers the forehead on the next. ALWAYS composite the sticker on a
  real frame of THAT clip and vision-check it clears the face/hair before the
  render; drop to `y=H*0.015`–`0.06` for high-face framings.
- **Cutting respiros: keep ~0.12s pad on each side of a removed silence.** Slicing
  the full silencedetect span edge-to-edge sounds robotic/clipped. Remove only the
  MIDDLE of each pause; invert one `between()` OR-chain into a KEEP expr and reuse
  the SAME expr for the intermediate cut AND the final render so cut points match.
- **`asetpts=N/SR/TB` can erase a real audio start offset and break lip-sync.**
  Compare audio/video `start_time` before silence cutting. If audio begins later
  and the initial video is retained, reset timestamps and materialize the delay
  as samples (`adelay=<offset_ms>|<offset_ms>`) in the cut intermediate so Whisper,
  voice treatment, and the final mux all share one zero-based timeline. If the
  initial trim already extends past the delayed audio start, the offset has been
  absorbed; do not add it again. See
  `references/av-sync-and-transcript-reconciliation.md`.

## MP branding for video (this user)
- **Vertical 1080×1920** for Reels/Stories. Target audio **-14 LUFS**, TP ≤ -1 dBTP.
- **Font: Campton** (`~/Downloads/campton full/*.otf`) for all burned text.
- **Subtitles: UNIFORM WHITE Campton**, subtle dark outline+shadow, lower third.
  NO colored word highlights, NO italics — the user tried green MP-keyword
  highlights + an italic interviewer question and **rejected both**; deliver
  plain uniform subtitles by default. (The green-keyword / italic ASS variant in
  the recipes file is legacy — only use it if the user explicitly asks.)
- **NO logo overlay by default** — the user removed it after the first pass and
  reaffirmed "sem logo" on later videos. Only add the coruja logo if asked. (The
  white-logo drop-shadow recipe stays available for when it IS wanted.)
- **No travessões (—) in any copy/subtitle.** Use comma/colon/period.
- **Music: soft CLASSICAL PIANO bed** (Satie/Gymnopédie feel), kept **very low**,
  especially over a speech-free opening. A brighter synth-pad bed was rejected as
  "too high/exposed"; a fuller CINEMATIC STRINGS/CELLO composition was rejected
  HARD ("ficou horroroso", "esses efeitos horríveis"). The user's settled bed is
  gentle solo piano — nothing else. Keep it at a fixed low level; do not let a
  post-mix loudnorm pump the quiet opening back up.
- **Varying the track across videos: keep it in the PIANO family.** The user
  noticed the SAME piano bed reused across every video and asked for variety —
  but the fix is a DIFFERENT piano melody/progression (regenerate
  `make_music_classica.py` with more bars / a new chord set), NOT a different
  instrument family. When they say "troque a música," give another soft classical
  piano piece, not strings/pads.
- **The music never drops to silence mid-video.** A dramatic full gate (music
  cut to zero for a beat, or a chord dying before the next one enters) reads as
  the track breaking. For a "freeze" beat cut the rhythm but keep a low sustained
  chord/bass under it; hold each scene's chord until the next one starts. Verify
  by RMS of the music stem in 0.1 s windows: nothing below ~−50 dB before the
  final tail.
- **Settled audio default = MUSIC ONLY.** No event ambient, no transition SFX
  (whooshes/chimes) unless explicitly requested. The user repeatedly stripped
  ambient ("sem barulho do evento", "Somente uma musica clássica") and SFX ("remova
  os sons de transição"). Build the bed music-only by default; keep any
  ambient/SFX as separable layers so a "remove it" request is a quick re-mux.
- **Family Office Club logo (when a logo IS wanted for an FO event):** the FOC
  mark (`~/OneDrive/Imagens/Logos MP/Frame 290 1.png`, gold coruja + "Family
  Office CLUB", transparent RGBA) goes DISCREET, bottom-center. Crop its
  transparent margins (PIL `getbbox`), scale to ~290px wide, add a soft drop
  shadow for legibility over any background, overlay `x=(W-w)/2:y=H-h-140`. On
  letterbox-blur scenes it lands in the lower blurred band; on cropped verticals
  it sits over the image but the shadow keeps it readable. Still off by default.
- **Denoise voice hard with RNNoise** (`arnndn=model=std.rnnn`) — the user asked
  for maximum noise removal and approved it; it beat FFT-only denoise by ~20 dB
  on the noise floor. Chain it before the compressor/EQ/loudnorm.
- Confirm ambiguous proper names in subtitles with the user before burning.
- **ASS pitfall: `[Events]` Format MUST include `Name` between `Style` and
  `MarginL`.** Canonical: `Layer, Start, End, Style, Name, MarginL, MarginR,
  MarginV, Effect, Text` (10 fields), matching the 10-field `Dialogue:` lines.
  Drop `Name` from the Format line (9 fields) while still writing 10-field
  Dialogues and libass shifts every column: the empty Name's trailing comma
  leaks into the text, so EACH subtitle renders a literal `,` glued to its first
  word (",QUE EU TENHO"), and the Style→Fontname binding breaks (serif fallback).
  Vision-check symptom: leading comma + wrong serif typeface. Keep Format and
  Dialogue field counts equal.
- **ASS Fontname selection differs by font provider; verify the actual `fontselect` log.** First inspect name IDs with `TTFont`: family is name ID 1, full name ID 4, PostScript name ID 6. On ffmpeg 9 **Windows DirectWrite**, this environment loaded `CamptonBold.otf` from `fontsdir` but `Fontname: Campton` and `Campton Bold` both fell back to `Arial-BoldMT`; `Fontname: Campton-Bold` (the PostScript name, ID 6) resolved correctly (`fontselect ... -> Campton-Bold`). Use the family name on providers where it resolves, but never trust the style string alone: read ffmpeg's `fontselect` line and require it to point to the intended font, not Arial/serif fallback. Verify visually on a frame as well.
- **`fontsdir` must contain ONLY font files.** If you point `subtitles=...:fontsdir=assets`
  at a dir that also holds non-font assets (e.g. the `std.rnnn` RNNoise model),
  libass tries to load them as fonts and spams `Error opening memory font
  'std.rnnn'`. Harmless-ish but noisy, and can slow font matching. FIX: keep a
  dedicated `fonts/` dir with just the `.otf`s (`cp assets/*.otf fonts/`) and
  point `fontsdir=fonts`.
- Cover an unavoidable messy shot (interviewer in frame during the question) with
  a Ken-Burns still of the subject listening, real audio playing over it, then
  cut to the live take.

- **concat demuxer exige áudio com MESMO sample rate/codec/layout em TODOS os
  segmentos.** Sintoma de mismatch: `ffmpeg -v error -i joined.mp4 -f null -`
  cospe centenas de `Number of (scalefactor) bands exceeds limit` / `channel
  element is not allocated` no stream AAC (o vídeo fica OK, só o áudio corrompe
  na junção). Causa vista na prática: o clipe principal herdou **96000 Hz** do
  áudio da live enquanto a vinheta gerada saiu a 48000 Hz. FIX: renormalize CADA
  segmento com `-c:v copy -c:a aac -b:a 256k -ar 48000` antes do
  `-f concat -safe 0 -i list.txt -c copy`. Sempre confira com
  `ffprobe -select_streams a -show_entries stream=sample_rate` antes de juntar.
- **SVG → PNG no Windows: use `sharp` (Node), não cairosvg/svglib.** cairosvg e
  reportlab/renderPM exigem a libcairo nativa (`no library called "cairo-2"`) que
  não está no Windows. `npm install sharp` e
  `sharp(svg,{density:900}).resize({width:N}).png().toFile(out)` renderiza SVG
  com transparência preservada, limpo. Node vive em
  `~/AppData/Local/hermes/node/`. Valide a transparência compositando sobre uma
  cor sólida + vision (o preview de PNG transparente engana com "fundo preto").

## Vinheta de encerramento MP PRO (padrão dos cortes da live Mais Retorno)
Padrão fechado com o user para os follow-ups da live "Diagnóstico com IA"
(revisado após feedback):
- **1080×1920, fundo em DEGRADÊ radial de preto** (#262626 no centro ~42% da
  altura → #0a0a0a nas bordas), desenhado pixel a pixel no Pillow. Logo MP PRO
  dourada (#E4D6A7) no centro-superior (~36%), linha divisória dourada fina,
  **botão DOURADO #E4D6A7 arredondado com texto ESCURO #181818** (o user trocou
  o botão verde pelo dourado da logo; texto escuro para legibilidade), CTA
  "Faça sua inscrição agora", subtítulo cinza "Formação + comunidade para
  consultores". Gerador reutilizável: `scripts/make_vinheta.py` (Campton em
  tudo, 2× supersample; edite OUT/LOGO/CTA/SUB conforme o workdir).
- **Logo MP PRO durante o clipe:** rodapé inferior CENTRAL, `scale=360:-1`,
  `overlay=(W-w)/2:H-h-70`.
- **Transição para a vinheta = XFADE (crossfade), NÃO corte seco.** O user pediu
  entrada suave. Render a vinheta como segmento próprio (~4s, áudio = cauda da
  trilha de piano a volume 0.16 com afade out), ambos os segmentos a 48kHz, e
  junte com:
  `[0:v][1:v]xfade=transition=fade:duration=0.8:offset=<dur_seg1 - 0.8>[v];`
  `[0:a][1:a]acrossfade=d=0.8:c1=tri:c2=tri[a]`.
  xfade re-encoda (não dá pra usar concat demuxer com transição), então rode o
  filtergraph completo com libx264 CRF 15. offset = duração do seg1 menos a
  duração do xfade.

## Layout de corte "screen-share / relatório herói" (live com tela compartilhada)
Quando o trecho da live é COMPARTILHAMENTO DE TELA (slide/relatório) com as
câmeras pequenas na lateral (ex.: o relatório HTML de diagnóstico da Mais
Retorno), há DOIS sub-casos:

### A) O relatório é sobre o que está sendo dito → relatório é o herói
- **Crop do relatório** (só o conteúdo útil, sem barra do browser nem as
  câmeras) → `scale=1060:-1`, overlay no topo `(W-w)/2:210`.
- **PiP arredondado do orador que fala** no meio (`(W-w)/2:~840`): crop apertado
  do rosto ACIMA do nametag da live. CUIDADO com DUAS bordas: o nametag azul
  vaza embaixo E o topo da cabeça corta fácil (user rejeitou "rosto cortado").
  Comece com um crop AMPLO da câmera inteira (ex.: 200×230) + vision para medir,
  em %, onde estão topo-da-cabeça e onde COMEÇA o nametag; então feche o crop
  entre esses dois limites com folga acima. Na câmera 1280×720 da live Mais
  Retorno o crop validado foi `crop=176:134:8:374` (cabeça inteira, zero
  nametag). Escale o PiP PRESERVANDO essa proporção (176:134 → 360:274, NÃO
  360:366 quadrado, senão distorce) e gere a máscara arredondada na MESMA
  proporção. `scale` do PiP e da máscara devem bater.
- **Fundo** cor sólida escura combinando com o relatório (ex.: `0x0c1a14`
  verde-petróleo escuro), NÃO o blur da câmera.
- **PiP arredondado com máscara `gray` (L) exige `format` explícito nos DOIS
  lados do alphamerge, senão o PiP some.** A máscara de `make_pipmask.py` é
  single-channel (`pix_fmt=gray`). `[luc][mask]alphamerge` só funde se o vídeo
  estiver em `yuva420p` e a máscara em `gray`: `crop=...,scale=W:H,setsar=1,
  format=yuva420p[luc]` + `scale=W:H,setsar=1,format=gray[mask]`. Sem os
  `format=`, o alphamerge falha silenciosamente (PiP invisível) OU dá
  `Input frame sizes do not match` se as dimensões pós-scale divergirem (a
  máscara 360×274 escalada por largura vira 300×228; force `scale=300:228` nos
  DOIS, idênticos). DEPURE isolando o PiP sobre um `color=red` — se aparecer no
  vermelho mas some na composição real, o problema NÃO é o alphamerge, é
  contraste: a câmera do orador tem fundo escuro (madeira/parede) que se funde no
  `0x0c1a14`. FIX: dê ao PiP uma moldura/pad claro OU posicione-o sobre uma faixa
  do relatório, não sobre o fundo liso.
- **Slides que evoluem no tempo (prompt → HTML → gráfico):** um mesmo crop fixo
  do relatório serve para todas as fases se o conteúdo ocupa a mesma região da
  tela. Valide o crop em 3 tempos (início/meio/fim) com vision — no Corte J o
  `crop=1020:570:242:100` pegou prompt, \"Raio-X da carteira\" e slide Morgan
  Stanley sem reajuste. Escale o relatório a `1080` de largura (tela cheia) com
  um `pad` fino colorido (`pad=iw+8:ih+8:4:4:color=0x1c3d30`) como moldura.
- **Limite de 1:30: cortar a sobra do INÍCIO mata dois coelhos.** Se o raw abre
  com o rabo da fala anterior e o clipe estourou o teto (ex.: 1:32), re-extraia
  começando ~2s depois, no gancho real — encurta E melhora a abertura. Desloque o
  SRT com um script (subtrair o shift de cada timestamp, descartar blocos que
  ficam <0) antes de gerar o ASS, para a legenda não sair adiantada.
- **Legenda** no terço inferior (MarginV 300) + logo no rodapé — sobram livres
  abaixo do PiP. Sem headline sticker quando o próprio relatório já traz a
  pergunta/gancho escrito (evita redundância).
- **PITFALL de performance:** a fonte `color` é infinita; se ela alimenta o
  overlay a saída nunca termina (render travou 7min+ e foi morto). FIX: dê
  duração e fps à fonte (`color=...:d=43.4:r=30`) E ponha `shortest=1` no
  primeiro overlay que a consome. Use `-preset medium` (não `slow`) nesses
  filtergraphs pesados com RNNoise + múltiplos overlays + subtitles.
- **RODE renders pesados em BACKGROUND, não em foreground.** Um filtergraph com
  RNNoise + vários overlays + subtitles a `-preset slow` ESTOURA o timeout de
  180s do foreground e deixa um MP4 INCOMPLETO (sem moov atom → ffprobe não lê
  duração). Sintoma: o arquivo existe com tamanho grande mas está corrompido.
  FIX: dispare com `background=true` + `notify_on_complete=true` e continue outro
  trabalho; ao terminar, confirme com `ffprobe ... format=duration`. Um corte de
  ~40-90s renderiza em ~1-2min nesses graphs — sempre background.

### B) A fala NÃO tem relação com o relatório na tela (dica/opinião genérica)
Ex.: durante uma tela compartilhada o orador solta uma dica de fechamento que
independe do slide. Aí o relatório é ruído — trate como TALKING-HEAD normal
focando SÓ a câmera de quem fala (mesma abordagem do Corte A: câmera nítida na
faixa central + fundo desfocado dela mesma + sticker + legenda + logo).
- A câmera de canto numa live com share é PEQUENA (~150px de largura). Ampliar
  p/ 1080 fica suave/macio, mas aceitável p/ Reels — avise o user que é limite
  da fonte. Sticker + legendas seguram a atenção.
- Mesmo cuidado das DUAS bordas do PiP (topo da cabeça + nametag) do caso A, MAIS
  uma terceira: **borda preta lateral** da caixa da câmera. Comece com crop amplo
  + vision, então feche entre borda-esquerda-preta, topo-da-cabeça e início-do-
  nametag. Crop validado da câmera do Gabriel (topo-esq, live 1280×720):
  `crop=142:132:11:199` (cabeça inteira, sem nametag, sem borda preta).

## Layout "duas câmeras empilhadas" (quando a câmera do orador é pequena demais)
Quando o trecho é talking-head MAS o orador está numa câmera minúscula
(~140-240px na fonte, típico de layout screen-share da live) e a fala NÃO é
sobre o relatório na tela, NÃO amplie a câmera dele pra tela cheia — o zoom
destrói a qualidade (user rejeitou: "a qualidade ficou horrível com esse zoom").
Em vez disso, empilhe as DUAS câmeras (quem fala em cima, quem ouve embaixo),
cada uma `scale=940:-1` (~672px alt), sobre fundo escuro sólido:
- `[bg][gab]overlay=(W-w)/2:250:shortest=1` e `[t1][luc]overlay=(W-w)/2:930`.
- Inclua o nametag de cada um no crop (identifica quem é sem esforço).
- Legenda sobreposta na base da câmera de baixo: `MarginV ~430` (não 300, senão
  cai na faixa preta colada na logo).
- **PITFALL de PTS crítico:** ao usar `-f lavfi -t N -i color=...` como fundo +
  `-ss T -i video`, os timestamps do vídeo começam em ~T (ex.: 1875s) e NÃO
  casam com a color (começa em 0) → o overlay do vídeo renderiza VAZIO (só o
  fundo). FIX obrigatório: `setpts=PTS-STARTPTS` em CADA stream croppada do vídeo
  antes do overlay. Sem isso o frame sai só com o fundo colorido.

## Layout consistente quando a live TROCA de modo no meio do clipe
Um mesmo trecho da live pode alternar entre screen-share (câmeras pequenas) e
câmeras-grandes-lado-a-lado no meio da fala. Ampliar um crop fixo quebra (pega o
relatório na parte errada). Solução validada (Corte B2, user aprovou "duas
câmeras empilhadas o tempo todo"):
1. Ache o timestamp EXATO da troca por bisseção com vision (frames a cada 1s).
2. Renderize DUAS fases separadas (só vídeo, `-an`), cada uma com `trim` do
   intervalo certo + `setpts=PTS-STARTPTS`, e crops próprios (câmeras pequenas na
   fase screen-share, câmeras grandes na outra).
3. CRÍTICO p/ não dar "pulo" na junção: force AMBAS as fases à MESMA geometria de
   saída por câmera com `scale=W:H:force_original_aspect_ratio=increase,crop=W:H`
   (ex.: 940×600) e as MESMAS posições de overlay (ex.: Gabriel y=300, Lucas
   y=960). Proporções de fonte diferentes NÃO importam depois desse scale+crop.
4. Concatene as duas fases-vídeo com o concat demuxer (`-c copy`) → um
   `stacked.mp4` unificado.
5. Passada FINAL: sobreponha áudio (do raw, tratado), sticker, legenda e logo
   sobre o stacked.mp4 numa única render, depois xfade com a vinheta.
Nametags das câmeras pequenas costumam ficar cortados/largos — corte acima deles
(reduza a altura do crop) na fase screen-share; a fase de câmeras grandes mantém
os nametags. A leve diferença de nitidez entre as fases é aceitável.

## Deliver
Copy the verified file to the user's Downloads folder. Confirm the copy's
integrity with the null-muxer check on the delivered path (native `C:/...` path).

- **ALWAYS keep a local master of every delivered cut in the project's `out/`**
  (e.g. `out/corte_<X>_final.mp4`), separate from the Downloads copy. This user's
  Downloads is **OneDrive-synced**, and delivered files can silently disappear
  from it later (moved/synced away) even though the `ffprobe`/null-check passed at
  delivery time. When the user comes back asking about the set, re-verify the
  Downloads copies exist; if any vanished, re-copy from the `out/` masters (a
  simple name-map loop over all cuts) and re-run the null check. Never assume a
  past successful delivery is still on disk.
- Note: `printf "%.1f" "$dur"` fails ("invalid number") when ffprobe emits a
  comma-decimal under a pt-BR locale — cosmetic only; the `cp` still ran. Use
  `awk`/`tr ',' '.'` if you need the formatted number, but don't treat the printf
  error as a delivery failure.
