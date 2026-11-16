from PIL import Image, ImageDraw, ImageFont

LINES = ["Crise no crédito", "privado no Brasil?"]
OUT = "C:/Users/phenr/mp-ads-polo-capital/sticker.png"

# white box + black text (default rotation start for the batch)
BG = (255, 255, 255, 255)
FG = (15, 15, 15, 255)

FONT_PATH = "C:/Windows/Fonts/segoeuib.ttf"
FS = 46
SS = 3
PAD_X = 22 * SS
PAD_Y = 8 * SS
GAP = 6 * SS
RADIUS = 16 * SS

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
