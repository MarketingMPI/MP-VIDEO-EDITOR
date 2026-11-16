# -*- coding: utf-8 -*-
"""Vinheta de encerramento MP PRO (1080x1920) — padrao reutilizavel dos cortes
da live Mais Retorno / MP PRO. Gera a IMAGEM da vinheta; o video (com fade e
cauda de piano) e a transicao xfade sao montados no ffmpeg (ver SKILL.md).

Fechado com o user (revisado apos feedback):
- fundo em DEGRADE radial de preto (centro #262626 -> bordas #0a0a0a)
- logo MP PRO dourada no centro-superior
- linha divisoria dourada fina
- botao DOURADO (#E4D6A7) com texto ESCURO (#181818), CTA "Faça sua inscrição agora"
- subtitulo cinza "Formação + comunidade para consultores"
- Campton em tudo, 2x supersample

Pre-requisitos:
- out/logo_mppro.png  (logo MP PRO dourada com transparencia; gerar via sharp,
  ver pitfall "SVG -> PNG no Windows" no SKILL.md)
- assets/CamptonSemiBold.otf, assets/CamptonMedium.otf
Ajuste OUT/LOGO/paths conforme o workdir da sessao.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SS = 2  # supersample
GOLD = (228, 214, 167, 255)  # #E4D6A7
DARK = (24, 24, 24, 255)     # texto escuro sobre o botao dourado
GREY = (176, 176, 176, 255)  # subtitulo

OUT = "out/vinheta.png"
LOGO = "out/logo_mppro.png"
F_SEMI = "assets/CamptonSemiBold.otf"
F_MED = "assets/CamptonMedium.otf"

CTA = "Faça sua inscrição agora"
SUB = "Formação + comunidade para consultores"

# --- Fundo degrade radial de preto (centro mais claro -> bordas escuras) ---
cx, cy = W*SS/2, H*SS*0.42
maxd = math.hypot(W*SS, H*SS) * 0.62
c_in, c_out = (38, 38, 38), (10, 10, 10)
img = Image.new("RGBA", (W*SS, H*SS))
px = img.load()
for y in range(H*SS):
    for x in range(W*SS):
        d = min(math.hypot(x-cx, y-cy)/maxd, 1.0)
        px[x, y] = (
            int(c_in[0] + (c_out[0]-c_in[0])*d),
            int(c_in[1] + (c_out[1]-c_in[1])*d),
            int(c_in[2] + (c_out[2]-c_in[2])*d),
            255,
        )
dr = ImageDraw.Draw(img)

# --- Logo MP PRO dourada, centro-superior ---
logo = Image.open(LOGO).convert("RGBA")
logo_w = 660*SS
logo_h = int(logo.height * (logo_w/logo.width))
logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
logo_y = int(H*SS*0.36)
img.paste(logo, ((W*SS - logo_w)//2, logo_y), logo)

# --- linha divisoria dourada fina ---
line_y = logo_y + logo_h + 70*SS
lx = W*SS//2
dr.line([(lx-70*SS, line_y), (lx+70*SS, line_y)], fill=(228, 214, 167, 150), width=3*SS)

# --- CTA: botao dourado arredondado, texto escuro ---
f_cta = ImageFont.truetype(F_SEMI, 54*SS)
bb = dr.textbbox((0, 0), CTA, font=f_cta)
tw, th = bb[2]-bb[0], bb[3]-bb[1]
pad_x, pad_y = 62*SS, 40*SS
bw, bh = tw + pad_x*2, th + pad_y*2
bx0 = (W*SS - bw)//2
by0 = line_y + 90*SS
dr.rounded_rectangle([bx0, by0, bx0+bw, by0+bh], radius=bh//2, fill=GOLD)
dr.text((bx0 + pad_x - bb[0], by0 + pad_y - bb[1]), CTA, font=f_cta, fill=DARK)

# --- subtitulo ---
f_sub = ImageFont.truetype(F_MED, 38*SS)
sbb = dr.textbbox((0, 0), SUB, font=f_sub)
sw = sbb[2]-sbb[0]
sy = by0 + bh + 54*SS
dr.text(((W*SS - sw)//2 - sbb[0], sy), SUB, font=f_sub, fill=GREY)

img = img.resize((W, H), Image.LANCZOS)
img.convert("RGB").save(OUT)
print("saved", OUT, img.size)
