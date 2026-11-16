from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS02_VS01.MOV")
cut = work / "ADS02_VS01_cut.mkv"
duration = 52.975851
silences = [
    (0.000000, 0.465250), (1.911312, 2.263250),
    (8.493375, 9.012813), (10.305312, 10.965750),
    (13.952875, 14.942438), (18.958875, 19.618750),
    (21.861187, 22.239062), (25.503688, 26.018062),
    (32.867063, 33.489063), (37.271750, 37.712875),
    (42.865687, 43.658875), (47.120562, 47.707000),
    (51.902875, 52.871875),
]
pad = 0.12
removals = []
for i, (start, end) in enumerate(silences):
    if start == 0:
        a, b = 0.0, end - pad
    elif i == len(silences) - 1:
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
    f"[0:a:0]aselect='{keep}',asetpts=N/SR/TB[a]"
)
subprocess.run([
    "ffmpeg", "-y", "-i", str(source), "-filter_complex", fg,
    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18",
    "-preset", "medium", "-c:a", "pcm_s16le", "-ar", "48000", str(cut),
], cwd=work, check=True)
subprocess.run([
    "ffmpeg", "-y", "-i", cut.name, "-vn", "-af",
    "whisper=model=ggml-large-v3-turbo.bin:language=pt:format=srt:destination=ADS02_VS01_cut.srt:queue=90:use_gpu=false",
    "-f", "null", "-",
], cwd=work, check=True)
print("DONE", flush=True)
