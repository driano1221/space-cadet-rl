"""Mede o quanto o agente aciona flipper sem bola por perto.

Nao assume limiar: coleta a distancia bola-flipper no momento de CADA decisao e
compara a distribuicao nos passos em que ele aciona contra a distribuicao geral.
Se ele mirasse, acionar seria mais frequente com bola perto; se spamma, as duas
distribuicoes coincidem.

Indices do vetor de observacao: 11,12 = rel esquerdo x,y | 13,14 = rel direito.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

TAG = sys.argv[1] if len(sys.argv) > 1 else "ppo_c9_base"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 6000

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
m = PPO.load(TAG, device="cpu")
obs, _ = env.reset()

acoes, d_esq, d_dir = [], [], []
for _ in range(N):
    v = obs["vetor"]
    d_esq.append(float(np.hypot(v[11], v[12])))   # distancia no momento da decisao
    d_dir.append(float(np.hypot(v[13], v[14])))
    a = int(m.predict(obs, deterministic=True)[0])
    acoes.append(a)
    obs, _, term, trunc, _ = env.step(a)
    if term or trunc:
        obs, _ = env.reset()
env.close()

acoes = np.array(acoes); d_esq = np.array(d_esq); d_dir = np.array(d_dir)
n = len(acoes)
print(f"n = {n} passos ({n*3/40:.0f}s de jogo)\n")
print("distribuicao de acoes:")
for k, nome in enumerate(["nada", "so esquerdo", "so direito", "AMBOS"]):
    print(f"  {nome:>12}: {(acoes==k).mean():6.1%}")
print(f"  {'algum flipper':>12}: {(acoes>0).mean():6.1%}\n")

print("distancia bola->flipper (obs normalizada) no momento da decisao:")
for lado, d, mask in [("esquerdo", d_esq, (acoes & 1) > 0),
                      ("direito",  d_dir, (acoes & 2) > 0)]:
    perto = d < np.percentile(d, 25)       # quartil mais proximo = zona de alcance
    print(f"  {lado}: mediana geral {np.median(d):.3f} | ao acionar {np.median(d[mask]):.3f}")
    print(f"    P(acionar | bola perto) = {mask[perto].mean():.1%}")
    print(f"    P(acionar | bola longe) = {mask[~perto].mean():.1%}")
    razao = mask[perto].mean() / max(mask[~perto].mean(), 1e-9)
    print(f"    razao = {razao:.2f}x   (1.0 = aciona sem olhar a bola)")

for lado, bit in [("esq", 1), ("dir", 2)]:
    on = (acoes & bit) > 0
    bordas = int(((~on[:-1]) & on[1:]).sum())
    dur = on.sum() / max(bordas, 1) * 3 / 40 * 1000
    print(f"\n  {lado}: {bordas} acionamentos em {n*3/40:.0f}s "
          f"({bordas/(n*3/40):.1f}/s), duracao media {dur:.0f} ms")
