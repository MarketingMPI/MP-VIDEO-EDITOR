from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS01_VS01.MOV")
cut = work / "ADS01_VS01_cut.mkv"

silences = [
    (0.000000, 0.753125), (4.966625, 5.531313),
    (8.887562, 9.249875), (9.706437, 10.551375),
    (12.928313, 13.748563), (15.876812, 16.260500),
    (17.426813, 17.876625), (19.931812, 20.369688),
    (22.139750, 22.611688), (25.548938, 25.915375),
    (29.071813, 29.904063), (33.914813, 34.333625),
    (39.350875, 39.821125), (43.552813, 44.093688),
    (48.188813, 49.528188),
]
pad = 0.12
duration = 49.642177
removals = []
for i, (start, end) in enumerate(silences):
    if i == 0 and start == 0:
        a, b = 0.0, end - pad
    elif i == len(silences) - 1 and end >= duration - 0.2:
        a, b = start + pad, duration
    else:
        a, b = start + pad, end - pad
    if b - a > 0.05:
        removals.append((a, b))
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
keep = f"not({expr})"
filtergraph = (
    f"[0:v:0]select='{keep}',setpts=N/FRAME_RATE/TB[v];"
    f"[0:a:0]aselect='{keep}',asetpts=N/SR/TB[a]"
)
cmd_cut = [
    "ffmpeg", "-y", "-i", str(source), "-filter_complex", filtergraph,
    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18",
    "-preset", "medium", "-c:a", "pcm_s16le", "-ar", "48000", str(cut),
]
print("Preparing silence-cut intermediate...", flush=True)
subprocess.run(cmd_cut, cwd=work, check=True)
print("Transcribing cut video...", flush=True)
cmd_whisper = [
    "ffmpeg", "-y", "-i", cut.name, "-vn", "-af",
    "whisper=model=ggml-large-v3-turbo.bin:language=pt:format=srt:destination=ADS01_VS01_cut.srt:queue=90:use_gpu=false",
    "-f", "null", "-",
]
subprocess.run(cmd_whisper, cwd=work, check=True)
print("DONE", flush=True)
