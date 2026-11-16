from pathlib import Path
import subprocess

work = Path(r"C:\Users\phenr\mp-ads-xpinc")
video_in = work / "ADS01_VS01_editado.mp4"
source = Path(r"C:\Users\phenr\OneDrive\Documentos\Meu Patrimônio\B2B\MP PRO\Ads Live - XP Inc\ADS01_VS01.MOV")
out = work / "ADS01_VS01_editado_audiofix.mp4"

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
audio = (
    f"[1:a:0]aselect='{keep}',asetpts=N/SR/TB,"
    "aresample=48000,"
    "pan=mono|c0=0.5*c0+0.5*c1,"
    "arnndn=m=std.rnnn,"
    "highpass=f=85,lowpass=f=9500,"
    "equalizer=f=180:t=q:w=1.2:g=-1.5,"
    "equalizer=f=3200:t=q:w=1.0:g=1.5,"
    "acompressor=threshold=0.10:ratio=2.2:attack=15:release=180:makeup=1.0,"
    "pan=stereo|c0=c0|c1=c0,"
    "loudnorm=I=-14:TP=-1.5:LRA=6,"
    "alimiter=limit=0.84[a]"
)
cmd = [
    "ffmpeg", "-y", "-i", str(video_in), "-i", str(source),
    "-filter_complex", audio, "-map", "0:v:0", "-map", "[a]",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
    "-movflags", "+faststart", "-shortest", str(out),
]
subprocess.run(cmd, cwd=work, check=True)
out.replace(video_in)
print(f"DONE: {video_in}")
