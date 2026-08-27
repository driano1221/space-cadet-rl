"""Calibra os pesos do fluxo de missao pela decomposicao real da recompensa.
Alvo: ~20% para os eventos de missao - longe dos 93% que capturaram o
objetivo no bonus de sobrevivencia."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

m = PPO.load("ppo_visao_v1", device="cpu")
for alvo, rampa, missao in ((4.0, 16.0, 80.0), (6.0, 24.0, 120.0), (9.0, 36.0, 180.0)):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=10000,
                        comprimir=True, peso_alvo=alvo, peso_rampa=rampa,
                        peso_missao=missao)
    obs, _ = env.reset()
    base = evs = 0.0
    for _ in range(9000):
        obs, r, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        base += info["rec_base"]; evs += info["rec_ev"]
        if term or trunc: obs, _ = env.reset()
    tot = base + evs or 1
    print(f"alvo={alvo:4.1f} rampa={rampa:4.1f} missao={missao:5.1f}  ->  "
          f"score {100*base/tot:5.1f}% | missao {100*evs/tot:5.1f}%")
    env.close()
