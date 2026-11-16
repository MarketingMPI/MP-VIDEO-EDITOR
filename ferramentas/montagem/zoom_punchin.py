# -*- coding: utf-8 -*-
# Reframe em duas fases com transicao suave (smoothstep) no tempo T (segundos do novo clipe).
# Fase 1 (pergunta): fechado, esconde entrevistador -> z1=1.42, cx1=0.425, cy1=0.46
# Fase 2 (depoimento): normal + punch-ins -> z2 base=1.13, cx2=0.53, cy2=0.50
# Transicao entre t0=5.9 e t1=7.6s
#
# Punch-ins (T em segundos do novo clipe; depoimento comeca ~6.3s, entao +6.3 nos tempos antigos):
#   antigo 10 -> 16.3   "futuro de cada pessoa"
#   antigo 30 -> 36.3   "ferramental / felicidade"
#   antigo 41 -> 47.3   "Family Office"
#   antigo 61 -> 67.3   climax "nacao"
T = "on/60"
t0, t1 = 5.9, 7.6

# smoothstep s in [0,1]
s = f"clip(({T}-{t0})/({t1-t0}),0,1)"
ss = f"({s}*{s}*(3-2*{s}))"   # smoothstep

# fase2 zoom base + gaussianas de punch-in
bumps = [(16.3,0.15,3.0),(36.3,0.12,3.2),(47.3,0.19,2.8),(67.3,0.22,3.2)]
punch = "+".join(f"{a}*exp(-pow(({T}-{c})/{w}\\,2))" for c,a,w in bumps)
z2 = f"(1.13+{punch})"
z1 = "1.42"
Z = f"({z1}+({z2}-{z1})*{ss})"

cx = f"(0.425+(0.53-0.425)*{ss})"
cy = f"(0.46+(0.50-0.46)*{ss})"
X = f"iw*{cx}-(iw/zoom/2)"
Y = f"ih*{cy}-(ih/zoom/2)"

# imprime tudo em uma linha, escapando para shell
print("Z=\"" + Z + "\"")
print("X=\"" + X + "\"")
print("Y=\"" + Y + "\"")
