"""Magnitude tipica da recompensa por passo, para calibrar o custo do flipper."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
m = PPO.load("ppo_c9_base", device="cpu")
obs, _ = env.reset()
recs, acoes = [], []
for _ in range(4000):
    a = int(m.predict(obs, deterministic=True)[0])
    obs, r, term, trunc, _ = env.step(a)
    recs.append(r); acoes.append(a)
    if term or trunc:
        obs, _ = env.reset()
env.close()
r = np.array(recs); a = np.array(acoes)
print(f"recompensa por passo: media {r.mean():.4f}  mediana {np.median(r):.4f}")
print(f"  zerada em {(r==0).mean():.1%} dos passos")
print(f"  quando != 0: media {r[r!=0].mean():.3f}  p90 {np.percentile(r[r!=0],90):.3f}")
on_e = (a & 1) > 0; on_d = (a & 2) > 0
bordas = int(((~on_e[:-1]) & on_e[1:]).sum() + ((~on_d[:-1]) & on_d[1:]).sum())
print(f"\nbordas de acionamento: {bordas} em {len(a)} passos = {bordas/len(a):.2f} por passo")
print(f"recompensa media por passo / bordas por passo = {r.mean()/(bordas/len(a)):.4f}")
print("  -> custo que consumiria X% da recompensa:")
for pct in (0.02, 0.05, 0.10):
    print(f"     {pct:.0%}: custo = {r.mean()*pct/(bordas/len(a)):.4f}")
