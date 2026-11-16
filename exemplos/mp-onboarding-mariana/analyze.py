from pathlib import Path
import subprocess,json,re,concurrent.futures
from PIL import Image,ImageDraw
W=Path(__file__).parent
SRC=Path('C:/Users/phenr/OneDrive/Documentos/Meu Patrimônio/Interno/Gravação de Onborading - MP PRO/Mariana .mp4')
FF='C:/Users/phenr/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe'
for sub in ['analysis','chunks','srt','out']: (W/sub).mkdir(exist_ok=True)
def cmd(args,log):
 p=subprocess.run([FF,'-hide_banner','-nostdin','-y',*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',cwd=W)
 (W/'analysis'/log).write_text(p.stderr,encoding='utf-8')
 if p.returncode: raise RuntimeError(p.stderr[-3000:])
 return p.stderr

def frames():
 times=[0,5,30,90,180,270,360,450,540,630,720,810,900,980,1010]
 sheet=Image.new('RGB',(960, len(times)//3*204),(25,25,25)); d=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  p=W/'analysis'/f'frame_{t:04}.jpg'
  cmd(['-loglevel','error','-ss',str(t),'-i',str(SRC),'-frames:v','1','-vf','scale=640:-2',str(p)],f'frame_{t}.log')
  im=Image.open(p); im.thumbnail((320,180)); x=(i%3)*320;y=(i//3)*204;sheet.paste(im,(x,y)); d.text((x+5,y+183),f'{t//60:02}:{t%60:02}',fill='white')
 sheet.save(W/'analysis'/'contact.jpg')
 print('frames ready',flush=True)
def audio():
 s=cmd(['-i',str(SRC),'-vn','-af','silencedetect=noise=-38dB:d=0.45,loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],'audio.log')
 starts=re.findall(r'silence_start: ([0-9.]+)',s); ends=re.findall(r'silence_end: ([0-9.]+)',s)
 intervals=list(zip(map(float,starts),map(float,ends)))
 (W/'analysis'/'silences.json').write_text(json.dumps(intervals,indent=2))
 print('AUDIO',s[-1300:], 'pauses',len(intervals),flush=True)
def transcription():
 # Exact 90-second chunks avoid accumulated ASR timestamp drift.
 for i,start in enumerate(range(0,1016,90)):
  wav=f'chunks/chunk_{i:02}.wav'; srt=f'srt/chunk_{i:02}.srt'
  cmd(['-loglevel','error','-ss',str(start),'-i',str(SRC),'-t','90','-vn','-ac','1','-ar','16000',wav],f'extract_{i}.log')
  cmd(['-loglevel','warning','-i',wav,'-af',f'whisper=model=../mp-live-maisretorno/ggml-large-v3-turbo.bin:language=pt:format=srt:destination={srt}:queue=90:use_gpu=false','-f','null','-'],f'asr_{i}.log')
  print(f'Transcribed {i+1}/12',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 tasks=[pool.submit(f) for f in [frames,audio,transcription]]
 for f in tasks:f.result()
print('ANALYSIS COMPLETE',flush=True)
