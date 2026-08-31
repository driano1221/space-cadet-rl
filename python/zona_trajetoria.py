"""Zona construida pela TRAJETORIA que precede cada tacada.

A versao anterior dilatava o ponto de contato em todas as direcoes, e o
resultado subia ate' perto dos bumpers - regiao onde a pa' nao alcanca de jeito
nenhum, o que devolveria o spam pela porta dos fundos. O Adriano viu isso na
imagem.

Aqui a zona e' o conjunto de celulas por onde a bola REALMENTE passou nos N
quadros que antecederam uma tacada. E' a regiao de aproximacao medida, nao um
borrao geometrico em volta do contato.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

CEL = 10
# 200 ms de aproximacao fazia a zona subir ate' os bumpers: nesse tempo a bola
# percorre meia mesa. 100 ms cobre a aproximacao final, que e' onde a decisao
# de apertar ainda muda o resultado.
ANTES = 12          # 100 ms (12 quadros a 120 fps)
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analise")

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(quadros_por_passo=1, visao=True, max_passos=288_000)
m = PPO.load("ppo_c9_base", device="cpu")
obs, info = env.reset()

hist, trilha = [], []
zonas = {"esq": {}, "dir": {}}
ac_ant = info["ev_flip_acerto"]
ang_ant = (0.0, 0.0)
for _ in range(24000):                       # 200 s de jogo, quadro a quadro
    a = int(m.predict(obs, deterministic=True)[0])
    obs, _, term, trunc, info = env.step(a)
    cel = (info["tela_x"] // CEL, info["tela_y"] // CEL)
    hist.append((cel, obs["vetor"][9], obs["vetor"][10]))
    trilha.append(cel)
    if info["ev_flip_acerto"] > ac_ant:
        # qual pa' estava em movimento -> a tacada foi dela
        lado = "esq" if hist[-1][1] > ang_ant[0] else "dir"
        for c, _, _ in hist[-ANTES:]:
            zonas[lado][c] = zonas[lado].get(c, 0) + 1
        ac_ant = info["ev_flip_acerto"]
    ang_ant = (hist[-1][1], hist[-1][2])
    if len(hist) > ANTES + 2:
        hist.pop(0)
    if term or trunc:
        obs, info = env.reset(); ac_ant = info["ev_flip_acerto"]
env.close()

print(f"{'min_visitas':>12} {'celulas':>9} {'tempo na zona':>14}")
escolhida = None
for minv in (1, 2, 3, 5, 8):
    z = {l: {c for c, n in d.items() if n >= minv} for l, d in zonas.items()}
    n = len(z["esq"]) + len(z["dir"])
    tempo = np.mean([c in z["esq"] or c in z["dir"] for c in trilha])
    print(f"{minv:>12} {n:>9} {tempo:>13.1%}")
    if 0.04 <= tempo <= 0.09 and minv >= 3 and escolhida is None:
        escolhida = (minv, z, tempo)

if escolhida:
    minv, z, tempo = escolhida
    json.dump({"celula": CEL, "zonas": {l: sorted(map(list, c)) for l, c in z.items()}},
              open(os.path.join(BASE, "zona_reativa.json"), "w"))
    ys = [c[1] for c in z["esq"] | z["dir"]]
    print(f"\nescolhida: min_visitas={minv} -> {len(z['esq'])+len(z['dir'])} celulas, "
          f"{tempo:.1%} do tempo")
    print(f"extensao vertical: celulas y de {min(ys)} a {max(ys)} "
          f"(pixels {min(ys)*CEL} a {max(ys)*CEL} do topo)")
else:
    print("\nnenhum limiar caiu na faixa alvo")
