from PIL import Image, ImageFilter

im = Image.open("C:/Users/phenr/OneDrive/Imagens/Logos MP/Frame 290 1.png").convert("RGBA")
# recorta o bounding box do conteudo (remove margens transparentes)
bbox = im.getbbox()
im = im.crop(bbox)
w, h = im.size
print("cropped:", w, h)

# escala para largura alvo ~300px (discreto)
target_w = 300
target_h = int(h * target_w / w)
im = im.resize((target_w, target_h), Image.LANCZOS)
w, h = im.size

pad = 30
canvas = Image.new("RGBA", (w+pad*2, h+pad*2), (0,0,0,0))
alpha = im.split()[3]
sh = Image.new("RGBA", im.size, (0,0,0,0))
black = Image.new("RGBA", im.size, (0,0,0,150))
sh = Image.composite(black, sh, alpha)
shadow = Image.new("RGBA", canvas.size, (0,0,0,0))
shadow.paste(sh, (pad, pad+2), sh)
shadow = shadow.filter(ImageFilter.GaussianBlur(5))
canvas = Image.alpha_composite(canvas, shadow)
canvas.paste(im, (pad, pad), im)
canvas.save("logo_foc.png")
print("logo_foc.png", canvas.size)
