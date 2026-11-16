# -*- coding: utf-8 -*-
import re, sys

SRT = sys.argv[1] if len(sys.argv) > 1 else "legendas.srt"
OUT = sys.argv[2] if len(sys.argv) > 2 else "legendas.ass"

def to_ass_time(srt_time):
    h, m, rest = srt_time.split(":")
    s, ms = rest.split(",")
    cs = int(ms) // 10
    return f"{int(h)}:{int(m):02d}:{int(s):02d}.{cs:02d}"

with open(SRT, encoding="utf-8") as f:
    content = f.read().strip()

blocks = re.split(r"\n\s*\n", content)

KEY = ["futuro", "Family Office", "nação", "ferramental", "família", "Estado"]
GREEN = r"{\c&H0011A600&}"
WHITE = r"{\c&H00FFFFFF&}"

def highlight(text):
    out = text
    for kw in KEY:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        out = pattern.sub(lambda m: GREEN + m.group(0) + WHITE, out)
    return out

lines = []
for b in blocks:
    parts = b.split("\n")
    if len(parts) < 3:
        continue
    start_s, end_s = [x.strip() for x in parts[1].split("-->")]
    raw = " ".join(p.strip() for p in parts[2:])
    is_question = raw.rstrip().endswith("?")
    text = "\\N".join(p.strip() for p in parts[2:])
    text = highlight(text)
    eff = r"{\fad(140,140)}"
    if is_question:
        # pergunta do entrevistador: italico, leve prefixo
        text = r"{\i1}" + text + r"{\i0}"
    lines.append(f"Dialogue: 0,{to_ass_time(start_s)},{to_ass_time(end_s)},MP,,0,0,0,,{eff}{text}")

with open("ass_header.txt", encoding="utf-8") as f:
    header = f.read()

with open(OUT, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("\n".join(lines) + "\n")

print(f"{OUT} gerado com {len(lines)} legendas")
