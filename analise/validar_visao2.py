"""Sobrepoe a grade a mesa real e acompanha a bola ao longo do tempo.
Valida (a) alinhamento espacial dos canais estaticos e (b) se a bola na grade
segue a bola no jogo.
"""
import os, sys
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
BIN = r"C:\Users\drian\Games\pinball_rl\SpaceCadetPinball\bin"
for p in (BIN, r"C:\Users\drian\Games\pinball_rl\python", r"C:\Users\drian\Games\pinball_patch\src"):
    sys.path.insert(0, p)
os.chdir(BIN)
import numpy as np
import spacecadet_env as core
from visao import Visao, GRADE_L, GRADE_A, C_BOLA, C_BUMPER, C_ALVO, C_ROLLOVER, C_LUZ, C_FLIPPER
from datlib import Dat, BAK
from PIL import Image, ImageDraw

core.iniciar(""); e = core.resetar()
v = Visao(core.inventario())
d = Dat(BAK)
mesa = d.to_image(d.bitmap("table"))
W, H = mesa.size
cw, ch = W / GRADE_L, H / GRADE_A

CAN = [(C_BUMPER, (255, 60, 60), "bumper"), (C_ALVO, (255, 190, 0), "alvo"),
       (C_ROLLOVER, (0, 210, 255), "rollover"), (C_FLIPPER, (255, 255, 0), "flipper"),
       (C_LUZ, (120, 120, 255), "luz acesa"), (C_BOLA, (0, 255, 0), "bola")]

def sobrepor(g, titulo):
    img = Image.fromarray((np.asarray(mesa, dtype=float)*.5).astype("uint8"))
    dr = ImageDraw.Draw(img)
    for canal, cor, _ in CAN:
        for y in range(GRADE_A):
            for x in range(GRADE_L):
                val = float(g[canal, y, x])
                if val <= 0.01:
                    continue
                a = int(70 + 150*min(1, val))
                dr.rectangle([x*cw, y*ch, (x+1)*cw-1, (y+1)*ch-1],
                             outline=tuple(int(c*a/220) for c in cor), width=2)
    dr.text((6, 6), titulo, fill=(255, 255, 255))
    return img

quadros = []
for i in range(6):
    for _ in range(18):
        e = core.passo(i % 2 == 0, i % 3 == 0, quadros=6)
    g = v.montar(e, core.luzes_acesas())
    quadros.append(sobrepor(g, f"t={e.tempo_s:.0f}s  score={e.score}  "
                               f"bola=({e.tela_x},{e.tela_y})  flip={g[C_FLIPPER].max():.1f}"))
    print(f"  t={e.tempo_s:5.1f}s bola_tela=({e.tela_x:3d},{e.tela_y:3d}) "
          f"celulas_bola={int((g[C_BOLA]>0).sum())} luzes={int((g[C_LUZ]>0).sum())} "
          f"flip_max={g[C_FLIPPER].max():.2f}")

tira = Image.new("RGB", (len(quadros)*(W+10)+10, H+20), (20, 20, 20))
for i, q in enumerate(quadros):
    tira.paste(q, (10 + i*(W+10), 10))
tira.save(r"C:\Users\drian\Games\pinball_rl\analise\validacao_visao2.png")
print("\nvalidacao_visao2.png salvo")
core.encerrar()
