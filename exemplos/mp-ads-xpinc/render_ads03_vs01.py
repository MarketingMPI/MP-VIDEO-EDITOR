from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS03_VS01.MOV")
audio = work / "ADS03_VS01_audio_master.wav"
out = work / "ADS03_VS01_editado.mp4"
duration = 60.006485
silences = [
    (0.000000, 0.619000),
    (4.383750, 4.803063), (16.053687, 16.632062),
    (18.565188, 19.354563), (23.712625, 24.200125),
    (27.431375, 27.812188), (29.916000, 30.718063),
    (36.966875, 37.730375), (44.048313, 44.484000),
    (46.537688, 47.153438), (49.496625, 49.900125),
    (54.629500, 55.092937), (58.842562, 59.907500),
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
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
keep = f"not({expr})"
vf = (
    f"[0:v:0]select='{keep}',setpts=N/FRAME_RATE/TB,"
    "hflip,"
    "eq=contrast=1.025:saturation=1.035:gamma=1.005:brightness=-0.005,"
    "subtitles=filename=ADS03_VS01.ass:fontsdir=fonts[v]"
)
cmd = [
    "ffmpeg", "-y", "-i", str(source), "-i", str(audio),
    "-filter_complex", vf, "-map", "[v]", "-map", "1:a:0",
    "-c:v", "libx264", "-preset", "veryslow", "-crf", "14",
    "-profile:v", "high", "-pix_fmt", "yuv420p",
    "-color_primaries", "bt709", "-color_trc", "bt709",
    "-colorspace", "bt709", "-color_range", "tv",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
    "-movflags", "+faststart", str(out),
]
subprocess.run(cmd, cwd=work, check=True)
print(f"DONE: {out}")
