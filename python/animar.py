"""Gera um GIF comparando dois agentes jogando lado a lado.

Uso: python animar.py <modelo_esq> <rotulo_esq> <modelo_dir> <rotulo_dir> [segundos]
Passe "heuristica" ou "aleatorio" no lugar do modelo para usar essas politicas.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, r"C:\Users\drian\Games\pinball_patch\src")
import numpy as np
from PIL import Image, ImageDraw
from spacecadet_gym import SpaceCadetEnv
from datlib import Dat, BAK

FPS_GIF = 20          # quadros por segundo do GIF
A_CADA = 2            # amostra 1 a cada N passos (25 ms cada)


def politica_de(nome, env):
    if nome == "aleatorio":
        rng = np.random.default_rng(3)
        return lambda o: int(rng.integers(4))
    if nome == "heuristica":
        def h(o):
            v = o["vetor"] if isinstance(o, dict) else o
            rex, rey = v[11] * 7.5, v[12] * 28.0
            rdx, rdy = v[13] * 7.5, v[14] * 28.0
            vy = v[3] * 40.0
            e = abs(rex) < 5 and -4 < rey < .5 and vy > 0
            d = abs(rdx) < 5 and -4 < rdy < .5 and vy > 0
            return (1 if e else 0) + (2 if d else 0)
        return h
    from stable_baselines3 import PPO
    m = PPO.load(nome, device="cpu")
    return lambda o: int(m.predict(o, deterministic=True)[0])


def coletar(nome, segundos):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=40000)
    pol = politica_de(nome, env)
    obs, _ = env.reset()
    quadros, n = [], 0
    alvo = int(segundos * 40)          # 40 decisoes por segundo de jogo
    while n < alvo:
        obs, _, term, trunc, info = env.step(pol(obs))
        n += 1
        if n % A_CADA == 0:
            quadros.append((info["tela_x"], info["tela_y"], info["score"],
                            info["tempo_s"], info["speed"]))
        if term or trunc:
            obs, _ = env.reset()
    return quadros


def montar(qa, ra, qb, rb, saida):
    mesa = Dat(BAK).to_image(Dat(BAK).bitmap("table"))
    W, H = mesa.size
    fundo = Image.fromarray((np.asarray(mesa, dtype=float) * .8).astype("uint8"))
    imgs = []
    for (xa, ya, sa, ta, va), (xb, yb, sb, tb, vb) in zip(qa, qb):
        quadro = Image.new("RGB", (W * 2 + 30, H + 46), (16, 16, 16))
        for i, (x, y, sc, t, vel, rot) in enumerate(
                ((xa, ya, sa, ta, va, ra), (xb, yb, sb, tb, vb, rb))):
            painel = fundo.copy()
            dr = ImageDraw.Draw(painel)
            if x >= 0:
                r = 5
                dr.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 90),
                           outline=(30, 30, 30))
            quadro.paste(painel, (10 + i * (W + 10), 34))
            d2 = ImageDraw.Draw(quadro)
            d2.text((14 + i * (W + 10), 6), rot, fill=(255, 220, 120))
            d2.text((14 + i * (W + 10), 20),
                    f"score {sc:,}   v={vel:4.1f}   t={t:.0f}s", fill=(200, 200, 200))
        imgs.append(quadro)
    imgs[0].save(saida, save_all=True, append_images=imgs[1:],
                 duration=int(1000 / FPS_GIF), loop=0, optimize=True)
    print(f"{saida}  |  {len(imgs)} quadros")


if __name__ == "__main__":
    ma, ra, mb, rb = sys.argv[1:5]
    seg = float(sys.argv[5]) if len(sys.argv) > 5 else 25
    print(f"coletando {ra}...", flush=True)
    qa = coletar(ma, seg)
    print(f"coletando {rb}...", flush=True)
    qb = coletar(mb, seg)
    n = min(len(qa), len(qb))
    montar(qa[:n], ra, qb[:n], rb,
           r"C:\Users\drian\Games\pinball_rl\analise\comparacao.gif")
