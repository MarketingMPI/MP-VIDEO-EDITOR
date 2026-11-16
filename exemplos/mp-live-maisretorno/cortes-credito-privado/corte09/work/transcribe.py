from pathlib import Path
import wave,json
import numpy as np
from faster_whisper import WhisperModel
root=Path(r"C:\Users\phenr\mp-live-maisretorno\cortes-credito-privado\corte09\work")
with wave.open(str(root/"clip.wav"),"rb") as f: audio=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(np.float32)/32768
model=WhisperModel("small",device="cpu",compute_type="int8")
segments,_=model.transcribe(audio,language="pt",vad_filter=False,word_timestamps=True,beam_size=5,initial_prompt="Juros altos, lucro operacional, pagamento de juros, Casa Bahia, prejuízo, crédito corporativo.")
rows=[]
for s in segments: rows.append({"start":round(s.start,3),"end":round(s.end,3),"text":s.text.strip()})
(root/"transcript.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
for s in rows: print(f"{s['start']:05.2f}-{s['end']:05.2f} {s['text']}")
