from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS02_VS01.MOV")
audio = work / "ADS02_VS01_audio_master.wav"
out = work / "ADS02_VS01_editado.mp4"
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
    "eq=contrast=1.03:saturation=1.03:gamma=1.015:brightness=-0.003,"
    "subtitles=filename=ADS02_VS01.ass:fontsdir=fonts[v]"
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
