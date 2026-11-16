# ffmpeg Editing Recipes (validated command blocks)

All paths are native Windows `C:/...` (ffmpeg under MSYS does NOT accept `/c/...`).
Reference build: ffmpeg 9.0 full (Gyan), has whisper + zscale + libass + zoompan.

## 1. Probe

```
ffprobe -v error -show_format -show_streams "C:/path/in.MOV" 2>&1 | \
  grep -E "codec_name|width|height|r_frame_rate|duration|color_space|color_transfer|color_primaries|rotation|channels"
```
HLG HDR tell: `color_transfer=arib-std-b67`, `color_primaries=bt2020`,
`pix_fmt=yuv420p10le`.

## 2. Extract graded frames for vision review

```
ffmpeg -y -loglevel error -ss 20 -i "C:/path/in.MOV" \
  -vf "zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p,eq=contrast=1.06:saturation=1.05:gamma=1.02,scale=-2:640" \
  -frames:v 1 "C:/work/frame.jpg"
```
Face-locating grid overlay: add `,drawgrid=w=216:h=384:t=2:c=red@0.7` (for 2160x3840,
i.e. W/10 x H/10) before the final scale, then ask vision for face % position.

## 3. Color chain (HDR HLG → SDR, reference-quality)

```
zscale=t=linear:npl=250,tonemap=mobius,zscale=t=bt709:m=bt709:p=bt709:r=tv,format=yuv420p,eq=contrast=1.06:saturation=1.05:gamma=1.02
```
- `tonemap=mobius` beat `hable` for natural skin. `npl=250` controls white blowout.
- Validate every look on a still with vision before committing to a slow render.

## 4. Transcription (ffmpeg built-in whisper)

Download model once:
```
curl -L -o ggml-large-v3-turbo.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin?download=true"
```
Extract the EXACT segment you'll caption, then transcribe (large `queue` = reliable
timing on the short file):
```
ffmpeg -y -loglevel error -ss 35.7 -to 102.5 -i "C:/path/in.MOV" -vn \
  -af "highpass=f=85,lowpass=f=7500,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5" -ac 1 -ar 16000 asr.wav
ffmpeg -y -loglevel error -i asr.wav \
  -af "whisper=model=ggml-large-v3-turbo.bin:language=pt:format=srt:destination=out.srt:max_len=32:queue=90:use_gpu=false" \
  -f null -
```
Runs on CPU (~real-time-ish for turbo); run it `background=true, notify_on_complete=true`.
Then hand-edit the SRT: fix errors, split into 2-4 word Reels lines, confirm proper
nouns with the user.

## 5. Subtitles: SRT → ASS with brand styling

ASS header (1080x1920, Campton font in ./assets, white text + dark outline/shadow,
brand-green style variant):
```
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MP,Campton,58,&H00FFFFFF,&H00FFFFFF,&H00332600,&H96000000,-1,0,0,0,100,100,0.4,0,1,3.5,2.2,2,90,90,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
```
Dialogue lines: `{\fad(140,140)}` fade; wrap brand keywords in
`{\c&H0011A600&}word{\c&H00FFFFFF&}` (green #00a611 as BGR); interviewer question
wrapped in `{\i1}...{\i0}`. Copy `CamptonBold.otf` → `assets/Campton.otf`.
Burn: `subtitles=legendas.ass:fontsdir=assets`. To burn on a still-frame test,
render a real subclip (single-frame extraction drops the subs due to PTS).

## 6. Punch-ins with zoompan (sum of gaussians)

Zoom curve peaked at emphasis moments; `T=on/60` seconds when `d=1`:
```
zoompan=z='1.13+0.15*exp(-pow((on/60-9.6)/3.0,2))+0.19*exp(-pow((on/60-40.6)/2.8,2))+0.22*exp(-pow((on/60-60.6)/3.2,2))':x='iw*0.53-(iw/zoom/2)':y='ih*0.50-(ih/zoom/2)':d=1:s=1080x1920:fps=60
```
- Reframe base zoom (~1.13) also crops out edge intruders (interviewer reflections).
- `crop` CANNOT do this (output size fixed at init) — use zoompan.
- To hide a standing interviewer during a question, tighter zoom + shift left; if
  they can't be fully removed, use the Ken-Burns-still cover (section 8).

## 7. Ken Burns still (opening hero over question audio)

Still needs a framerate so it yields finite frames; zoompan `d=1`; slope in FRAMES:
```
ffmpeg -y -loglevel error -loop 1 -framerate 60 -t 6.7 -i hero_4k.png \
  -filter_complex "[0:v]scale=2160:3840,zoompan=z='1.06+0.0002*on':x='iw*0.53-(iw/zoom/2)':y='ih*0.47-(ih/zoom/2)':d=1:s=1080x1920:fps=60,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 60 segA.mp4
```
(1.06→1.14 over 402 frames = slope 0.0002/frame. `d=402` here would explode the
frame count — see SKILL pitfall.)

## 8. Two-segment render + clean concat (ships without corruption)

Render each segment to its own clean MP4 (segA still, segB live take), then:
```
printf "file 'segA.mp4'\nfile 'segB.mp4'\n" > list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy video_concat.mp4
ffmpeg -v error -i video_concat.mp4 -f null -   # MUST print nothing (0 errors)
```
Never use the `concat` FILTER across a looped-still segment — it corrupted the
H.264 (Invalid NAL unit size). Demuxer concat of pre-rendered segments is clean.

## 9. Audio: voice cleanup + ducked music bed (CORRECT graph)

```
ffmpeg -y -loglevel error -ss 29.0 -to 102.5 -i "C:/path/in.MOV" -i trilha.wav \
 -filter_complex "\
[0:a]highpass=f=90,lowpass=f=9000,afftdn=nf=-24,acompressor=threshold=-20dB:ratio=3:attack=8:release=200,equalizer=f=180:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=2:g=2,loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[voz_mix][voz_sc];\
[1:a]atrim=0:73.5,asetpts=PTS-STARTPTS,volume=0.30,afade=t=in:st=0:d=2.5,afade=t=out:st=69.5:d=3.5[bg];\
[bg][voz_sc]sidechaincompress=threshold=0.03:ratio=10:attack=5:release=350[bg_duck];\
[voz_mix][bg_duck]amix=inputs=2:weights=1 1:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95,aresample=48000[aout]" \
 -map "[aout]" -c:a pcm_s16le audio_final.wav
```
KEY: bed is the sidechaincompress MAIN input, voice is the KEY. Mix the OTHER voice
copy (`asplit`) with the ducked bed — NOT voice+[voice+bed] (doubles the voice).
Verify: `loudnorm=print_format=summary` → Integrated ~-14, TP ≤ -1.

## 10. Final mux (subtitles + logo overlay + audio) and delivery

```
ffmpeg -y -loglevel error -i video_concat.mp4 -i audio_final.wav -i assets/logo_mp_shadow.png \
 -filter_complex "[0:v]subtitles=legendas.ass:fontsdir=assets[vsub];[vsub][2:v]overlay=x=(W-w)/2:y=70:format=auto[vlogo];[vlogo]fade=t=in:st=0:d=0.6,fade=t=out:st=72.5:d=1.0[vout]" \
 -map "[vout]" -map "1:a:0" -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 19 -pix_fmt yuv420p -x264-params "keyint=120:min-keyint=60" -c:a aac -b:a 192k -ar 48000 -movflags +faststart out.mp4
ffmpeg -v error -i out.mp4 -f null -            # 0 errors
cp out.mp4 "C:/Users/<user>/Downloads/<name>.mp4"
```

## Logo drop-shadow (Pillow) so white logo reads on light backgrounds

```python
from PIL import Image, ImageFilter
im = Image.open('assets/logo_mp.png').convert('RGBA'); w,h = im.size; pad=40
canvas = Image.new('RGBA',(w+pad*2,h+pad*2),(0,0,0,0))
alpha = im.split()[3]
sh = Image.new('RGBA',canvas.size,(0,0,0,0))
black = Image.new('RGBA',im.size,(10,20,15,180))
lay = Image.composite(black, Image.new('RGBA',im.size,(0,0,0,0)), alpha)
sh.paste(lay,(pad,pad+3),lay); sh = sh.filter(ImageFilter.GaussianBlur(7))
canvas = Image.alpha_composite(canvas, sh); canvas = Image.alpha_composite(canvas, sh)
canvas.paste(im,(pad,pad),im); canvas.save('assets/logo_mp_shadow.png')
```
