from pathlib import Path
import wave
import numpy as np
from faster_whisper import WhisperModel
root=Path(r"C:\Users\phenr\mp-live-maisretorno\cortes-credito-privado\corte10\work")
with wave.open(str(root/"clip_tight.wav"),"rb") as f: audio=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(np.float32)/32768
model=WhisperModel("small",device="cpu",compute_type="int8")
segments,_=model.transcribe(audio,language="pt",vad_filter=False,word_timestamps=True,beam_size=5,initial_prompt="Banco Master, duas horas, dois meses, gestor, ações, clínicas, análise aprofundada, evitar problemas.")
for s in segments: print(f"{s.start:05.2f}-{s.end:05.2f} {s.text.strip()}")
