#!/usr/bin/env python3
# Gera as KEEP expressions para corte de respiros (COPY 01 - Polo Capital)
# Timeline do asr.wav (0-based na fala). Video real = asr + DELTA.
DELTA = 0.756  # audio start_time no container
LEADIN_TRIM = DELTA - 0.05  # remove lead-in mudo do video, com 0.05s de folga
PAD = 0.12   # folga em cada lado da pausa removida
MINCUT = 0.05

# pausas detectadas no asr.wav (start, end)
pauses = [
    (2.012542, 2.366667),
    (4.694271, 5.269083),
    (13.081917, 13.948313),   # duas adjacentes fundidas
    (19.624937, 20.029042),
    (23.237604, 23.633708),
    (26.078646, 26.670833),
    (27.45, 27.822937),
    (32.752146, 33.160167),
    (35.649125, 36.40075),
    (42.286854, 42.850812),
    (46.041083, 46.771313),
    (53.265187, 53.961667),
    (55.426187, 55.79975),
    (59.122667, 59.501812),
    (60.733917, 61.445375),
    (70.448188, 71.019667),
    (74.001396, 74.401229),
    (79.9695, 80.666125),      # trailing silence final
]

def middle(a, b):
    a2 = a + PAD
    b2 = b - PAD
    if b2 - a2 < MINCUT:
        return None
    return (a2, b2)

cuts_a = []
for a, b in pauses:
    m = middle(a, b)
    if m:
        cuts_a.append(m)

# Expr de audio (timeline asr)
terms_a = "+".join(f"between(t\\,{a:.4f}\\,{b:.4f})" for a, b in cuts_a)
KEEP_A = f"not({terms_a})"

# Expr de video (timeline video real = asr + DELTA); remove lead-in tambem
terms_v = "+".join(f"between(t\\,{a+DELTA:.4f}\\,{b+DELTA:.4f})" for a, b in cuts_a)
KEEP_V = f"gte(t\\,{LEADIN_TRIM:.4f})*not({terms_v})"

removed = sum(b - a for a, b in cuts_a) + LEADIN_TRIM
print("NUM_CUTS:", len(cuts_a))
print("REMOVED_SECONDS:", round(removed, 3))
print("KEEP_A=" + KEEP_A)
print("KEEP_V=" + KEEP_V)

with open("keep_a.txt", "w") as f:
    f.write(KEEP_A)
with open("keep_v.txt", "w") as f:
    f.write(KEEP_V)
