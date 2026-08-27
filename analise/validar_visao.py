"""Renderiza cada canal da grade ao lado da mesa real, em varios instantes.
Se os canais estaticos casarem com os objetos e a bola aparecer onde deveria,
a visao esta correta.
"""
import os, sys
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
BIN = r"C:\Users\drian\Games\pinball_rl\SpaceCadetPinball\bin"
for p in (BIN, r"C:\Users\drian\Games\pinball_rl\python", r"C:\Users\drian\Games\pinball_patch\src"):
    sys.path.insert(0, p)
os.chdir(BIN)
import numpy as np
import spacecadet_env as core
from visao import Visao, GRADE_L, GRADE_A, N_CANAIS
from datlib import Dat, BAK
from PIL import Image, ImageDraw

core.iniciar("")
e = core.resetar()
v = Visao(core.inventario())

NOMES = ["bola", "vel x", "vel y", "bumpers", "alvos", "rollovers", "luzes", "flippers"]
CEL = 9

def painel(g, canal):
    """Um canal da grade como imagem."""
    a = g[canal]
    img = Image.new("RGB", (GRADE_L*CEL, GRADE_A*CEL), (12, 12, 12))
    dr = ImageDraw.Draw(img)
    for y in range(GRADE_A):
        for x in range(GRADE_L):
            val = float(a[y, x])
            if val == 0:
                continue
            if val > 0:
                c = (int(255*min(1, val)), int(180*min(1, val)), 40)
            else:
                c = (40, int(120*min(1, -val)), int(255*min(1, -val)))
            dr.rectangle([x*CEL, y*CEL, x*CEL+CEL-1, y*CEL+CEL-1], fill=c)
    return img

d = Dat(BAK)
mesa = d.to_image(d.bitmap("table")).resize((GRADE_L*CEL, GRADE_A*CEL))

# avanca ate' a bola estar em jogo e coleta 1 quadro
for _ in range(40):
    e = core.passo(False, False, quadros=6)
g = v.montar(e, core.luzes_acesas())

W = GRADE_L*CEL
tira = Image.new("RGB", (W*(N_CANAIS+1) + 20*(N_CANAIS+2), GRADE_A*CEL + 40), (20, 20, 20))
dr = ImageDraw.Draw(tira)
tira.paste(mesa, (20, 30)); dr.text((24, 10), "MESA REAL", fill=(255, 220, 120))
for i in range(N_CANAIS):
    x = 20 + (i+1)*(W + 20)
    tira.paste(painel(g, i), (x, 30))
    nz = int((g[i] != 0).sum())
    dr.text((x + 4, 10), f"{NOMES[i]} ({nz})", fill=(255, 220, 120))
tira.save(r"C:\Users\drian\Games\pinball_rl\analise\validacao_visao.png")

print("bola em tela:", e.tela_x, e.tela_y, "| score:", e.score)
for i, n in enumerate(NOMES):
    print(f"  canal {i} {n:10s}: {int((g[i]!=0).sum()):4d} celulas ativas, "
          f"soma={float(g[i].sum()):7.2f}")
print("\nvalidacao_visao.png salvo")
core.encerrar()
