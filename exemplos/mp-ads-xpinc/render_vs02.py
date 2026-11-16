from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS01_VS02.MOV")
audio = work / "ADS01_VS02_audio_master.wav"
out = work / "ADS01_VS02_editado.mp4"
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
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
keep = f"not({expr})"
vf = (
    f"[0:v:0]select='{keep}',setpts=N/FRAME_RATE/TB,"
    "hflip,"
    "eq=contrast=1.03:saturation=1.04:gamma=1.01:brightness=-0.004,"
    "subtitles=filename=ADS01_VS02.ass:fontsdir=fonts[v]"
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
