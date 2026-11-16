# -*- coding: utf-8 -*-
# Gera whooshes sutis de transicao (ruido filtrado com sweep + envelope).
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR=48000

def whoosh(dur=0.7, f_start=400, f_end=2500, amp=0.35, reverse=False):
    N=int(dur*SR); t=np.arange(N)/SR
    noise=np.random.randn(N)*0.5
    # sweep de banda: filtro passa-banda movel aproximado por 2 estagios
    # envelope: sobe e desce (whoosh)
    env=np.sin(np.pi*t/dur)**1.6
    # filtro passa-baixa variavel: aplica LP com cutoff medio + HP
    cut_hi=np.linspace(f_start,f_end,N)
    # aproxima: filtra com LP fixo alto e HP fixo, modula amplitude por env
    sos_bp_lo=butter(2, max(f_start,120)/(SR/2), btype='high', output='sos')
    sos_bp_hi=butter(4, min(f_end,6000)/(SR/2), btype='low', output='sos')
    s=sosfilt(sos_bp_lo,noise); s=sosfilt(sos_bp_hi,s)
    s*=env
    if reverse: s=s[::-1]
    s/=np.max(np.abs(s))+1e-9
    return (amp*s).astype(np.float32)

# um whoosh suave padrao
w=whoosh(0.8, 300, 2200, amp=0.5)
# fade extra nas pontas
fi=int(0.05*SR)
w[:fi]*=np.linspace(0,1,fi); w[-fi:]*=np.linspace(1,0,fi)
st=np.stack([w,w],axis=1)
st=(st*32767).astype(np.int16)
wavfile.write("whoosh.wav",SR,st)
print("whoosh.wav:",len(w)/SR,"s")

# um "shimmer/chime" bem sutil para o close do brinde (opcional)
def chime(dur=1.2, base=880, amp=0.18):
    N=int(dur*SR); t=np.arange(N)/SR
    s=np.zeros(N)
    for k,a in [(1,1),(2,0.5),(3,0.3),(4.2,0.2)]:
        s+=a*np.sin(2*np.pi*base*k*t)*np.exp(-t*3.5)
    s/=np.max(np.abs(s))+1e-9
    return (amp*s).astype(np.float32)
c=chime()
stc=(np.stack([c,c],axis=1)*32767).astype(np.int16)
wavfile.write("chime.wav",SR,stc)
print("chime.wav:",len(c)/SR,"s")
