#!/usr/bin/env python
"""Converte o SRT do video JA CORTADO em legenda ASS estilo Reels (MP).
Campton branca uniforme, blocos de 2-3 palavras, terco inferior, fade sutil.

Uso: python srt_to_ass.py IN.srt OUT.ass
Depois: revisar OUT.ass e corrigir erros do whisper (proper nouns etc.).
Queimar: subtitles=OUT.ass:fontsdir=assets  (assets/ com CamptonBold.otf etc.)
"""
import re, sys

def parse(srt):
    out = []
    for b in re.split(r"\n\s*\n", srt.strip()):
        lines = [l for l in b.splitlines() if l.strip() != ""]
        tl = [l for l in lines if "-->" in l]
        if not tl:
            continue
        t = tl[0]; idx = lines.index(t)
        txt = " ".join(lines[idx + 1:]).strip()
        a, b2 = t.split("-->")
        out.append((a.strip().replace(".", ","), b2.strip().replace(".", ","), txt))
    return out

def to_cs(ts):
    h, m, s = ts.split(":"); s, ms = s.split(",")
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

def to_ass(ms):
    ms = int(ms); cs = ms // 10
    h = cs // 360000; cs %= 360000; m = cs // 6000; cs %= 6000; s = cs // 100; c = cs % 100
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"

HEADER = '''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MP,Campton,44,&H00FFFFFF,&H00FFFFFF,&H00202020,&HA0000000,-1,0,0,0,100,100,0.3,0,1,2.6,1.6,2,60,60,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
# NOTE: PlayResX/Y = 720x1280. Para 1080x1920 dobrar Fontsize (~66) e MarginV (~225).

def main():
    srt = open(sys.argv[1], encoding="utf-8").read()
    items = parse(srt)
    words = []
    for a, b, txt in items:
        ca, cb = to_cs(a), to_cs(b); ws = txt.split()
        if not ws:
            continue
        d = (cb - ca) / len(ws)
        for i, w in enumerate(ws):
            words.append((int(ca + i * d), int(ca + (i + 1) * d), w))
    blocks = []; cur = []
    def flush():
        if cur:
            blocks.append((cur[0][0], cur[-1][1], " ".join(w for _, _, w in cur)))
            cur.clear()
    for st, en, w in words:
        if cur and (len(cur) >= 3 or (en - cur[0][0]) > 1600):
            flush()
        cur.append((st, en, w))
    flush()
    out = [HEADER]
    for st, en, txt in blocks:
        txt = txt.replace("\u2014", ",").upper()
        out.append(f"Dialogue: 0,{to_ass(st)},{to_ass(en)},MP,,0,0,0,,{{\\fad(90,90)}}{txt}")
    open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
    print("blocos:", len(blocks), "->", sys.argv[2])

if __name__ == "__main__":
    main()
