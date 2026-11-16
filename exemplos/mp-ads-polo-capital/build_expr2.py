#!/usr/bin/env python3
DELTA = 0.114
LEADIN_TRIM = DELTA - 0.05
PAD = 0.12
MINCUT = 0.05

pauses = [
    (4.10275, 4.564354),
    (8.628583, 9.086313),
    (11.672646, 12.165083),
    (14.331625, 14.996229),
    (18.198458, 18.621688),
    (19.359562, 19.807104),
    (21.606083, 22.351167),
    (25.867896, 26.259229),
    (29.942896, 30.298646),
    (39.981917, 40.56975),
    (51.600625, 51.974458),
    (54.133333, 54.491),
    (59.293875, 60.079313),  # trailing
]

def middle(a, b):
    a2 = a + PAD; b2 = b - PAD
    if b2 - a2 < MINCUT: return None
    return (a2, b2)

cuts = [m for a,b in pauses if (m:=middle(a,b))]
terms_a = "+".join(f"between(t\\,{a:.4f}\\,{b:.4f})" for a,b in cuts)
KEEP_A = f"not({terms_a})"
terms_v = "+".join(f"between(t\\,{a+DELTA:.4f}\\,{b+DELTA:.4f})" for a,b in cuts)
KEEP_V = f"gte(t\\,{LEADIN_TRIM:.4f})*not({terms_v})"
removed = sum(b-a for a,b in cuts) + LEADIN_TRIM
print("NUM_CUTS:", len(cuts), "REMOVED:", round(removed,3))
open("keep_a2.txt","w").write(KEEP_A)
open("keep_v2.txt","w").write(KEEP_V)
