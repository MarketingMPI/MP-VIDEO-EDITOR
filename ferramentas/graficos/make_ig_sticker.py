#!/usr/bin/env python
"""Build an Instagram-Stories-style headline sticker PNG.

White rounded boxes (one per line) + black text, Segoe UI Bold as an
Instagram-Sans stand-in. Transparent canvas so it overlays onto a vertical clip
and reads like an organic Stories text sticker (not an ad banner).

Usage: edit LINES, run, then composite onto a REAL hflip frame and check the
y-position with vision before rendering. See references/talking-head-ad-clips.md.
"""
from PIL import Image, ImageDraw, ImageFont

# One entry per visual line. Keep 2-4 lines; break where it reads naturally.
LINES = ["A maioria dos consultores", "perde cliente logo na", "primeira reunião"]
OUT = "C:/Users/phenr/mp-ads-maisretorno/sticker.png"

# Box + text color. ALTERNATE between versions so a batch isn't all identical:
#   white box/black text (default) -> dark box/white text -> MP green/white text.
BG = (255, 255, 255, 255)   # box fill.  dark=#181818 -> (24,24,24,255); green=#00503c -> (0,80,60,255)
FG = (15, 15, 15, 255)      # text color. use (255,255,255,255) on the dark/green boxes

FONT_PATH = "C:/Windows/Fonts/segoeuib.ttf"   # Segoe UI Bold ~ Instagram Sans
FS = 46            # base font size (px, pre-supersample)
SS = 3             # supersample factor for smooth rounded corners
PAD_X = 22 * SS    # horizontal padding inside each box
PAD_Y = 8 * SS     # vertical padding inside each box
GAP = 6 * SS       # vertical gap between stacked boxes
RADIUS = 16 * SS   # corner radius

f = ImageFont.truetype(FONT_PATH, FS * SS)
tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
dims = []
for ln in LINES:
    bb = tmp.textbbox((0, 0), ln, font=f)
    dims.append((bb[2] - bb[0], bb[3] - bb[1], bb))
maxw = max(w for w, _, _ in dims)
totalH = sum(h + PAD_Y * 2 for _, h, _ in dims) + GAP * (len(LINES) - 1)

img = Image.new("RGBA", (maxw + PAD_X * 2 + 8 * SS, totalH + 8 * SS), (0, 0, 0, 0))
dr = ImageDraw.Draw(img)
y = 4 * SS
for (w, h, bb), ln in zip(dims, LINES):
    bw = w + PAD_X * 2
    x0 = (img.width - bw) // 2
    y0, x1, y1 = y, x0 + bw, y + h + PAD_Y * 2
    dr.rounded_rectangle([x0, y0, x1, y1], radius=RADIUS, fill=BG)
    dr.text((x0 + PAD_X - bb[0], y0 + PAD_Y - bb[1]), ln, font=f, fill=FG)
    y = y1 + GAP

img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
img.save(OUT)
print("saved", OUT, img.size)
