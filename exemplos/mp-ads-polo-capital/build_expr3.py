#!/usr/bin/env python3
DELTA = 0.101
LEADIN_TRIM = 0.30   # remove o silencio inicial 0-0.355 (fala comeca ~0.355)
PAD = 0.12
MINCUT = 0.05

# ignora a primeira (0,0.3556 = lead-in, tratado pelo trim)
pauses = [
    (13.295312, 13.7525),
    (16.775063, 17.211083),
    (20.005542, 20.5885),
    (24.902208, 25.382604),
    (50.047479, 50.51125),
]

def middle(a, b):
    a2 = a + PAD; b2 = b - PAD
    if b2 - a2 < MINCUT: return None
    return (a2, b2)

cuts = [m for a,b in pauses if (m:=middle(a,b))]
terms_a = "+".join(f"between(t\\,{a:.4f}\\,{b:.4f})" for a,b in cuts)
KEEP_A = f"gte(t\\,{LEADIN_TRIM:.4f})*not({terms_a})"
terms_v = "+".join(f"between(t\\,{a+DELTA:.4f}\\,{b+DELTA:.4f})" for a,b in cuts)
KEEP_V = f"gte(t\\,{LEADIN_TRIM+DELTA:.4f})*not({terms_v})"
removed = sum(b-a for a,b in cuts) + LEADIN_TRIM
print("NUM_CUTS:", len(cuts), "REMOVED:", round(removed,3))
open("keep_a3.txt","w").write(KEEP_A)
open("keep_v3.txt","w").write(KEEP_V)
