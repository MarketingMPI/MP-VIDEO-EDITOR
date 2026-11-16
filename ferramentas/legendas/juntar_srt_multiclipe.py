# -*- coding: utf-8 -*-
# Constroi SRT combinado (so a fala de Caroline) reposicionando os tempos
# na timeline da montagem final (com crossfades de 0.4s = trechos se sobrepoem levemente).
import re

XF = 0.4  # crossfade
# (arquivo_srt, ss_original, to_original) na ordem da montagem
segs = [
    ("srt_IMG_0241.srt", 28.0, 68.0),
    ("srt_IMG_0242.srt", 7.0, 42.0),
    ("srt_IMG_0244.srt", 13.6, 67.2),
    ("srt_IMG_0243.srt", 0.0, 14.4),
]
# frases a excluir (bastidores / auto-cortes / perguntas que escaparam)
EXCLUDE = [
    "depois voce corta", "depois você corta",
    "o que eu ia falar", "qual foi uma decis", "o que voce considera", "o que você considera",
    "nao precisa falar", "não precisa falar", "melhor eu", "ja meteu", "já meteu", "desliga",
]

def parse(fn):
    with open(fn, encoding="utf-8") as f:
        raw = f.read()
    blocks = re.split(r"\n\s*\n", raw.strip())
    out = []
    for b in blocks:
        lines = [l for l in b.splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        tl = next((l for l in lines if "-->" in l), None)
        if not tl:
            continue
        idx = lines.index(tl)
        txt = " ".join(lines[idx+1:]).strip()
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", tl)
        if not m:
            continue
        a = int(m[1])*3600+int(m[2])*60+int(m[3])+int(m[4])/1000
        z = int(m[5])*3600+int(m[6])*60+int(m[7])+int(m[8])/1000
        out.append([a, z, txt])
    return out

def fmt(t):
    if t < 0: t = 0
    h = int(t//3600); mnt = int((t%3600)//60); s = int(t%60); ms = int(round((t-int(t))*1000))
    return f"{h:02d}:{mnt:02d}:{s:02d},{ms:03d}"

entries = []
timeline = 0.0
for i, (fn, ss, to) in enumerate(segs):
    subs = parse(fn)
    seg_dur = to - ss
    for a, z, txt in subs:
        # só o que está dentro do corte
        if z <= ss or a >= to:
            continue
        low = txt.lower()
        if any(e in low for e in EXCLUDE):
            continue
        na = max(a, ss) - ss + timeline
        nz = min(z, to) - ss + timeline
        if nz - na < 0.3:
            continue
        entries.append([na, nz, txt])
    timeline += seg_dur - XF  # proximo trecho comeca com overlap do crossfade

# escreve SRT
with open("legendas_herdeira.srt", "w", encoding="utf-8") as f:
    for i, (a, z, txt) in enumerate(entries, 1):
        f.write(f"{i}\n{fmt(a)} --> {fmt(z)}\n{txt}\n\n")
print("legendas_herdeira.srt:", len(entries), "linhas; timeline total:", round(timeline+segs[-1][1]-segs[-1][0],2), "s")
