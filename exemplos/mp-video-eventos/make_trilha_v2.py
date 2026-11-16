# -*- coding: utf-8 -*-
# Trilha NOVA e diferente: cordas cinematograficas em tom menor elegante (Am/Em),
# arpejos fluidos + pad de cordas + violoncelo grave. Mais solene/emotivo que as anteriores.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR=48000; BPM=72.0
beat=60.0/BPM; bar=beat*4   # 4/4
N_BARS=26
total=bar*N_BARS
n=int(total*SR)+SR
arp=np.zeros(n); pad=np.zeros(n); bass=np.zeros(n); lead=np.zeros(n)

def mf(m): return 440.0*2**((m-69)/12.0)

def string(midi,dur,amp=1.0,attack=0.12,release=0.5):
    # timbre de cordas: serra suavizada + vibrato + swell
    N=int(dur*SR); t=np.arange(N)/SR; f=mf(midi)
    vib=1+0.006*np.sin(2*np.pi*5.2*t)
    s=np.zeros(N)
    for k,a in [(1,1.0),(2,0.5),(3,0.33),(4,0.22),(5,0.14),(6,0.09)]:
        s+=a*np.sin(2*np.pi*f*k*vib*t)/k
    env=np.ones(N)
    ai=int(attack*SR); ri=int(release*SR)
    if ai>0: env[:ai]=np.linspace(0,1,ai)**1.5
    if ri>0: env[-ri:]=np.linspace(1,0,ri)**1.5
    return amp*s*env

def pluck(midi,dur,amp=0.5):
    # arpejo dedilhado (harpa/pizzicato) decaimento rapido
    N=int(dur*SR); t=np.arange(N)/SR; f=mf(midi)
    s=np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*2*f*t)+0.2*np.sin(2*np.pi*3*f*t)
    s*=np.exp(-t*4.5)
    at=int(0.004*SR); s[:at]*=np.linspace(0,1,at)
    return amp*s

def add(buf,sig,at):
    s=int(at*SR); e=min(s+len(sig),len(buf)); buf[s:e]+=sig[:e-s]

# Progressao em Lá menor, elegante: Am - F - C - G - Am - Em - F - E
# (midi do baixo, notas do acorde)
CH={
 'Am':(45,[57,60,64]),   # A C E
 'F' :(41,[57,60,65]),   # F A C
 'C' :(48,[55,60,64]),   # C E G
 'G' :(43,[59,62,67]),   # G B D
 'Em':(40,[59,62,67]),   # E G B
 'Dm':(38,[57,62,65]),   # D F A
 'E' :(40,[56,59,64]),   # E G# B
}
prog=['Am','F','C','G','Am','Em','Dm','E']

# melodia de violino (linha superior) - entra bar 6
mel=[None,None,None,None, None,
 76,74,72,71, 69,72,76,74,      # b6-13
 72,71,69,67, 69,72,74,76,      # b14-21
 72,69,None,None, None]          # b22-26

for b in range(N_BARS):
    t0=b*bar; name=prog[b%len(prog)]; b_midi,ch=CH[name]
    dyn=0.65+0.5*np.sin(np.pi*min(b,N_BARS-b)/(N_BARS*0.5))
    # violoncelo grave sustentado (root -12)
    add(bass, string(b_midi-12, bar*1.02, amp=0.42*dyn, attack=0.25, release=0.7), t0)
    # pad de cordas com o acorde (sustentado)
    for ntn in ch:
        add(pad, string(ntn, bar*1.0, amp=0.10*dyn, attack=0.3, release=0.6), t0)
    # arpejo fluido (harpa) subindo/descendo ao longo do compasso
    arp_notes=ch+[ch[0]+12]+ch[::-1]
    for i,ntn in enumerate(arp_notes):
        add(arp, pluck(ntn, beat*1.2, amp=0.16*dyn), t0+i*(bar/len(arp_notes)))
    # melodia violino
    if b<len(mel) and mel[b] is not None:
        add(lead, string(mel[b], bar*1.1, amp=0.26*dyn, attack=0.15, release=0.7), t0+0.03)

out=bass+pad+arp+lead
out/=np.max(np.abs(out))+1e-9

def reverb(x):
    d=[0.023,0.041,0.061,0.089,0.117,0.151]; g=[0.55,0.44,0.35,0.27,0.19,0.12]
    y=x.copy()
    for dd,gg in zip(d,g):
        di=int(dd*SR); y+=gg*np.concatenate([np.zeros(di),x])[:len(x)]
    return y
mix=0.68*out+0.46*reverb(out)   # mais reverb = cinematografico
mix=sosfilt(butter(4,4800/(SR/2),btype='low',output='sos'),mix)
mix=sosfilt(butter(2,48/(SR/2),btype='high',output='sos'),mix)
fi=int(2.0*SR); fo=int(4.5*SR)
mix[:fi]*=np.linspace(0,1,fi); mix[-fo:]*=np.linspace(1,0,fo)
mix/=np.max(np.abs(mix))+1e-9; mix*=10**(-3.5/20)
right=np.concatenate([np.zeros(int(0.013*SR)),mix])[:len(mix)]
st=(np.stack([mix,right],axis=1)*32767).astype(np.int16)
wavfile.write("trilha_evento_v2.wav",SR,st)
print("trilha_evento_v2.wav:",st.shape[0]/SR,"s")
