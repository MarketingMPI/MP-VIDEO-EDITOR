from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS02_VS02.MOV")
audio = work / "ADS02_VS02_audio_master.wav"
out = work / "ADS02_VS02_editado.mp4"
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
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
keep = f"not({expr})"
vf = (
    f"[0:v:0]select='{keep}',setpts=N/FRAME_RATE/TB,"
    "hflip,"
    "eq=contrast=1.03:saturation=1.03:gamma=1.015:brightness=-0.003,"
    "subtitles=filename=ADS02_VS02.ass:fontsdir=fonts[v]"
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
