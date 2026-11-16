#!/usr/bin/env python
"""Constroi a expressao KEEP de corte de respiros a partir da saida do silencedetect.

Cola os pares (start,end) de silencio na lista `sil` e roda. Remove o miolo de
cada pausa mantendo `pad` de folga em cada ponta; silencio inicial (start=0) e
aparado desde 0. Imprime a variavel KEEP pronta pra usar no ffmpeg
(select/aselect).

Uso: editar a lista `sil` abaixo (ou passar via stdin) e:
  python build_cut.py  DURACAO_TOTAL
"""
import sys

# Cole aqui os pares do silencedetect (segundos):
sil = [
    # (2.75, 3.18),
    # (5.62, 6.30),
]
pad = 0.12
dur = float(sys.argv[1]) if len(sys.argv) > 1 else None

rems = []
for i, (s, e) in enumerate(sil):
    if i == 0 and s == 0:      # silencio de abertura: aparar do zero
        a, b = 0, e - pad
    else:
        a, b = s + pad, e - pad
    if b - a > 0.05:
        rems.append((round(a, 3), round(b, 3)))

tot = sum(b - a for a, b in rems)
print("cortes:", len(rems), "tempo cortado:", round(tot, 2),
      "final aprox:", round(dur - tot, 2) if dur else "?")
expr = "+".join(f"between(t\\,{a}\\,{b})" for a, b in rems)
print('KEEP="not(' + expr + ')"')
