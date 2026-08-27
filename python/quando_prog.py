"""Quando o progresso acontece? Se for raro demais, a recompensa nao guia."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=24000)
m = PPO.load("ppo_visao_v1", device="cpu")
for ep in range(4):
    obs, _ = env.reset()
    term = trunc = False
    eventos, ant, passos = [], 0, 0
    while not (term or trunc):
        obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        passos += 1
        p = info["progresso"]
        if p != ant:
            eventos.append((round(info["tempo_s"]), ant, p))
            ant = p
    print(f"ep{ep}: {passos} passos ({info['tempo_s']:.0f}s), "
          f"score={info['score']:>9,}, {len(eventos)} mudancas de progresso")
    for t, de, para in eventos[:6]:
        print(f"     t={t:>3}s  progresso {de} -> {para}")
