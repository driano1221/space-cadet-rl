"""Valida o inventario: desenha cada componente detectado sobre a mesa real.
Se as caixas cairem em cima dos objetos que a gente ve, a extracao esta certa.
"""
import os, sys
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
BIN = r"C:\Users\drian\Games\pinball_rl\SpaceCadetPinball\bin"
sys.path.insert(0, BIN)
sys.path.insert(0, r"C:\Users\drian\Games\pinball_patch\src")
os.chdir(BIN)
import spacecadet_env as env
from datlib import Dat, BAK
from PIL import Image, ImageDraw
from collections import Counter

env.iniciar(""); env.resetar()
inv = [p for p in env.inventario() if p.tem_sprite]
print("componentes com sprite:", len(inv), "de", len(env.inventario()))
print(Counter(p.tipo for p in inv).most_common())

d = Dat(BAK)
mesa = d.to_image(d.bitmap("table"))
W, H = mesa.size
print("mesa:", W, "x", H)
xs = [p.tela_x for p in inv]; ys = [p.tela_y for p in inv]
print(f"tela_x: {min(xs)} a {max(xs)} | tela_y: {min(ys)} a {max(ys)}")

CORES = {
    "bumper": (255, 60, 60), "alvo_popup": (255, 200, 0), "alvo_solo": (255, 140, 0),
    "rollover": (0, 220, 255), "rollover_luz": (0, 255, 200), "rampa": (180, 0, 255),
    "kickout": (255, 0, 255), "sink": (120, 120, 255), "buraco": (200, 200, 200),
    "spinner": (0, 255, 0), "kickback": (255, 255, 255), "flipper": (255, 255, 0),
    "plunger": (150, 255, 150), "dreno": (255, 0, 0), "luz": (80, 80, 255),
}
DESTAQUE = {k: v for k, v in CORES.items() if k != "luz"}

img = Image.fromarray((__import__("numpy").asarray(mesa, dtype=float) * .55).astype("uint8"))
dr = ImageDraw.Draw(img)
for p in inv:
    if p.tipo not in DESTAQUE:
        continue
    c = DESTAQUE[p.tipo]
    x0, y0 = p.tela_x - p.larg // 2, p.tela_y - p.alt // 2
    dr.rectangle([x0, y0, x0 + p.larg, y0 + p.alt], outline=c, width=2)

leg = Image.new("RGB", (150, H), (18, 18, 18))
dl = ImageDraw.Draw(leg)
for i, (t, c) in enumerate(sorted(DESTAQUE.items())):
    n = sum(1 for p in inv if p.tipo == t)
    dl.rectangle([8, 12 + i*22, 26, 26 + i*22], fill=c)
    dl.text((34, 14 + i*22), f"{t} ({n})", fill=(230, 230, 230))

par = Image.new("RGB", (W*2 + leg.width + 40, H + 20), (18, 18, 18))
par.paste(mesa, (10, 10)); par.paste(img, (W + 20, 10)); par.paste(leg, (W*2 + 30, 10))
par.save(r"C:\Users\drian\Games\pinball_rl\analise\validacao_inventario.png")
print("validacao_inventario.png salvo")
env.encerrar()
