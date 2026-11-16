from PIL import Image, ImageDraw
# mascara de cantos arredondados para o PiP (base 116x118 escalado p/ 330x336)
W, H = 330, 336
R = 42
m = Image.new("L", (W*3, H*3), 0)
d = ImageDraw.Draw(m)
d.rounded_rectangle([0, 0, W*3-1, H*3-1], radius=R*3, fill=255)
m = m.resize((W, H), Image.LANCZOS)
m.save("C:/Users/phenr/mp-live-maisretorno/out/pip_mask.png")
print("mask ok", m.size)
