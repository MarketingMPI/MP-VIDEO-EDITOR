from pathlib import Path
import subprocess,json,re
import numpy as np
W=Path(__file__).parent
SRC='C:/Users/phenr/OneDrive/Documentos/Meu Patrimônio/Interno/Gravação de Onborading - MP PRO/Mariana .mp4'
p=subprocess.run(['ffmpeg','-v','error','-i',SRC,'-vn','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True)
a=np.frombuffer(p.stdout,dtype=np.float32); n=len(a)//320
rms=np.sqrt(np.mean(a[:n*320].reshape(n,320)**2,axis=1)); db=20*np.log10(np.maximum(rms,1e-10))
print('20ms RMS percentiles', dict(zip([1,5,10,20,30,50,75,90,99],np.percentile(db,[1,5,10,20,30,50,75,90,99]).tolist())))
np.save(W/'analysis'/'rms_db.npy',db)
p=subprocess.run(['ffmpeg','-hide_banner','-i',SRC,'-vn','-af','silencedetect=noise=-44dB:d=0.65','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
(W/'analysis'/'silence_conservative.log').write_text(p.stderr,encoding='utf-8')
starts=list(map(float,re.findall(r'silence_start: ([0-9.]+)',p.stderr)));ends=list(map(float,re.findall(r'silence_end: ([0-9.]+)',p.stderr)))
iv=list(zip(starts,ends));(W/'analysis'/'silences_conservative.json').write_text(json.dumps(iv,indent=2))
print('pauses',len(iv),'total',sum(b-a for a,b in iv))
print('longest',sorted(iv,key=lambda x:x[1]-x[0],reverse=True)[:35])
