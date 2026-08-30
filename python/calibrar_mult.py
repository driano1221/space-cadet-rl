"""Calibra os pesos do multiplicador pela decomposicao real.
Alvo: ~20% da recompensa - a faixa que funcionou no passo 4."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

m = PPO.load("ppo_visao_v1", device="cpu")
print(f"{'alvo':>6} {'trinca':>8} {'score %':>9} {'mult %':>8}  premio por completar")
for pa, pn in ((6.0, 24.0), (8.0, 32.0)):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=9000,
                        comprimir=True, peso_mult_alvo=pa, peso_mult_nivel=pn)
    obs, _ = env.reset(); base = mult = 0.0
    for _ in range(8000):
        obs, r, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        base += info["rec_base"]; mult += info["rec_mult"]
        if term or trunc: obs, _ = env.reset()
    tot = base + mult or 1
    print(f"{pa:>6.1f} {pn:>8.1f} {100*base/tot:>8.1f}% {100*mult/tot:>7.1f}%"
          f"   trinca vale {pn/(3*pa):.2f}x os 3 alvos", flush=True)
    env.close()
