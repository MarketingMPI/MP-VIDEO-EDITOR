# -*- coding: utf-8 -*-
# Piano solo sereno estilo Satie/Gymnopedie. Variacao propria p/ Corte A.
# Progressao em Dó e melodia novas (diferente das trilhas anteriores).
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
BPM = 64.0
beat = 60.0/BPM
bar = beat*3
N_BARS = 34
total = bar*N_BARS
n_total = int(total*SR)+SR
out = np.zeros(n_total)

def midi_to_freq(m): return 440.0*2**((m-69)/12.0)

def piano(midi, dur, amp=1.0, tau=1.7):
    n=int(dur*SR); t=np.arange(n)/SR; f=midi_to_freq(midi)
    harms=[(1,1.0,1.0),(2,0.5,1.3),(3,0.3,1.7),(4,0.18,2.2),(5,0.10,2.8),(6,0.06,3.4)]
    sig=np.zeros(n)
    for k,a,dk in harms:
        inh=1+0.0007*k*k
        sig+=a*np.sin(2*np.pi*f*k*inh*t)*np.exp(-t/(tau/dk))
    at=int(0.008*SR)
    if at>0: sig[:at]*=np.linspace(0,1,at)
    return amp*sig

def add(buf,sig,at_t):
    s=int(at_t*SR); e=min(s+len(sig),len(buf)); buf[s:e]+=sig[:e-s]

# Progressao nova em C: Cmaj7 Am7 Fmaj7 G7 / Em7 Am7 Dm7 G7
CH={
 'Cmaj7':(48,[52,55,59]),  # C E G B
 'Am7'  :(45,[52,55,60]),  # A E G C
 'Fmaj7':(41,[53,57,60]),  # F A C E
 'G7'   :(43,[53,57,62]),  # G F A D
 'Em7'  :(40,[55,59,62]),  # E G B D
 'Dm7'  :(38,[53,57,60]),  # D F A C
}
prog=['Cmaj7','Am7','Fmaj7','G7','Em7','Am7','Dm7','G7']

# melodia esparsa nova (entra no bar 3)
melody=[None,None,
 72,71,67,69, 65,67,None,72,       # b3-10
 76,74,72,71, 69,67,None,64,       # b11-18
 65,67,69,71, 72,69,None,None,     # b19-26
 67,64,None,None, None,None,None,None]  # cauda

for b in range(N_BARS):
    t0=b*bar; name=prog[b%len(prog)]; bass,chord=CH[name]
    add(out,piano(bass,bar*1.05,amp=0.5,tau=2.6),t0)
    for beatpos in [1,2]:
        for ntn in chord:
            add(out,piano(ntn,beat*1.6,amp=0.15,tau=1.5),t0+beatpos*beat)
    if b<len(melody) and melody[b] is not None:
        add(out,piano(melody[b],bar*1.15,amp=0.33,tau=2.2),t0+0.02)
        add(out,piano(melody[b]+12,bar*0.5,amp=0.05,tau=1.2),t0+0.02)

out/=np.max(np.abs(out))+1e-9
def reverb(x):
    d=[0.021,0.037,0.053,0.079,0.107,0.141]; g=[0.5,0.4,0.32,0.24,0.17,0.11]; y=x.copy()
    for dd,gg in zip(d,g):
        di=int(dd*SR); y+=gg*np.concatenate([np.zeros(di),x])[:len(x)]
    return y
wet=reverb(out); mix=0.7*out+0.4*wet
mix=sosfilt(butter(4,4200/(SR/2),btype='low',output='sos'),mix)
mix=sosfilt(butter(2,55/(SR/2),btype='high',output='sos'),mix)
fi=int(2.5*SR); fo=int(4.0*SR)
mix[:fi]*=np.linspace(0,1,fi); mix[-fo:]*=np.linspace(1,0,fo)
mix/=np.max(np.abs(mix))+1e-9; mix*=10**(-4.0/20)
right=np.concatenate([np.zeros(int(0.012*SR)),mix])[:len(mix)]
st=(np.stack([mix,right],axis=1)*32767).astype(np.int16)
wavfile.write("out/trilha_A.wav",SR,st)
print("out/trilha_A.wav:", st.shape[0]/SR,"s")
