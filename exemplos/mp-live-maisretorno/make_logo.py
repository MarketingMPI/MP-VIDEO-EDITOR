from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image

SRC = "C:/Users/phenr/OneDrive/Imagens/Logos MP/Logo MP PRO SVG.svg"
OUT = "C:/Users/phenr/mp-live-maisretorno/out/logo_mppro.png"

drawing = svg2rlg(SRC)
# escala 6x para alta resolucao (554x115 -> 3324x690)
SCALE = 6
drawing.width *= SCALE
drawing.height *= SCALE
drawing.scale(SCALE, SCALE)
renderPM.drawToFile(drawing, OUT, fmt="PNG", bg=0xFFFFFF, configPND=None)
# svglib nao respeita transparencia via renderPM; abrir e tornar branco transparente
img = Image.open(OUT).convert("RGBA")
px = img.getdata()
new = []
for r, g, b, a in px:
    # branco puro (fundo) -> transparente
    if r > 245 and g > 245 and b > 245:
        new.append((r, g, b, 0))
    else:
        new.append((r, g, b, a))
img.putdata(new)
# crop bounding box
bbox = img.getbbox()
img = img.crop(bbox)
img.save(OUT)
print("saved", OUT, img.size)
