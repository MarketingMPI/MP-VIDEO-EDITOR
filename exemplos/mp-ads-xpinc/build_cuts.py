#!/usr/bin/env python
"""Gera KEEP (video) e mesma expr pra audio a partir dos silencios."""

pad = 0.12

jobs = {
    "ADS04_VS01": {
        "dur": 51.101667,
        "sil": [
            (0, 0.388063),
            (3.362437, 3.7515),
            (6.082187, 6.715),
            (8.201625, 8.556563),
            (10.08525, 10.523125),
            (13.925125, 14.67375),
            (18.449562, 18.953063),
            (20.6815, 21.056188),
            (22.76575, 23.143062),
            (25.947312, 26.6375),
            (32.424312, 33.201125),
            (43.10025, 43.46425),
            (50.259875, 51.0375),
        ],
    },
    "ADS05_VS01": {
        "dur": 41.635,
        "sil": [
            (8.5505, 9.310562),
            (11.795438, 12.190688),
            (13.307063, 13.744063),
            (16.53025, 16.982125),
            (21.341313, 21.983375),
            (25.423938, 25.932625),
            (30.300187, 31.07225),
            (35.717125, 36.274938),
            (38.246625, 38.6015),
            (40.741188, 41.586937),
        ],
    },
}

for name, j in jobs.items():
    dur = j["dur"]
    rems = []
    for i, (s, e) in enumerate(j["sil"]):
        if i == 0 and s == 0:            # abertura: aparar do zero
            a, b = 0.0, e - pad
        elif e >= dur - 0.15:            # silencio de fim: aparar ate o final
            a, b = s + pad, dur
        else:
            a, b = s + pad, e - pad
        if b - a > 0.05:
            rems.append((round(a, 3), round(b, 3)))
    tot = sum(b - a for a, b in rems)
    expr = "+".join(f"between(t\\,{a}\\,{b})" for a, b in rems)
    keep = "not(" + expr + ")"
    print(f"### {name}: cortes={len(rems)} cortado={round(tot,2)}s final~{round(dur-tot,2)}s")
    print(keep)
    print()
