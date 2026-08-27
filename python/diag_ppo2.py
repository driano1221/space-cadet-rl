import sys, numpy as np
sys.path.insert(0, '.')
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(recompensa="score", max_passos=6000, comprimir=True, bonus_vivo=0.02)
m = PPO.load("ppo2_score", device="cpu")
obs, _ = env.reset()
det = Counter(); score_r = []; vivo_r = []
for i in range(4000):
    a = int(m.predict(obs, deterministic=True)[0])
    det[a] += 1
    obs, r, term, trunc, info = env.step(a)
    vivo_r.append(0.02); score_r.append(r - 0.02)
    if term or trunc:
        obs, _ = env.reset()
nomes = {0: "nenhum", 1: "esq", 2: "dir", 3: "ambos"}
tot = sum(det.values())
print("acoes do PPO:", {nomes[k]: f"{v/tot:.1%}" for k, v in sorted(det.items())})
print(f"\nde onde veio a recompensa acumulada:")
print(f"  score       : {sum(score_r):8.1f}  ({100*sum(score_r)/(sum(score_r)+sum(vivo_r)):.0f}%)")
print(f"  bonus vivo  : {sum(vivo_r):8.1f}  ({100*sum(vivo_r)/(sum(score_r)+sum(vivo_r)):.0f}%)")
