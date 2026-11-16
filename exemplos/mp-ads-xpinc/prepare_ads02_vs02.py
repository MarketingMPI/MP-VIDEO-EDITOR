from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS02_VS02.MOV")
cut = work / "ADS02_VS02_cut.mkv"
duration = 60.048934
silences = [
    (0.000000, 0.377500), (6.386188, 7.223937),
    (11.037500, 11.663937), (13.213000, 13.792000),
    (16.793750, 17.688562), (21.996125, 22.602313),
    (24.316313, 24.689063), (27.849375, 28.507313),
    (30.292188, 30.708375), (33.947000, 34.657000),
    (39.362500, 39.733250), (42.217750, 42.611875),
    (47.099250, 47.876063), (54.262250, 54.757625),
    (59.063000, 59.953938),
]
pad = 0.12
removals = []
for i, (start, end) in enumerate(silences):
    if i == 0:
        a, b = 0.0, end - pad
    elif i == len(silences) - 1:
        a, b = start + pad, duration
    else:
        a, b = start + pad, end - pad
    if b - a > 0.05:
        removals.append((a, b))
removed = sum(b-a for a,b in removals)
print(f"cuts={len(removals)} removed={removed:.3f}s estimated={duration-removed:.3f}s", flush=True)
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
keep = f"not({expr})"
fg = f"[0:v:0]select='{keep}',setpts=N/FRAME_RATE/TB[v];[0:a:0]aselect='{keep}',asetpts=N/SR/TB[a]"
subprocess.run([
    "ffmpeg", "-y", "-i", str(source), "-filter_complex", fg,
    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18",
    "-preset", "medium", "-c:a", "pcm_s16le", "-ar", "48000", str(cut),
], cwd=work, check=True)
subprocess.run([
    "ffmpeg", "-y", "-i", cut.name, "-vn", "-af",
    "whisper=model=ggml-large-v3-turbo.bin:language=pt:format=srt:destination=ADS02_VS02_cut.srt:queue=90:use_gpu=false",
    "-f", "null", "-",
], cwd=work, check=True)
print("DONE", flush=True)
