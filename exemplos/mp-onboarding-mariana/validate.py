from pathlib import Path
import subprocess,json,re
from PIL import Image,ImageDraw
W=Path(__file__).parent
OUT=W/'out/Mariana - Onboarding MP PRO - Editado.mp4'
P=json.loads((W/'analysis/edit_plan.json').read_text())
def run(args):
 return subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUT)]).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert len(probe['streams'])==2
assert (v['width'],v['height'])==(1280,720)
assert int(v['nb_frames'])==P['output_frames'],(v['nb_frames'],P['output_frames'])
assert abs(float(v['duration'])-float(a['duration']))<1/30
assert v['start_time']==a['start_time']=='0.000000'
q=run(['ffmpeg','-v','error','-i',str(OUT),'-f','null','-'])
(W/'analysis/decode_errors.log').write_text(q.stderr)
assert not q.stderr.strip(),q.stderr
m=run(['ffmpeg','-hide_banner','-i',str(OUT),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']).stderr
measure=json.loads(m[m.rfind('{'):m.rfind('}')+1]);(W/'analysis/final_loudness.json').write_text(json.dumps(measure,indent=2))
assert -17<float(measure['input_i'])<-15
assert float(measure['input_tp'])<=-1.0
# Sample the actual final file, including the tail, rather than the preview only.
times=[5,30,180,360,540,720,900,968]
sheet=Image.new('RGB',(1280,4*384),(25,25,25));d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 f=W/'analysis'/f'final_{t}.jpg'
 run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(OUT),'-frames:v','1','-vf','scale=640:-2',str(f)])
 sheet.paste(Image.open(f),((i%2)*640,(i//2)*384));d.text(((i%2)*640+8,(i//2)*384+362),f'{t//60:02}:{t%60:02}',fill='white')
sheet.save(W/'analysis/final_contact.jpg')
report={'decode_errors':0,'video_frames':int(v['nb_frames']),'video_duration':float(v['duration']),'audio_duration':float(a['duration']),'av_duration_difference':abs(float(v['duration'])-float(a['duration'])),'integrated_lufs':float(measure['input_i']),'true_peak_dbtp':float(measure['input_tp']),'lra_lu':float(measure['input_lra']),'file_size_mb':round(OUT.stat().st_size/1e6,2),'cut_count':len(P['cuts_frames']),'removed_seconds':sum(b-a for a,b in P['cuts_frames'])/30}
(W/'analysis/validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
