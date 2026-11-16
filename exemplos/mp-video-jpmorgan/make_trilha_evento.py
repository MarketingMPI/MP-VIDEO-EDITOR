# -*- coding: utf-8 -*-
# Trilha classica institucional ~58s: piano + leve cordas (pad) ao fundo.
# Arco: intro suave -> desenvolvimento -> pico sereno -> resolucao.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR=48000; BPM=68.0
beat=60.0/BPM; bar=beat*3   # 3/4
N_BARS=40
total=bar*N_BARS
n=int(total*SR)+SR
piano_buf=np.zeros(n); pad_buf=np.zeros(n)

def mf(m): return 440.0*2**((m-69)/12.0)

def piano(midi,dur,amp=1.0,tau=1.8):
    N=int(dur*SR); t=np.arange(N)/SR; f=mf(midi)
    harms=[(1,1,1),(2,0.5,1.3),(3,0.3,1.7),(4,0.18,2.2),(5,0.10,2.8),(6,0.06,3.4)]
    s=np.zeros(N)
    for k,a,dk in harms:
        s+=a*np.sin(2*np.pi*f*k*(1+0.0007*k*k)*t)*np.exp(-t/(tau/dk))
    at=int(0.008*SR); s[:at]*=np.linspace(0,1,at)
    return amp*s

def pad(midi,dur,amp=0.5):
    N=int(dur*SR); t=np.arange(N)/SR; f=mf(midi)
    s=np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2*f*t)+0.3*np.sin(2*np.pi*3*f*t)
    # vibrato lento tipo cordas
    s*= (1+0.02*np.sin(2*np.pi*5*t))
    env=np.ones(N); a=int(0.4*SR); r=int(0.6*SR)
    env[:a]=np.linspace(0,1,a); env[-r:]=np.linspace(1,0,r)
    return amp*s*env

def add(buf,sig,at):
    s=int(at*SR); e=min(s+len(sig),len(buf)); buf[s:e]+=sig[:e-s]

CH={
 'Gmaj7':(43,[59,62,66]),'Dmaj7':(38,[57,61,66]),'Em7':(40,[55,59,62]),
 'Cmaj7':(48,[52,55,59]),'Am7':(45,[60,64,67]),'D7':(38,[54,57,60]),
 'Bm7':(47,[57,62,66]),
}
prog=['Gmaj7','Dmaj7','Em7','Cmaj7','Gmaj7','Bm7','Am7','D7']

# melodia mais presente no meio (bars 8-26)
mel=[None,None,None,None,
 71,74,73,71, 69,71,None,66,
 67,71,69,67, 66,64,None,62,
 74,73,71,69, 67,66,64,62,
 66,None,None,None, None,None]

for b in range(N_BARS):
    t0=b*bar; name=prog[b%len(prog)]; bass,ch=CH[name]
    # dinamica: cresce ate o meio, resolve no fim
    dyn=0.7+0.5*np.sin(np.pi*min(b,N_BARS-b)/ (N_BARS*0.5))
    add(piano_buf, piano(bass,bar*1.05,amp=0.5*dyn,tau=2.6), t0)
    for beatpos in [1,2]:
        for ntn in ch:
            add(piano_buf, piano(ntn,beat*1.6,amp=0.14*dyn,tau=1.5), t0+beatpos*beat)
    # pad de cordas sustenta o acorde (bem suave, entra apos intro)
    if b>=3:
        for ntn in ch:
            add(pad_buf, pad(ntn+12,bar*1.0,amp=0.06*dyn), t0)
        add(pad_buf, pad(bass+12,bar*1.0,amp=0.05*dyn), t0)
    if b<len(mel) and mel[b] is not None:
        add(piano_buf, piano(mel[b],bar*1.15,amp=0.32*dyn,tau=2.2), t0+0.02)

out=piano_buf+pad_buf
out/=np.max(np.abs(out))+1e-9

def reverb(x):
    d=[0.019,0.033,0.051,0.077,0.104,0.139]; g=[0.5,0.4,0.32,0.24,0.17,0.11]
    y=x.copy()
    for dd,gg in zip(d,g):
        di=int(dd*SR); y+=gg*np.concatenate([np.zeros(di),x])[:len(x)]
    return y
mix=0.7*out+0.42*reverb(out)
mix=sosfilt(butter(4,4400/(SR/2),btype='low',output='sos'),mix)
mix=sosfilt(butter(2,52/(SR/2),btype='high',output='sos'),mix)
fi=int(2.5*SR); fo=int(4.5*SR)
mix[:fi]*=np.linspace(0,1,fi); mix[-fo:]*=np.linspace(1,0,fo)
mix/=np.max(np.abs(mix))+1e-9; mix*=10**(-3.5/20)
right=np.concatenate([np.zeros(int(0.012*SR)),mix])[:len(mix)]
st=(np.stack([mix,right],axis=1)*32767).astype(np.int16)
wavfile.write("trilha_jp.wav",SR,st)
print("trilha_jp.wav:",st.shape[0]/SR,"s")
