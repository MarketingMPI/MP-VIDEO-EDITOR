from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS01_VS03.MOV")
audio = work / "ADS01_VS03_audio_master.wav"
out = work / "ADS01_VS03_editado.mp4"
duration = 49.988005
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
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
keep = f"not({expr})"
vf = (
    f"[0:v:0]select='{keep}',setpts=N/FRAME_RATE/TB,"
    "hflip,"
    "eq=contrast=1.045:saturation=1.055:gamma=1.015,"
    "subtitles=filename=ADS01_VS03.ass:fontsdir=fonts[v]"
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
