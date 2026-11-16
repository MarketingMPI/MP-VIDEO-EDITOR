from PIL import Image, ImageFilter

im = Image.open('assets/logo_mp.png').convert('RGBA')
w, h = im.size
pad = 40
canvas = Image.new('RGBA', (w+pad*2, h+pad*2), (0,0,0,0))

# sombra: silhueta do alpha, escurecida e borrada
alpha = im.split()[3]
shadow = Image.new('RGBA', canvas.size, (0,0,0,0))
sh_layer = Image.new('RGBA', im.size, (0,0,0,0))
# preenche preto onde ha alpha
black = Image.new('RGBA', im.size, (10,20,15,180))
sh_layer = Image.composite(black, sh_layer, alpha)
shadow.paste(sh_layer, (pad, pad+3), sh_layer)
shadow = shadow.filter(ImageFilter.GaussianBlur(7))

# duas passadas de sombra para reforcar contraste sobre fundo claro
canvas = Image.alpha_composite(canvas, shadow)
canvas = Image.alpha_composite(canvas, shadow)
canvas.paste(im, (pad, pad), im)

canvas.save('assets/logo_mp_shadow.png')
print('logo_mp_shadow.png', canvas.size)
