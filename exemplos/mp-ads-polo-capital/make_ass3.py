#!/usr/bin/env python3
import re

FIXES = [
    ("MPPROC", "MP PRO"),
    ("MPProc", "MP PRO"),
    ("MP Proc", "MP PRO"),
    ("ler a classe de verdade", "ler a crise de verdade"),
]

def parse_srt(path):
    blocks = []
    raw = open(path, encoding="utf-8").read()
    raw = re.sub(r'(?m)^\d+\|', '', raw)
    for chunk in re.split(r'\n\s*\n', raw.strip()):
        lines = [l for l in chunk.splitlines() if l.strip()]
        if len(lines) < 2: continue
        tl_idx = next((i for i,l in enumerate(lines) if '-->' in l), None)
        if tl_idx is None: continue
        tl = lines[tl_idx]
        text = " ".join(lines[tl_idx+1:]).strip()
        m = re.search(r'(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)', tl)
        if not m: continue
        g = list(map(int, m.groups()))
        st = g[0]*3600+g[1]*60+g[2]+g[3]/1000
        en = g[4]*3600+g[5]*60+g[6]+g[7]/1000
        blocks.append((st, en, text))
    return blocks

def apply_fixes(t):
    for a,b in FIXES: t = t.replace(a,b)
    return t

def sec_to_ass(s):
    h=int(s//3600); s-=h*3600
    m=int(s//60); s-=m*60
    return f"{h:d}:{m:02d}:{s:05.2f}"

blocks = parse_srt("cut3.srt")
events=[]
for st,en,text in blocks:
    text = apply_fixes(text)
    words = text.split()
    if not words: continue
    groups=[]; i=0
    while i < len(words):
        n = 3 if (len(words)-i)!=4 else 2
        n = min(n, len(words)-i)
        groups.append(" ".join(words[i:i+n])); i+=n
    dur=en-st; total_chars=sum(len(g) for g in groups); t=st
    for g in groups:
        share = dur*(len(g)/total_chars)
        events.append((t,t+share,g.upper())); t+=share

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

with open("subs3.ass","w",encoding="utf-8") as f:
    f.write(HEADER)
    for gs,ge,txt in events:
        txt = txt.replace("—",",")
        f.write(f"Dialogue: 0,{sec_to_ass(gs)},{sec_to_ass(ge)},Sub,,0,0,0,,{{\\fad(90,90)}}{txt}\n")
print("events:", len(events), "last end:", round(events[-1][1],2))
