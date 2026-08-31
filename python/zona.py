"""Onde a bola estava quando o agente iniciou um flip que DEU CERTO.

Uma tacada efetiva injeta energia: a velocidade da bola salta logo apos o
acionamento. Aqui, para cada borda desligado->ligado, olho os proximos passos e
classifico como efetiva se bola_speed subiu acima de um limiar. A zona util e' a
regiao (rel_x, rel_y) dessas bordas - inclui a antecipacao, porque e' medida no
INICIO do flip, nao no contato.

Indices da obs: 4 = speed | 11,12 = rel esq | 13,14 = rel dir
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

TAG = sys.argv[1] if len(sys.argv) > 1 else "ppo_c9_base"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
JANELA = 4          # passos apos o acionamento em que a tacada deve aparecer

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
spd = V[:, 4]
# salto de velocidade: limiar no p90 das variacoes positivas, para pegar o
# empurrao do flipper e nao a aceleracao normal da gravidade
d = np.diff(spd, prepend=spd[0])
LIM = np.percentile(d[d > 0], 90)
print(f"n={len(A)} passos | limiar de salto de velocidade = {LIM:.4f}\n")

for lado, bit, ix, iy in [("ESQUERDO", 1, 11, 12), ("DIREITO", 2, 13, 14)]:
    on = (A & bit) > 0
    bordas = np.where((~on[:-1]) & on[1:])[0] + 1
    efetiva = np.array([bool((d[i:i + JANELA] > LIM).any()) for i in bordas])
    x = V[bordas, ix]; y = V[bordas, iy]
    print(f"=== {lado} ===  {len(bordas)} acionamentos, "
          f"{efetiva.sum()} efetivos ({efetiva.mean():.1%})")
    if efetiva.sum() < 20:
        print("  poucos efetivos para delimitar zona\n"); continue
    xe, ye = x[efetiva], y[efetiva]
    # zona util = retangulo que cobre 95% das tacadas efetivas
    qx = np.percentile(xe, [2.5, 97.5]); qy = np.percentile(ye, [2.5, 97.5])
    print(f"  zona util (95% das efetivas): rel_x [{qx[0]:+.3f}, {qx[1]:+.3f}]  "
          f"rel_y [{qy[0]:+.3f}, {qy[1]:+.3f}]")
    dentro = (x >= qx[0]) & (x <= qx[1]) & (y >= qy[0]) & (y <= qy[1])
    print(f"  acionamentos dentro da zona: {dentro.mean():.1%}  "
          f"-> a mascara cortaria {1-dentro.mean():.1%} deles")
    # quanto do tempo TOTAL a bola passa dentro da zona (quanto a mascara liberaria)
    tx, ty = V[:, ix], V[:, iy]
    livre = ((tx >= qx[0]) & (tx <= qx[1]) & (ty >= qy[0]) & (ty <= qy[1])).mean()
    print(f"  bola dentro da zona: {livre:.1%} do tempo "
          f"-> teto de acionamento com mascara\n")
