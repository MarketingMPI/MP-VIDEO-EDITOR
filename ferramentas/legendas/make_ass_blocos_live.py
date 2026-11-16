#!/usr/bin/env python
"""Constroi ASS de legendas (branco uniforme Campton, blocos 2-3 palavras)
para o Corte A. PlayRes 1080x1920. Legenda no terco inferior, acima da area
do rosto/nametag."""
import re

SRT = "C:/Users/phenr/mp-live-maisretorno/out/A.srt"
OUT = "C:/Users/phenr/mp-live-maisretorno/out/A.ass"

def parse_srt(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    # arquivo lido pelo tool tem prefixo "N|" nas linhas; normalizar
    raw = re.sub(r"^\d+\|", "", raw, flags=re.M)
    blocks = re.split(r"\n\s*\n", raw.strip())
    cues = []
    for b in blocks:
        lines = [l for l in b.splitlines() if l.strip() != ""]
        if len(lines) < 2:
            continue
        tc = None
        for i, l in enumerate(lines):
            if "-->" in l:
                tc = l
                txt = " ".join(lines[i+1:]).strip()
                break
        if not tc:
            continue
        a, b2 = tc.split("-->")
        cues.append((a.strip(), b2.strip(), txt))
    return cues

def to_cs(ts):
    ts = ts.replace(".", ",")
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    total = int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
    return total

def ass_ts(t):
    cs = int(round(t*100))
    h = cs // 360000
    cs %= 360000
    m = cs // 6000
    cs %= 6000
    s = cs // 100
    cs %= 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

# correcoes de homofonos / dominio
FIX = {
}

cues = parse_srt(SRT)

# quebrar cada cue em blocos de ate 3 palavras, distribuindo o tempo
def split_words(txt):
    return txt.split()

header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,Campton,72,&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,-1,0,0,0,100,100,0,0,1,4.2,2.4,2,90,90,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines_out = []
for a, b, txt in cues:
    for k, v in FIX.items():
        txt = txt.replace(k, v)
    txt = txt.strip()
    if not txt or txt == "Isso.":
        continue
    words = split_words(txt)
    t0 = to_cs(a); t1 = to_cs(b)
    dur = max(t1 - t0, 0.4)
    # agrupar em blocos de 3
    groups = [words[i:i+3] for i in range(0, len(words), 3)]
    n = len(groups)
    seg = dur / n
    for gi, g in enumerate(groups):
        gs = t0 + gi*seg
        ge = t0 + (gi+1)*seg
        text = " ".join(g)
        text = text.replace(",", "").replace(".", "")  # legendas dinamicas sem pontuacao pesada
        text = "{\\fad(80,80)}" + text.upper()
        lines_out.append(f"Dialogue: 0,{ass_ts(gs)},{ass_ts(ge)},Legenda,,0,0,0,,{text}")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(header + "\n".join(lines_out) + "\n")
print("ASS escrito:", OUT, "-", len(lines_out), "blocos")
