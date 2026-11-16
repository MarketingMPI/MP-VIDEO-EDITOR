# Multi-clip event / institutional montage (ffmpeg)

Combine several raw event clips into one polished vertical montage with
transitions, a music bed, ambient sound, and subtle SFX. Validated building the
Evento MFO institutional (6 "Event N" clips → 48s 9:16 reel). No NLE.

## Workflow
1. **Probe every clip.** They are heterogeneous: mixed resolution (4K / 720p /
   576p / 1440x1920), mixed fps (60 / 30 / 30000/1001 / 600/19), mixed HDR (some
   HLG, some bt709 SDR), all usually `rotation -90` (shot vertical). Note each.
2. **Scout content via frames + vision.** Long clips (e.g. a 2.5-min networking
   take) need several sample frames to pick the best in/out sub-ranges. Build a
   short shot list with a narrative arc (establish → content → authority →
   relationship → detail → warm close). **Watch the presentation TV/screen in the
   background:** avoid in/out points where it shows a device config/setup screen
   (e.g. "Verificar Alimentação do Dispositivo") or a blank/input-select state —
   pick moments where it shows a real content slide, or crop tighter on the
   speaker to hide a bad screen. Sample enough timestamps to catch it.
3. **Confirm direction with the user before rendering** — duration/pace, on-screen
   text yes/no, ambient sound yes/no, logo yes/no. These change the whole build.
4. **Normalize each chosen sub-clip to one clean segment** (1080x1920, 60fps,
   graded) — see below. Render each to its OWN mp4.
5. **Join with xfade transitions** (timebase-normalized — see the gotcha).
6. **Build audio** = music bed + low ambient + transition SFX, then final mux.
7. Integrity-check (`ffmpeg -v error -i out.mp4 -f null -` → 0 errors), deliver to
   Downloads, re-verify the copy.

## Normalize a segment (fit 9:16, grade, upscale low-res)

Clip already ~9:16 → scale-to-fill + crop:
```
scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920
```
SDR look (add light sharpen for upscaled low-res footage):
```
eq=contrast=1.06:saturation=1.06:gamma=1.02,unsharp=5:5:0.5:5:5:0.0,format=yuv420p
```
HDR clip → prepend the tonemap chain
(`zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p`)
then a lighter grade (contrast 1.05, sat 1.05).

**Aspect that is NOT 9:16 (3:4 like 1440x1920, OR a genuinely HORIZONTAL 16:9
clip): blurred-fill** instead of a hard crop, so nothing important is lost:
```
[0:v]...grade...[c];[c]split[a][b];
[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28[bg];
[b]scale=1080:-2,unsharp=5:5:0.5:5:5:0.0[fg];
[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p
```
(Use `split` off one graded stream, not two decodes of the source.)
**Why this matters for horizontal presentation footage:** in a wide shot the
speaker and the on-screen slide often sit on OPPOSITE sides of frame — a hard
9:16 crop keeps one and loses the other (validated: a 0.66-center crop of the JP
Morgan speaker cut her AND dropped the slide). The letterbox-blur keeps the whole
16:9 composition (speaker + slide) centered with an elegant blurred surround, and
reads as institutional. Prefer it over crop whenever the wide frame carries two
points of interest. Mixed horizontal + vertical sources in one montage: crop the
verticals, letterbox-blur the horizontals; everything lands at 1080x1920.
Encode every segment identically: `-r 60 -c:v libx264 -profile:v high -preset medium -crf 19 -pix_fmt yuv420p`.

## Reframe each scene individually (the user WILL ask for this)

A plain scale-to-fill crop leaves lots of dead ceiling/headroom and off-center
subjects — the user rejected this twice ("muito espaço solto em cima", "ajuste a
centralização"). Give EACH scene its own `zoompan` reframe after the fit-crop:
```
scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
zoompan=z=1.3:x='iw*CX-(iw/zoom/2)':y='ih*CY-(ih/zoom/2)':d=1:s=1080x1920:fps=FPS
```
- `CX`/`CY` are the subject center as a fraction (find it with a `drawgrid`
  overlay + vision). Lower `CY` (e.g. 0.32–0.56) pulls the frame DOWN to kill top
  headroom; raise zoom (1.15–1.6) to fill and cut a distracting foreground/second
  person. Validate each on a still + vision before the full render.
- Match `fps=` to that clip's real fps (60 for HDR, 30 for the SDR phone clips)
  or the segment's frame timing drifts.

## Rescue a too-short detail clip with gentle slow-mo
When the best sub-range of a short clip is only ~3s but you need ~5s, slow it:
append `setpts=PTS/0.72` (0.72x ≈ 4.05s → 5.6s). Looks elegant on a product/detail
close-up and buys montage length without a hard freeze. Re-`ffprobe` its new
duration and recompute offsets.

## xfade transitions — the two things that bite

**1. Timebase must match or xfade refuses.** Different-source segments carry
different timebases; xfade errors `First input link ... timebase ... do not match`.
FIX: normalize every input's timebase + fps right before the chain:
```
[0:v]settb=AVTB,fps=60[v0];[1:v]settb=AVTB,fps=60[v1];...  # one per input
```
then chain xfades on `[v0][v1]...`.

**1b. `settb=AVTB` is NOT enough when segments have DIFFERENT source fps.** On the
Salume montage (segments were a mix of 60fps HDR and 30fps FHD, because each
`zoompan` used `fps=` matched to its own clip), `settb=AVTB,fps=60` still collapsed
an 80s montage to ~15s — the accumulated xfade timing silently broke. FIX: pin BOTH
to explicit constants, fps FIRST then a fixed timebase: `[N:v]fps=60,settb=1/60[vN]`.
That forces every input onto identical 60fps / 1-60 timebase and the offsets hold.

**2. Cumulative offset math.** In a CHAIN of xfades, each `offset` is measured on
the ACCUMULATED output so far, not the raw clip. With transition duration `T`:
```
offset_1 = dur(seg1) - T
offset_n = (running output length after xfade n-1) - T
running length after an xfade = prev_running + dur(next_seg) - T
```
Elegant, institutional set: `fade` / `fadeblack` / a single `smoothleft` slide,
`duration=0.6`.

**TRAP: a segment SHORTER than you asked for silently collapses the montage.**
`-ss X -t 4.5` on a clip that is only 2.9s long yields ~2.6s, and every
downstream offset is now wrong → the whole thing overlaps into a too-short
result. Always `ffprobe` each rendered segment's real `duration` and recompute
offsets from the actual numbers before the montage render.

**TRAP 2: container duration ≠ video-STREAM duration — offsets need the stream
number.** After a `zoompan` render, `ffprobe -show_entries format=duration` (the
CONTAINER) can read e.g. 8.0s while the actual video stream is 6.67s. xfade works
on the stream, so cumulative offsets computed from the container are wrong and the
montage mis-times. Pull the per-segment length from the VIDEO STREAM, not the
container: `ffprobe -select_streams v:0 -show_entries stream=duration,nb_frames -of csv=p=0 seg.mp4`,
and if they disagree recompute offsets from the stream duration (or `nb_frames/fps`).
Also: a 4K-HDR `-ss` seek can land imprecisely (a requested 8.5s came out 7.65s) —
re-probe after rendering and never trust the requested `-t`.

## Audio: music bed + low ambient + transition SFX
- **Music bed:** synthesize a longer classical piece (see
  `make_music_classica.py` pattern — piano + a faint string pad, gentle arc that
  swells mid-way and resolves). Render longer than needed, use the first N sec.
- **Ambient realism (if user wants it):** extract audio from one clip with good
  event murmur, filter hard and drop it very low:
  `highpass=f=120,lowpass=f=6000,afftdn=nf=-20,volume=0.10,loudnorm=I=-30`.
  NOTE `afftdn` `nf` valid range bottoms out near **-20**; `nf=-18` errors
  "Result too large".
- **Transition SFX are OPTIONAL — ask, don't assume.** On the Evento MFO
  institutional the user first wanted synced whooshes, then decided "remove os
  sons de transição, não precisa" and had them all stripped. Deliver a clean
  music+ambient bed by default; only add whooshes/chime if the user asks, and
  keep them as a separable audio layer so they're trivial to remove on request
  (rebuild the mix without the whoosh/chime inputs; the xfade video is untouched).
- **Transition SFX (when wanted):** synthesize a soft filtered-noise *whoosh*
  (bandpassed noise under a `sin(pi*t/dur)` envelope) and drop one at each
  transition via `adelay=<ms>|<ms>`. A faint bell/chime on a "detail/reveal" beat
  (e.g. a product close-up) is a nice touch.
- **SYNC THE WHOOSH BY ITS PEAK, not its start (the user WILL notice).** A
  `sin(pi*t/dur)` whoosh peaks at its own MIDPOINT (~0.4s into a 0.8s whoosh). The
  transition's visual center is `offset + T/2`. So the whoosh START (its `adelay`)
  must be `transition_center - whoosh_peak`, i.e. `adelay ≈ (offset + T/2 - 0.4)*1000` ms.
  Placing the whoosh START at the transition center (the naive approach) lands it
  audibly LATE and the user flagged it as "not synced." Recompute all adelays from
  the FINAL segment durations after any reframe/slow-mo/length change — the
  offsets shift and the SFX must follow.
- **Verify sync objectively:** `volumedetect max_volume` in a 0.6s window at each
  transition center should show a clear peak vs. a non-transition window (e.g.
  ~-1 to -5 dB at transitions vs. ~-7 dB mid-scene). Cheap, no ears needed.
- **Mix:** `amix=inputs=N:normalize=0` of [music][ambient][whoosh1..k][chime], then
  ONE `loudnorm=I=-15:TP=-1.5` + `alimiter=limit=0.92`. Target ~-13 to -15 LUFS,
  TP ≤ -1. Give the music an `afade=t=out` at the tail.

## Final mux
Mux the montage video with the built audio, `-shortest`, `-c:v libx264 -preset
slow -crf 19 -movflags +faststart -c:a aac -b:a 192k`. Integrity-check and deliver.

## "Maior qualidade possível" render
When the user asks for maximum quality, re-render the WHOLE chain at high quality,
not just the final mux — quality lost at the segment/montage stage can't be
recovered later. Bump every encode (`make_segments`, `make_montagem`, final) to
`-preset veryslow -crf 12` and the final audio to `-c:a aac -b:a 320k`. This ~doubled
the video bitrate (≈5.7→10.3 Mbps) on the Evento MFO reel. Be honest with the user:
CRF 12 preserves the source but **cannot add detail to low-resolution clips**
(the 576p/720p event clips stay soft; only the 4K HDR sources reach full quality).
Offer HEVC (smaller file, same quality) or a higher output resolution as follow-ups.

**But cap veryslow at 1080p short clips — it is very slow at 60fps.** A ~80s 1080p60
final at `veryslow -crf 13` took ~13 min on Salume. For 1080 finals `veryslow -crf 13`
is fine but budget the time (or use `-crf 13 -preset slow` for a near-identical file
much faster). Reserve `crf 12` for shorter pieces. (For 4K masters see the size/time
blowup section — there `slow` beats `veryslow` because the tonemap dominates.)

## Settled "vídeo do evento no geral" recipe (dynamic close/wide montage)
For a general event-recap request ("edição profissional, closes, aproximar, cortes,
mínimo 1min20s"), the validated shape is ~10 scenes, ~8s each, alternating WIDE
establishing/room shots with CLOSE punch-ins on speakers, xfade `duration=0.5`
(`fade`/`fadeblack`/one `smoothleft`+`smoothright` slide). Give wides a slow Ken
Burns (`zoompan z='min(1.06+0.10*on/FRAMES,1.16)'...`) and closes a tighter fixed
or punched zoom (1.18–1.36). Alternate the two so it breathes. Ten ~8s segments
minus 9×0.5s transitions ≈ 80s — clears the 1min20s minimum with margin.

## 4K-vertical max-quality: size/time blowup + dual delivery
A single 4K vertical clip (2160×3840, HDR source ~37 Mbps) at `veryslow -crf 12`
is a trap: on OGAT7539 (20s) it ran **10+ min** and produced a **~281 MB** file
(CRF 15 slow still gave ~281 MB) — over WhatsApp's ~64 MB limit, and social sites
recompress it anyway. Two lessons:
- **The HDR tonemap is the real bottleneck, not the x264 preset**, so `veryslow`
  buys almost nothing over `slow` here — use `-preset slow -crf 15` for a 4K
  master and skip the veryslow penalty.
- **Deliver BOTH: the 4K master AND a practical 1080 downscale.** Downscale from
  the finished 4K (no re-tonemap): `-vf scale=1080:1920:flags=lanczos -c:v
  libx264 -preset slow -crf 18 -c:a aac -b:a 256k` → ~57 MB, shareable. Hand the
  user the 1080 as the everyday file and the 4K as the archive/edit master, and
  say which is which.

## Single already-edited clip (grade + music only)
Sometimes the input is ONE finished clip (e.g. OGAT7539: a panoramic take + a
3-panel multi-cam grid, with a ~0.2s black flash between them via `blackdetect`).
The user may want it kept whole — just tonemap/grade the color and lay a low
classical bed over it (no subtitles, no reframe, no cuts). Confirm structure with
the user (keep whole vs. split), then it's just: color chain + `audio bed trimmed
to clip length with afade in/out` muxed with `-shortest`. Reuse the existing
`trilha_classica.wav` across projects rather than re-composing.
