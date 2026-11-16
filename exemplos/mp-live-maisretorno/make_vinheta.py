# -*- coding: utf-8 -*-
"""Vinheta de encerramento MP PRO (1080x1920). Padrao reutilizavel.
Fundo degrade preto, logo MP PRO dourada, botao dourado, subtitulo."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SS = 2  # supersample
GOLD = (228, 214, 167, 255)  # #E4D6A7
DARK = (24, 24, 24, 255)     # texto escuro sobre o botao dourado
WHITE = (255, 255, 255, 255)
GREY = (176, 176, 176, 255)  # subtitulo

OUT = "C:/Users/phenr/mp-live-maisretorno/out/vinheta.png"
LOGO = "C:/Users/phenr/mp-live-maisretorno/out/logo_mppro.png"
F_SEMI = "assets/CamptonSemiBold.otf"
F_MED = "assets/CamptonMedium.otf"

# --- Fundo degrade preto (radial suave: #262626 no centro -> #0c0c0c nas bordas) ---
import math
cx, cy = W*SS/2, H*SS*0.42
maxd = math.hypot(W*SS, H*SS) * 0.62
bg = Image.new("RGBA", (W*SS, H*SS))
px = bg.load()
c_in = (38, 38, 38)   # centro mais claro
c_out = (10, 10, 10)  # bordas mais escuras
for y in range(H*SS):
    for x in range(W*SS):
        d = min(math.hypot(x-cx, y-cy)/maxd, 1.0)
        r = int(c_in[0] + (c_out[0]-c_in[0])*d)
        g = int(c_in[1] + (c_out[1]-c_in[1])*d)
        b = int(c_in[2] + (c_out[2]-c_in[2])*d)
        px[x, y] = (r, g, b, 255)
img = bg
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
dr.line([(lx-70*SS, line_y), (lx+70*SS, line_y)], fill=(228,214,167,150), width=3*SS)

# --- CTA: botao dourado arredondado, texto escuro ---
cta_txt = "Faça sua inscrição agora"
f_cta = ImageFont.truetype(F_SEMI, 54*SS)
bb = dr.textbbox((0,0), cta_txt, font=f_cta)
tw, th = bb[2]-bb[0], bb[3]-bb[1]
pad_x, pad_y = 62*SS, 40*SS
bw, bh = tw + pad_x*2, th + pad_y*2
bx0 = (W*SS - bw)//2
by0 = line_y + 90*SS
dr.rounded_rectangle([bx0, by0, bx0+bw, by0+bh], radius=bh//2, fill=GOLD)
dr.text((bx0 + pad_x - bb[0], by0 + pad_y - bb[1]), cta_txt, font=f_cta, fill=DARK)

# --- subtitulo ---
sub = "Formação + comunidade para consultores"
f_sub = ImageFont.truetype(F_MED, 38*SS)
sbb = dr.textbbox((0,0), sub, font=f_sub)
sw = sbb[2]-sbb[0]
sy = by0 + bh + 54*SS
dr.text(((W*SS - sw)//2 - sbb[0], sy), sub, font=f_sub, fill=GREY)

img = img.resize((W, H), Image.LANCZOS)
img.convert("RGB").save(OUT)
print("saved", OUT, img.size)
