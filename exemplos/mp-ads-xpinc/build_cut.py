silences = [
    (0.000000, 0.753125),
    (4.966625, 5.531313),
    (8.887562, 9.249875),
    (9.706437, 10.551375),
    (12.928313, 13.748563),
    (15.876812, 16.260500),
    (17.426813, 17.876625),
    (19.931812, 20.369688),
    (22.139750, 22.611688),
    (25.548938, 25.915375),
    (29.071813, 29.904063),
    (33.914813, 34.333625),
    (39.350875, 39.821125),
    (43.552813, 44.093688),
    (48.188813, 49.528188),
]
pad = 0.12
duration = 49.642177
removals = []
for i, (start, end) in enumerate(silences):
    if i == 0 and start == 0:
        a, b = 0.0, end - pad
    elif i == len(silences) - 1 and end >= duration - 0.2:
        a, b = start + pad, duration
    else:
        a, b = start + pad, end - pad
    if b - a > 0.05:
        removals.append((round(a, 6), round(b, 6)))
removed = sum(b - a for a, b in removals)
expr = "+".join(f"between(t\\,{a:.6f}\\,{b:.6f})" for a, b in removals)
print(f"CUT_COUNT={len(removals)}")
print(f"REMOVED={removed:.3f}")
print(f"ESTIMATED_DURATION={duration-removed:.3f}")
print(f"KEEP=not({expr})")
