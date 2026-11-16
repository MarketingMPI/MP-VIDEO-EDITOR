# -*- coding: utf-8 -*-
# Trilha classica original: piano solo lento e sereno, estilo Satie (Gymnopedie).
# Valsa gentil 3/4, acordes maj7, melodia esparsa. Suave e discreta.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
BPM = 66.0
beat = 60.0/BPM        # ~0.909s
bar = beat*3           # 3/4
N_BARS = 28
total = bar*N_BARS
n_total = int(total*SR)+SR
out = np.zeros(n_total)

def midi_to_freq(m):
    return 440.0*2**((m-69)/12.0)

def piano(midi, dur, amp=1.0, tau=1.7):
    n = int(dur*SR)
    t = np.arange(n)/SR
    f = midi_to_freq(midi)
    # harmonicos com leve inharmonicidade; agudos decaem mais rapido
    harms = [(1,1.0,1.0),(2,0.5,1.3),(3,0.3,1.7),(4,0.18,2.2),(5,0.10,2.8),(6,0.06,3.4)]
    sig = np.zeros(n)
    for k,a,dk in harms:
        inh = 1+0.0007*k*k
        sig += a*np.sin(2*np.pi*f*k*inh*t)*np.exp(-t/(tau/dk))
    # ataque suave 8ms
    at = int(0.008*SR)
    if at>0: sig[:at]*=np.linspace(0,1,at)
    return amp*sig

def add(buf, sig, at_t):
    s = int(at_t*SR)
    e = min(s+len(sig), len(buf))
    buf[s:e]+=sig[:e-s]

# --- Acordes por compasso: (baixo_midi, [notas_acorde]) estilo Satie maj7 ---
G=43; D=38; E=40; C=48; A=45
CH = {
 'Gmaj7':(43,[59,62,66]),   # G  B D F#
 'Dmaj7':(38,[57,61,66]),   # D  A C# F#
 'Em7'  :(40,[55,59,62]),   # E  G B D
 'Cmaj7':(48,[52,55,59]),   # C  E G B
 'Am7'  :(45,[60,64,67]),   # A  C E G
 'D7'   :(38,[54,57,60]),   # D  F# A C
}
prog = ['Gmaj7','Dmaj7','Em7','Cmaj7','Gmaj7','Dmaj7','Am7','D7']

# --- Melodia esparsa (midi por compasso; None = descanso), entra no bar 3 ---
melody = [None,None,
 71,69,67,66, 64,66,None,74,        # b3-10
 73,71,69,67, 66,64,None,62,        # b11-18
 66,64,62,61, 62,66,None,None,      # b19-26
 None,None]                          # cauda

for b in range(N_BARS):
    t0 = b*bar
    name = prog[b % len(prog)]
    bass, chord = CH[name]
    # beat1: baixo (ring longo)
    add(out, piano(bass, bar*1.05, amp=0.5, tau=2.6), t0)
    # beat2 e beat3: acorde suave (oom-pah-pah)
    for bi,beatpos in enumerate([1,2]):
        for j,ntn in enumerate(chord):
            add(out, piano(ntn, beat*1.6, amp=0.16, tau=1.5), t0+beatpos*beat)
    # melodia
    if b < len(melody) and melody[b] is not None:
        add(out, piano(melody[b], bar*1.15, amp=0.34, tau=2.2), t0+0.02)
        # eco harmonico uma oitava (bem baixo) p/ brilho
        add(out, piano(melody[b]+12, bar*0.5, amp=0.05, tau=1.2), t0+0.02)

# normaliza
out /= np.max(np.abs(out))+1e-9

# reverb (sala pequena, suave)
def reverb(x):
    d=[0.021,0.037,0.053,0.079,0.107,0.141]; g=[0.5,0.4,0.32,0.24,0.17,0.11]
    y=x.copy()
    for dd,gg in zip(d,g):
        di=int(dd*SR); y+=gg*np.concatenate([np.zeros(di),x])[:len(x)]
    return y
wet=reverb(out)
mix=0.7*out+0.4*wet

# filtros: passa-baixa quente + tira sub-grave
mix=sosfilt(butter(4,4200/(SR/2),btype='low',output='sos'),mix)
mix=sosfilt(butter(2,55/(SR/2),btype='high',output='sos'),mix)

# fades e nivel discreto
fi=int(3.0*SR); fo=int(4.0*SR)
mix[:fi]*=np.linspace(0,1,fi); mix[-fo:]*=np.linspace(1,0,fo)
mix/=np.max(np.abs(mix))+1e-9
mix*=10**(-4.0/20)   # pico ~ -4 dB

# estereo com leve largura
right=np.concatenate([np.zeros(int(0.012*SR)),mix])[:len(mix)]
st=np.stack([mix,right],axis=1)
st=(st*32767).astype(np.int16)
wavfile.write("trilha_classica.wav",SR,st)
print("trilha_classica.wav:", st.shape[0]/SR,"s")
