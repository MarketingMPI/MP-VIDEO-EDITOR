from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS01_VS03.MOV")
cut = work / "ADS01_VS03_cut.mkv"
duration = 49.988005
audio_delay_ms = 692
silences = [
    (4.326500, 5.282250), (9.270938, 10.049125),
    (10.367000, 10.838437), (13.026312, 13.641188),
    (15.392062, 16.104500), (17.287562, 17.712813),
    (21.738188, 22.165813), (26.291750, 26.682125),
    (29.035187, 29.594313), (34.515563, 34.924875),
    (39.695125, 40.232250), (44.076250, 44.579375),
    (48.384313, 49.296000),
]
pad = 0.12
removals = []
for i, (start, end) in enumerate(silences):
    if i == len(silences) - 1:
        a, b = start + pad, duration
    else:
        a, b = start + pad, end - pad
    if b - a > 0.05:
        removals.append((a, b))
removed = sum(b - a for a, b in removals)
print(f"cuts={len(removals)} removed={removed:.3f}s estimated={duration-removed:.3f}s", flush=True)
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
keep = f"not({expr})"
fg = (
    f"[0:v:0]select='{keep}',setpts=N/FRAME_RATE/TB[v];"
    f"[0:a:0]aselect='{keep}',asetpts=N/SR/TB,adelay={audio_delay_ms}|{audio_delay_ms}[a]"
)
subprocess.run([
    "ffmpeg", "-y", "-i", str(source), "-filter_complex", fg,
    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18",
    "-preset", "medium", "-c:a", "pcm_s16le", "-ar", "48000", str(cut),
], cwd=work, check=True)
subprocess.run([
    "ffmpeg", "-y", "-i", cut.name, "-vn", "-af",
    "whisper=model=ggml-large-v3-turbo.bin:language=pt:format=srt:destination=ADS01_VS03_cut.srt:queue=90:use_gpu=false",
    "-f", "null", "-",
], cwd=work, check=True)
print("DONE", flush=True)
