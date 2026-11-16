# -*- coding: utf-8 -*-
# Gera a expressao de zoom (soma de gaussianas) para o zoompan.
# Momentos de enfase (tempo do clipe, base 0 = 35.7s do original):
#   ~10s  "construir o futuro de cada pessoa"
#   ~30s  "esse tipo de ferramental / a felicidade de ter"
#   ~41s  "Family Office"
#   ~61s  "se constroi o futuro de uma nacao" (climax)
bumps = [
    (10.0, 0.16, 3.0),
    (30.0, 0.13, 3.5),
    (41.0, 0.18, 2.8),
    (61.0, 0.22, 3.5),
]
terms = []
for c, a, w in bumps:
    terms.append(f"{a}*exp(-pow((time-{c})/{w}\\,2))")
z_expr = "min(1.0+" + "+".join(terms) + "\\,1.28)"
# centro do enquadramento (fracao da imagem de entrada 2160x3840)
cx, cy = 0.52, 0.45
x_expr = f"iw*{cx}-(iw/zoom/2)"
y_expr = f"ih*{cy}-(ih/zoom/2)"
print("ZEXPR=" + z_expr)
print("XEXPR=" + x_expr)
print("YEXPR=" + y_expr)
