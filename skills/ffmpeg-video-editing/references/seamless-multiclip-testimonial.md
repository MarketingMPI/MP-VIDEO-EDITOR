# Several answer-takes of ONE speaker → one seamless testimonial

Validated on the "Herdeira - MFO - Depoimento" job: 4 separate Q&A clips of the
same interviewee (Caroline), each an answer to a different off-camera question,
joined into a single ~2m20s vertical reel that plays like one continuous, flowing
statement — no visible questions, soft cuts that read as "continuation of her
speech." All clips same person, same chair, same set.

## Workflow

1. **Probe + frame-scout each clip** (usual: vertical HDR HLG, often 30fps FHD).
2. **Transcribe ALL clips first** (`whisper` filter, `format=text` for a quick
   read, then `format=srt` for timed cuts). The transcript is how you discover:
   - which clip is the **self-introduction** (the user asked to open with her
     presenting herself), and
   - the natural narrative order across clips (intro → the decision → the
     philosophy → a strong closing line).
   Whisper picks up the interviewer's question at the head of each answer AND
   bastidores ("pode começar", "depois você corta", "melhor eu não falar isso")
   — you will strip all of that.
3. **Decide the editorial order by MEANING, not file order.** Example arc used:
   `IMG_0241` (intro: who she is, family company) → `IMG_0242` (how MP entered) →
   `IMG_0244` (building/preserving patrimony across generations) → `IMG_0243`
   (short punchy close: "decisão muito acertada… confiamos 100%"). Trim each to
   just her answer: e.g. 0241 starts at 28.0s (right at "Meu nome é…"), 0242 ends
   at 42.0s to cut her self-retraction. State the cut list to the user.
4. **Grade + reframe each take identically** (see the green-LED fix in SKILL.md;
   these were shot under shifting event LEDs). Same `zoompan` reframe on all so
   framing is consistent take-to-take — the user explicitly flagged too much
   ceiling ("sobrou muito espaço na parte superior mostrando muito o teto"): pull
   `CY` up to ~0.56 and zoom ~1.22 so she's centered with modest headroom.
   Render each to its own video-only mp4 (keep audio separate for treatment).
5. **Treat each take's audio separately, THEN crossfade-join** (below).
6. **Build one combined SRT across the whole timeline** (below) and burn it.
7. Final mux (video xfade + audio acrossfade + burned subs), integrity-check,
   deliver.

## Soft cuts = crossfade BOTH video and audio (the "continuation" feel)

The user wanted cuts "mais suaves, como se fosse continuação da fala dela."
A hard cut between takes looks like a jump; the fix is a short simultaneous
crossfade on video and audio.

- **Video:** xfade `transition=fade:duration=0.4` chained across the 4 segments.
  Normalize fps+timebase first (`[N:v]fps=30,settb=1/30[vN]` — these were all
  30fps; pin explicitly, see the fps-collapse trap in event-montage.md), and use
  the cumulative-offset math (offset_n = running_length − T).
- **Audio:** `acrossfade=d=0.4:c1=tri:c2=tri` chained across the 4 treated voice
  tracks. This dovetails the tail of one answer into the head of the next so it
  sounds continuous instead of butt-spliced. Keep the SAME 0.4s duration as the
  video xfade so picture and sound cross together.
- Because audio crossfades OVERLAP by `d`, the audio total ends ~0.13s shorter
  than the naive sum; that's fine — mux with `-shortest`.

## Per-take voice treatment (before the crossfade join)

Each take is quiet and noisy. Chain, per take:
```
highpass=f=90,arnndn=model=std.rnnn,
equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=2:g=2.5,equalizer=f=7500:t=q:w=3:g=-3,
acompressor=threshold=-20dB:ratio=3:attack=8:release=180,
loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000
```
(highpass → RNNoise denoise → EQ: cut mud ~200, lift presence ~3k, tame sibilance
~7.5k → compress → per-take loudnorm to -16). Treating each take to the SAME
target BEFORE the crossfade means the levels already match at the seams.

## One combined SRT across the whole reel (only her words)

Don't caption each clip separately. Write a small Python pass that:
- parses each clip's SRT, keeps only cues INSIDE that clip's [ss,to] cut window,
- drops interviewer questions + bastidores via an EXCLUDE substring list
  (lowercased match: "depois você corta", "o que você considera", "qual foi uma
  decisão", "não precisa falar", "melhor eu", "desliga", …),
- RE-OFFSETS each surviving cue onto the montage timeline, accounting for the
  0.4s crossfade overlap (`timeline += seg_dur - XF` between clips),
- writes one merged SRT. Then fix the brand name ("meu patrimônio" →
  "Meu Patrimônio") with sed, and convert SRT→ASS (uniform white Campton, no
  highlights — the settled MP style) before burning with `subtitles=…:fontsdir=assets`.

The user asked for NO on-screen question and to "já começar o vídeo dela se
apresentando" — so the very first cue is her first real sentence, nothing before.

## Deliver
Render final at max quality (30fps FHD source → `-preset veryslow -crf 14` is
fine and not too slow at 30fps; ~2m20s took a few min), integrity-check, copy to
Downloads, re-verify.
