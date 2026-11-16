import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 115.0          # segundos, folga para cobrir o vídeo trimado
BPM = 62
beat = 60.0 / BPM
bar = beat * 4       # compasso 4/4

def note(freq):
    # frequência da nota (A4=440) por semitons a partir de A4
    return 440.0 * (2 ** (freq / 12.0))

# Graus (semitons rel. A4)
D3  = note(-19); F3s = note(-16); A3 = note(-12); C4s = note(-9)
D4  = note(-7);  E4  = note(-5);  F4s= note(-4);  G3 = note(-14)
B3  = note(-10); A2  = note(-24); B2 = note(-22); G2 = note(-26)
Cn5 = note(3)

# Progressao: Dmaj7 | Bm7 | Gmaj7 | A7sus4  (2 compassos cada = 8 beats)
progression = [
    (D3,  [D4, F4s, note(4), note(6)]),   # Dmaj7  (D F# A C#)
    (B2,  [B3, D4, F4s, note(2)]),        # Bm7    (B D F# A)
    (G2,  [note(-2), B3, D4, F4s]),       # Gmaj7  (G B D F#)
    (A2,  [note(0), C4s, E4, note(5)]),   # A7sus->A (A C# E G)  suave
]
chord_len = bar * 2  # cada acorde dura 2 compassos

t_total = int(DUR * SR)
out = np.zeros(t_total, dtype=np.float64)

def adsr(n, a, d, s_level, r):
    env = np.ones(n)
    ai = int(a*SR); di = int(d*SR); ri = int(r*SR)
    if ai>0: env[:ai] = np.linspace(0,1,ai)
    if di>0: env[ai:ai+di] = np.linspace(1,s_level,di)
    env[ai+di:n-ri] = s_level
    if ri>0: env[n-ri:] = np.linspace(s_level,0,ri)
    return env

def voice(freq, n, detune=0.0):
    tt = np.arange(n)/SR
    f = freq*(2**(detune/1200.0))
    # timbre suave: fundamental + harmonicos fracos + leve vibrato
    vib = 1 + 0.0025*np.sin(2*np.pi*4.8*tt)
    sig  = np.sin(2*np.pi*f*tt*vib)
    sig += 0.28*np.sin(2*np.pi*2*f*tt)
    sig += 0.12*np.sin(2*np.pi*3*f*tt)
    return sig

pos = 0.0
idx = 0
while pos < DUR:
    root, chord = progression[idx % len(progression)]
    seg_len = min(chord_len, DUR - pos)
    n = int(seg_len * SR)
    start = int(pos * SR)
    env = adsr(n, a=0.9, d=0.6, s_level=0.8, r=1.1)
    seg = np.zeros(n)
    # baixo grave (root uma oitava abaixo)
    seg += 0.5*voice(root, n)*adsr(n, 1.0, 0.4, 0.75, 1.2)
    # acorde: notas com leve detune para largura
    for k, f in enumerate(chord):
        seg += 0.22*voice(f, n, detune=(-6 if k%2 else 6))
    seg *= env
    # pequena "estrela" de piano-ish no topo a cada acorde (bem suave)
    lead = chord[-1]*2
    ln = int(min(seg_len, 2.2)*SR)
    seg[:ln] += 0.10*voice(lead, ln)*adsr(ln, 0.05, 0.5, 0.3, 1.4)
    out[start:start+n] += seg[:t_total-start]
    pos += chord_len
    idx += 1

# Normaliza pre-efeitos
out /= np.max(np.abs(out)) + 1e-9

# Reverb simples (varios ecos curtos decrescentes) -> sensacao de sala
def reverb(x, sr):
    delays = [0.017, 0.031, 0.047, 0.071, 0.099, 0.131]
    gains  = [0.55, 0.42, 0.33, 0.25, 0.18, 0.12]
    y = x.copy()
    for d, g in zip(delays, gains):
        di = int(d*sr)
        pad = np.zeros(di)
        y += g*np.concatenate([pad, x])[:len(x)]
    return y

wet = reverb(out, SR)
mix = 0.75*out + 0.35*wet

# Passa-baixa (deixa quente/ao fundo) + passa-alta (tira lama grave)
sos_lp = butter(4, 3200/(SR/2), btype='low', output='sos')
sos_hp = butter(2, 70/(SR/2), btype='high', output='sos')
mix = sosfilt(sos_lp, mix)
mix = sosfilt(sos_hp, mix)

# Fades suaves de entrada e saida
fi = int(2.5*SR); fo = int(4.0*SR)
mix[:fi] *= np.linspace(0,1,fi)
mix[-fo:] *= np.linspace(1,0,fo)

# Normaliza final para -18 dBFS pico (trilha discreta)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 10**(-3.0/20)   # pico ~ -3 dB no arquivo; volume real ajustado no mix do video

# Estereo com leve largura
left  = mix
right = np.concatenate([np.zeros(int(0.011*SR)), mix])[:len(mix)]
stereo = np.stack([left, right], axis=1)
stereo = (stereo * 32767).astype(np.int16)

wavfile.write("trilha.wav", SR, stereo)
print("trilha.wav gerada:", stereo.shape[0]/SR, "s")
