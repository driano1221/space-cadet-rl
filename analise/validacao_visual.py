"""Validacao visual usando as coordenadas de tela que o proprio jogo calcula
(proj::xform_to_2d). Gera dois paineis: densidade e trajetoria de uma partida.
"""
import csv, sys, colorsys
sys.path.insert(0, r"C:\Users\drian\Games\pinball_patch\src")
from datlib import Dat, BAK
from PIL import Image, ImageDraw
import numpy as np

d = Dat(BAK)
mesa = d.to_image(d.bitmap("table"))
W, H = mesa.size

def carrega(pol):
    xs, ys, eps, ts = [], [], [], []
    with open(f"dados/rl_trace_p{pol}.csv") as f:
        for r in csv.DictReader(f):
            xs.append(int(r["tela_x"])); ys.append(int(r["tela_y"]))
            eps.append(r["episodio"]); ts.append(float(r["tempo_s"]))
    return np.array(xs), np.array(ys), eps, ts

def densidade(xs, ys):
    m = np.zeros((H, W))
    ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
    np.add.at(m, (ys[ok], xs[ok]), 1.0)
    m = np.log1p(m)
    return m / m.max()

nomes = {0: "Nunca aperta", 1: "Aleatoria", 2: "Sempre apertado"}
paineis = [("Mesa original", np.asarray(mesa, dtype=float))]
for p in (0, 1, 2):
    xs, ys, _, _ = carrega(p)
    dn = densidade(xs, ys)
    calor = np.zeros((H, W, 3))
    calor[..., 0] = 255 * np.clip(dn * 2.2, 0, 1)
    calor[..., 1] = 255 * np.clip(dn * 1.5 - .3, 0, 1)
    calor[..., 2] = 255 * np.clip(dn * 0.8 - .5, 0, 1)
    base = np.asarray(mesa, dtype=float) * 0.40
    paineis.append((nomes[p], np.clip(base + calor * 0.9, 0, 255)))

tira = Image.new("RGB", (len(paineis) * (W + 12) + 12, H + 40), (22, 22, 22))
dr = ImageDraw.Draw(tira)
for i, (nome, arr) in enumerate(paineis):
    tira.paste(Image.fromarray(arr.astype(np.uint8)), (12 + i * (W + 12), 30))
    dr.text((16 + i * (W + 12), 10), nome, fill=(255, 220, 120))
tira.save("validacao_densidade.png")
print("validacao_densidade.png", tira.size)

# trajetoria de uma partida, agora em pixels exatos
xs, ys, eps, ts = carrega(1)
sel = [i for i in range(len(eps)) if eps[i] == "3" and ts[i] <= 40]
img = Image.fromarray((np.asarray(mesa, dtype=float) * 0.38).astype(np.uint8))
dr = ImageDraw.Draw(img)
for k in range(1, len(sel)):
    i, j = sel[k - 1], sel[k]
    a, b = (xs[i], ys[i]), (xs[j], ys[j])
    if abs(a[0] - b[0]) > 90 or abs(a[1] - b[1]) > 110:
        continue
    h = 0.60 * (1 - ts[i] / 40)
    dr.line([a, b], fill=tuple(int(255 * c) for c in colorsys.hsv_to_rgb(h, .95, 1)), width=2)
par = Image.new("RGB", (W * 2 + 36, H + 40), (22, 22, 22))
d2 = ImageDraw.Draw(par)
par.paste(mesa, (12, 30)); par.paste(img, (W + 24, 30))
d2.text((16, 10), "Mesa original", fill=(255, 220, 120))
d2.text((W + 28, 10), "Caminho da bola: 40s de uma partida (azul=inicio, vermelho=fim)", fill=(255, 220, 120))
par.save("validacao_trajetoria.png")
print("validacao_trajetoria.png", par.size, "| segmentos:", len(sel))
