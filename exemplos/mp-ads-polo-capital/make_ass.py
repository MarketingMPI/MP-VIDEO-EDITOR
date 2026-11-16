#!/usr/bin/env python3
# Constroi o ASS a partir do cut.srt, corrige nomes/homofonos, reflow 2-3 palavras.
import re

# Correcoes por texto (aplicadas linha a linha do SRT do cut)
FIXES = [
    ("recuperação.", "recuperação judicial."),
    ("Marabás", "Marabraz"),
    ("Toxok", "Tok&Stok"),
    ("só pra lembrar isso aqui", "só pra lembrar algumas aqui"),
    ("manchete final", "manchete de jornal"),
    ("preparado, ganha.", "preparado, ganha o cliente."),
    ("esse balado", "esse barulho todo"),
    ("as oportunidades.", "as oportunidades disfarçadas."),
    ("gestor da Pital", "gestor da Polo Capital"),
    ("garantir a carga", "garantir a sua vaga"),
]

def parse_srt(path):
    blocks = []
    raw = open(path, encoding="utf-8").read()
    # remove line-number prefixes "N|"
    raw = re.sub(r'(?m)^\d+\|', '', raw)
    for chunk in re.split(r'\n\s*\n', raw.strip()):
        lines = [l for l in chunk.splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        # find the timestamp line
        tl_idx = next((i for i,l in enumerate(lines) if '-->' in l), None)
        if tl_idx is None:
            continue
        tl = lines[tl_idx]
        text = " ".join(lines[tl_idx+1:]).strip()
        m = re.search(r'(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)', tl)
        if not m:
            continue
        g = list(map(int, m.groups()))
        st = g[0]*3600+g[1]*60+g[2]+g[3]/1000
        en = g[4]*3600+g[5]*60+g[6]+g[7]/1000
        blocks.append((st, en, text))
    return blocks

def apply_fixes(t):
    for a,b in FIXES:
        t = t.replace(a,b)
    return t

def sec_to_ass(s):
    h=int(s//3600); s-=h*3600
    m=int(s//60); s-=m*60
    return f"{h:d}:{m:02d}:{s:05.2f}"

blocks = parse_srt("cut.srt")
# reflow into 2-3 word chunks, proportional timing
events=[]
for st,en,text in blocks:
    text = apply_fixes(text)
    words = text.split()
    if not words: continue
    # group 2-3 words
    groups=[]
    i=0
    while i < len(words):
        n = 3 if (len(words)-i)!=4 else 2  # avoid leaving a lone word
        n = min(n, len(words)-i)
        groups.append(" ".join(words[i:i+n]))
        i+=n
    dur=en-st
    total_chars=sum(len(g) for g in groups)
    t=st
    for g in groups:
        share = dur*(len(g)/total_chars)
        gs=t; ge=t+share
        events.append((gs,ge,g.upper()))
        t=ge

# ensure no overlap / tiny gaps
HEADER = r"""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub, Campton-Bold, 44, &H00FFFFFF, &H00FFFFFF, &H00202020, &H80000000, 0, 0, 0, 0, 100, 100, 0, 0, 1, 2.6, 1.6, 2, 60, 60, 150, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

with open("subs.ass","w",encoding="utf-8") as f:
    f.write(HEADER)
    for gs,ge,txt in events:
        txt = txt.replace("—",",")
        f.write(f"Dialogue: 0,{sec_to_ass(gs)},{sec_to_ass(ge)},Sub,,0,0,0,,{{\\fad(90,90)}}{txt}\n")

print("events:", len(events))
print("last end:", round(events[-1][1],2))
