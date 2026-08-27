import sys, numpy as np
sys.path.insert(0, '.')
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(recompensa="score", max_passos=6000)
m = PPO.load("ppo_score", device="cpu")

obs, _ = env.reset()
det, est = Counter(), Counter()
recs = []
for i in range(3000):
    a_det = int(m.predict(obs, deterministic=True)[0])
    a_est = int(m.predict(obs, deterministic=False)[0])
    det[a_det] += 1; est[a_est] += 1
    obs, r, term, trunc, info = env.step(a_det)
    recs.append(r)
    if term or trunc:
        obs, _ = env.reset()

nomes = {0: "nenhum", 1: "esq", 2: "dir", 3: "ambos"}
print("acoes com deterministic=True :", {nomes[k]: f"{v/sum(det.values()):.1%}" for k, v in sorted(det.items())})
print("acoes com deterministic=False:", {nomes[k]: f"{v/sum(est.values()):.1%}" for k, v in sorted(est.items())})
r = np.array(recs)
print(f"\nrecompensa por passo: media={r.mean():.3f} dp={r.std():.3f} "
      f"zeros={100*(r==0).mean():.1f}% max={r.max():.1f}")
