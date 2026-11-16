from pathlib import Path
import subprocess,json,sys
W=Path(__file__).parent
P=json.loads((W/'analysis/edit_plan.json').read_text()); M=json.loads((W/'analysis/voice_measure.json').read_text())
preview='--preview' in sys.argv
expr='+'.join(f'between(n,{a},{b-1})' for a,b in P['cuts_frames'])
vf=f"select='not({expr})',setpts=N/(30*TB),{P['video_filter']}"
af=f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={M['input_i']}:measured_TP={M['input_tp']}:measured_LRA={M['input_lra']}:measured_thresh={M['input_thresh']}:offset={M['target_offset']}:linear=false,aresample=48000"
out=W/('analysis/preview.mp4' if preview else 'out/Mariana - Onboarding MP PRO - Editado.mp4')
args=['ffmpeg','-hide_banner','-nostdin','-y','-filter_threads','2','-i',P['source'],'-i',str(W/'analysis/voice_cut.wav'),'-map','0:v:0','-map','1:a:0','-vf',vf,'-af',af,'-c:v','libx264','-crf','17','-preset','medium','-threads','4','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-c:a','aac','-b:a','192k','-ar','48000','-map_metadata','-1','-metadata','title=Mariana | Onboarding MP PRO','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart']
args+=['-t','35' if preview else f"{P['output_frames']/P['fps']:.9f}"]
args+=[str(out)]
with (W/'analysis'/('render_preview.log' if preview else 'render.log')).open('w',encoding='utf-8') as log:
 p=subprocess.run(args,stdout=log,stderr=log)
if p.returncode:raise RuntimeError('Render failed; inspect log')
print('RENDER COMPLETE',out,flush=True)
