from PIL import Image, ImageDraw, ImageFilter, ImageChops
S = 2048  # draw big, scale down for smooth edges
def sc(*v): return [int(x * S / 1024) for x in v]

def blob(poly_fn, blur):
    m = Image.new('L', (S, S), 0); poly_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(blur * S / 1024))
    return m.point(lambda v: 255 if v > 128 else 0)

def face(d, cx, cy, gap, eye, ink, blush):
    for sx in (-1, 1):
        ex = cx + sx * gap
        d.ellipse(sc(ex - eye, cy - eye * 1.15, ex + eye, cy + eye * 1.15), fill=ink)
        d.ellipse(sc(ex - eye * .35 + eye * .25, cy - eye * .7, ex + eye * .25 + eye * .1, cy - eye * .1), fill='white')
        bx = cx + sx * (gap + eye * 2.2)
        d.ellipse(sc(bx - 38, cy + eye * 1.2, bx + 38, cy + eye * 1.2 + 26), fill=blush)
    d.arc(sc(cx - 34, cy - 4, cx + 34, cy + 44), 20, 160, fill=ink, width=int(12 * S / 1024))

def save(im, folder):
    for n in (512, 192, 180):
        im.resize((n, n), Image.LANCZOS).save(f'{folder}/icon-{n}.png')

# ---------- onigiri (Japanese app) ----------
im = Image.new('RGB', (S, S), '#28418F'); d = ImageDraw.Draw(im)
tri = lambda o: (lambda dr: dr.polygon(sc(512, 140 - o, 160 - o, 830 + o * .6, 864 + o, 830 + o * .6), fill=255))
shadow = blob(tri(0), 70)
im.paste('#1C2F6B', (int(14 * S / 1024), int(26 * S / 1024)), shadow)       # soft drop shadow
outline = blob(tri(14), 70); rice = blob(tri(0), 70)
im.paste('#2B2B33', (0, 0), outline)
im.paste('#FBFAF5', (0, 0), rice)
nori = Image.new('L', (S, S), 0); ImageDraw.Draw(nori).rounded_rectangle(sc(392, 615, 632, 900), radius=int(18 * S / 1024), fill=255)
nori = ImageChops.multiply(nori, rice)
im.paste('#1F2E25', (0, 0), nori)
d = ImageDraw.Draw(im)
for x, y in ((480, 330), (560, 360), (505, 405), (420, 450), (610, 440)):  # rice grains
    d.ellipse(sc(x - 9, y - 5, x + 9, y + 5), fill='#ECE8DC')
face(d, 512, 540, 78, 30, '#2B2B33', '#F4A3A8')
save(im, '/home/claude/n5-flashcards')

# ---------- olive (Spanish app) ----------
im = Image.new('RGB', (S, S), '#F2C14E'); d = ImageDraw.Draw(im)
def olive_shape(grow):
    def f(dr): dr.ellipse(sc(300 - grow, 300 - grow, 724 + grow, 820 + grow), fill=255)
    return f
olive_layer = Image.new('L', (S, S), 0)
sh = blob(olive_shape(0), 4); im.paste('#C9962F', (int(16 * S / 1024), int(24 * S / 1024)), sh)
ol = blob(olive_shape(14), 4); body = blob(olive_shape(0), 4)
im.paste('#3E5416', (0, 0), ol); im.paste('#7A9A2E', (0, 0), body)
d = ImageDraw.Draw(im)
d.ellipse(sc(360, 360, 450, 520), fill='#9DBA4E')                       # shine
d.ellipse(sc(385, 385, 420, 450), fill='#C8DB8A')
# stem and leaf
d.line(sc(530, 312, 560, 210), fill='#6B4A2B', width=int(22 * S / 1024))
leaf = Image.new('L', (S, S), 0); ImageDraw.Draw(leaf).ellipse(sc(540, 150, 760, 250), fill=255)
leaf = leaf.rotate(-18, center=(int(560 * S / 1024), int(205 * S / 1024)), resample=Image.BICUBIC)
im.paste('#3E5416', (int(-4 * S / 1024), int(6 * S / 1024)), leaf); im.paste('#5E8A2A', (0, 0), leaf)
d = ImageDraw.Draw(im)
d.line(sc(585, 208, 715, 185), fill='#3E5416', width=int(8 * S / 1024))
face(d, 512, 590, 82, 30, '#26300F', '#E58A7B')
save(im, '/home/claude/n5-flashcards/spanish')
print('ok')
