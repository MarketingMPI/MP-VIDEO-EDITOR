#!/usr/bin/env python
"""Gera o sticker de headline estilo texto do Instagram Stories.
Caixinhas brancas/pretas/verdes arredondadas POR LINHA, fonte Segoe UI Bold.

Uso:
  python make_sticker.py OUT.png "cor" "Linha 1" "Linha 2" ["Linha 3" ...]
  cor: white | black | green
"""
import sys
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    "white": ((255, 255, 255, 255), (15, 15, 15, 255)),
    "black": ((24, 24, 24, 255), (255, 255, 255, 255)),
    "green": ((0, 80, 60, 255), (255, 255, 255, 255)),  # #00503c MP
}

def main():
    out = sys.argv[1]
    cor = sys.argv[2]
    lines = sys.argv[3:]
    BG, FG = COLORS[cor]
    font_path = "C:/Windows/Fonts/segoeuib.ttf"
    FS = 44; SS = 3; fs = FS * SS
    f = ImageFont.truetype(font_path, fs)
    pad_x = 22 * SS; pad_y = 8 * SS; gap = 6 * SS; radius = 16 * SS
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    dims = []
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=f)
        dims.append((bb[2] - bb[0], bb[3] - bb[1], bb))
    maxw = max(w for w, _, _ in dims)
    totalH = sum(h + pad_y * 2 for _, h, _ in dims) + gap * (len(lines) - 1)
    img = Image.new("RGBA", (maxw + pad_x * 2 + 8 * SS, totalH + 8 * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img); y = 4 * SS
    for (w, h, bb), ln in zip(dims, lines):
        bw = w + pad_x * 2; x0 = (img.width - bw) // 2
        y0 = y; x1 = x0 + bw; y1 = y0 + h + pad_y * 2
        dr.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=BG)
        dr.text((x0 + pad_x - bb[0], y0 + pad_y - bb[1]), ln, font=f, fill=FG)
        y = y1 + gap
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
    img.save(out)
    print("saved", out, img.size)

if __name__ == "__main__":
    main()
