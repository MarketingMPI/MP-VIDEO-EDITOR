from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS01_VS02.MOV")
cut = work / "ADS01_VS02_cut.mkv"
duration = 49.394966
silences = [
    (5.610938, 6.269125), (10.323063, 10.704063),
    (11.067938, 11.743813), (14.162063, 14.969688),
    (16.675687, 17.221563), (19.675125, 20.063500),
    (23.713812, 24.144687), (30.548625, 31.189625),
    (36.110937, 36.477938), (39.135438, 39.690063),
    (42.207250, 42.622000), (43.698875, 44.179125),
    (46.699125, 47.143937), (48.250687, 49.296000),
]
pad = 0.12
removals = []
for i, (start, end) in enumerate(silences):
    if i == len(silences) - 1 and end >= duration - 0.2:
        a, b = start + pad, duration
    else:
        a, b = start + pad, end - pad
    if b - a > 0.05:
        removals.append((a, b))
removed = sum(b - a for a, b in removals)
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
    "whisper=model=ggml-large-v3-turbo.bin:language=pt:format=srt:destination=ADS01_VS02_cut.srt:queue=90:use_gpu=false",
    "-f", "null", "-",
], cwd=work, check=True)
print("DONE", flush=True)
