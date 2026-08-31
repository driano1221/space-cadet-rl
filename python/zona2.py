"""Versao com CONTROLE: a deteccao de 'tacada efetiva' mede alguma coisa?

Se a taxa de salto de velocidade apos uma borda for igual a' taxa apos um passo
aleatorio, a deteccao nao mede o flipper - mede qualquer colisao (bumper
inclusive). Alem do controle, exige que a bola esteja na METADE INFERIOR da mesa
e subindo, o que exclui bumpers (que ficam no topo).

obs: 1 = bola_y (0=topo, 1=base) | 3 = vy | 4 = speed | 11..14 = rel esq/dir
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

TAG = sys.argv[1] if len(sys.argv) > 1 else "ppo_c9_base"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
JANELA = 4
rng = np.random.default_rng(42)

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
m = PPO.load(TAG, device="cpu")
obs, _ = env.reset()
V, A = [], []
for _ in range(N):
    V.append(obs["vetor"].copy())
    a = int(m.predict(obs, deterministic=True)[0])
    A.append(a)
    obs, _, term, trunc, _ = env.step(a)
    if term or trunc:
        obs, _ = env.reset()
env.close()
V = np.array(V); A = np.array(A)
y, vy, spd = V[:, 1], V[:, 3], V[:, 4]
d = np.diff(spd, prepend=spd[0])
LIM = np.percentile(d[d > 0], 90)
print(f"n={len(A)} | limiar {LIM:.4f} | bola_y mediana {np.median(y):.2f}")

def efetivas(idx, exigir_baixo):
    """salto de velocidade na janela; opcionalmente so' na parte baixa da mesa"""
    ok = []
    for i in idx:
        j = slice(i, min(i + JANELA, len(d)))
        cond = d[j] > LIM
        if exigir_baixo:
            cond = cond & (y[j] > np.percentile(y, 60)) & (vy[j] > 0)
        ok.append(bool(cond.any()))
    return np.array(ok)

for lado, bit, ix, iy in [("ESQUERDO", 1, 11, 12), ("DIREITO", 2, 13, 14)]:
    on = (A & bit) > 0
    bordas = np.where((~on[:-1]) & on[1:])[0] + 1
    ctrl = rng.choice(len(A) - JANELA, size=len(bordas), replace=False)
    for nome, exigir in [("qualquer salto", False), ("baixo+subindo", True)]:
        eb, ec = efetivas(bordas, exigir), efetivas(ctrl, exigir)
        lift = eb.mean() / ec.mean() if ec.mean() > 0 else float("nan")
        print(f"{lado:>9} | {nome:>14}: borda {eb.mean():5.1%}  "
              f"controle {ec.mean():5.1%}  lift {lift:4.2f}x")
        if exigir and eb.sum() >= 20 and lift > 1.2:
            xe, ye = V[bordas[eb], ix], V[bordas[eb], iy]
            qx = np.percentile(xe, [2.5, 97.5]); qy = np.percentile(ye, [2.5, 97.5])
            tx, ty = V[:, ix], V[:, iy]
            livre = ((tx >= qx[0]) & (tx <= qx[1]) & (ty >= qy[0]) & (ty <= qy[1])).mean()
            print(f"           zona x[{qx[0]:+.2f},{qx[1]:+.2f}] y[{qy[0]:+.2f},{qy[1]:+.2f}]"
                  f" -> bola dentro {livre:.1%} do tempo")
