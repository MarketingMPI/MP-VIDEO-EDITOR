from pathlib import Path
import json,math,subprocess,wave
import numpy as np
W=Path(__file__).parent
SRC='C:/Users/phenr/OneDrive/Documentos/Meu Patrimônio/Interno/Gravação de Onborading - MP PRO/Mariana .mp4'
FPS=30; FRAMES=30473
iv=json.loads((W/'analysis/silences_conservative.json').read_text())
merged=[]
for a,b in iv:
 if merged and a-merged[-1][1]<0.10:merged[-1][1]=b
 else:merged.append([a,b])
cuts=[]
for a,b in merged:
 if b-a<0.95:continue
 # Preserve breathing room, longer at chapter-like pauses. Never cut right at speech edges.
 pad=0.32 if b-a<1.8 else 0.42
 start=math.ceil((a+pad)*FPS);end=math.floor((b-pad)*FPS)
 if b>1015 and a>1010: start=math.ceil((a+0.65)*FPS);end=FRAMES
 if end-start>=6:cuts.append([start,end])
keep=[];prev=0
for a,b in cuts:
 if a>prev:keep.append([prev,a])
 prev=b
if prev<FRAMES:keep.append([prev,FRAMES])
plan={'source':SRC,'fps':FPS,'original_frames':FRAMES,'cuts_frames':cuts,'keep_frames':keep,'output_frames':sum(b-a for a,b in keep),'video_filter':"unsharp=5:5:0.15:3:3:0",'audio_filter':'highpass=f=70,afftdn=nr=6:nf=-60:tn=1,agate=threshold=0.002:ratio=1.4:range=0.5:attack=15:release=180,equalizer=f=200:t=q:w=0.8:g=-1,acompressor=threshold=0.065:ratio=1.6:attack=15:release=180:makeup=1'}
(W/'analysis/edit_plan.json').write_text(json.dumps(plan,indent=2))
print('Cuts',len(cuts),'removed_s',sum(b-a for a,b in cuts)/FPS,'duration_s',plan['output_frames']/FPS)
# Process voice on the original timeline so compressor/denoiser state is continuous.
p=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-i',SRC,'-vn','-af',plan['audio_filter'],'-ar','48000','-ac','2','-c:a','pcm_s16le',str(W/'analysis/voice_full.wav')],capture_output=True,text=True,encoding='utf-8',errors='replace')
(W/'analysis/voice_cleanup.log').write_text(p.stderr,encoding='utf-8');p.check_returncode()
with wave.open(str(W/'analysis/voice_full.wav'),'rb') as f: samples=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).reshape(-1,2).copy()
need=FRAMES*1600
if len(samples)<need:samples=np.pad(samples,((0,need-len(samples)),(0,0)))
parts=[];fade=240
for i,(a,b) in enumerate(keep):
 s=samples[a*1600:b*1600].astype(np.float32)
 if i:s[:fade]*=np.linspace(0,1,fade)[:,None]
 if i<len(keep)-1:s[-fade:]*=np.linspace(1,0,fade)[:,None]
 parts.append(s.astype(np.int16))
cut=np.concatenate(parts)
# Short fade only at the tail, without swallowing the last spoken word.
cut[-9600:]=(cut[-9600:].astype(float)*np.linspace(1,0,9600)[:,None]).astype(np.int16)
with wave.open(str(W/'analysis/voice_cut.wav'),'wb') as f:
 f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes(cut.tobytes())
p=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(W/'analysis/voice_cut.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace');p.check_returncode()
(W/'analysis/voice_measure.log').write_text(p.stderr,encoding='utf-8')
measure=json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1]);(W/'analysis/voice_measure.json').write_text(json.dumps(measure,indent=2))
print('MEASUREMENT',measure)
