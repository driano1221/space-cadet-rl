"""Calibra o peso dos medal targets pela decomposicao real. Alvo ~20%."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
m = PPO.load("ppo_c9_base", device="cpu")
print(f"{'peso':>6} {'score %':>9} {'medal %':>9}")
for pm in (4.0, 8.0, 16.0):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=9000,
                        comprimir=True, peso_medal=pm)
    obs, _ = env.reset(); base = med = 0.0
    for _ in range(8000):
        obs, r, t, tr, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        base += info["rec_base"]; med += info["rec_medal"]
        if t or tr: obs, _ = env.reset()
    tot = base + med or 1
    print(f"{pm:>6.1f} {100*base/tot:>8.1f}% {100*med/tot:>8.1f}%", flush=True)
    env.close()
