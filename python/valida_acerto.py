"""O contador flip_acerto discrimina agente treinado de politica aleatoria?

Controles ja' verificados: nunca apertar = 0 acertos; segurar erguido = 0
(a funcao so' roda com o flipper em movimento, entao premiar acerto nao tem a
brecha que punir acionamento tinha). Falta o teste discriminante.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
m = PPO.load("ppo_c9_base", device="cpu")
N = 3000
rng = np.random.default_rng(0)

def roda(nome, escolher):
    obs, _ = env.reset()
    prev, bordas, base, ult = (False, False), 0, None, 0
    for _ in range(N):
        a = escolher(obs)
        e_, d_ = bool(a & 1), bool(a & 2)
        bordas += (e_ and not prev[0]) + (d_ and not prev[1]); prev = (e_, d_)
        obs, _, term, trunc, info = env.step(a)
        if base is None:
            base = info["ev_flip_acerto"]
        ult = info["ev_flip_acerto"]
        if term or trunc:
            obs, _ = env.reset(); prev = (False, False); base = 0; ult = 0
    seg = N * 3 / 40
    print(f"{nome:>18}: {bordas:>5} acionam.  {ult-base:>4} acertos  "
          f"{(ult-base)/max(bordas,1):.3f} por acionam.  {(ult-base)/seg:.2f}/s")

roda("aleatoria", lambda o: int(rng.integers(0, 4)))
roda("agente treinado", lambda o: int(m.predict(o, deterministic=True)[0]))
env.close()
