"""A diferenca de missoes (0,7 -> 0,9) e' real ou ruido?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import stats
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N = 20
res = {}
for tag in ("ppo_visao_v1", "ppo_missao"):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    m = PPO.load(tag, device="cpu")
    sc, mi, al = [], [], []
    for _ in range(N):
        obs, _ = env.reset(); term = trunc = False
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        sc.append(info["score"]); mi.append(info["ev_missao_completa"])
        al.append(info["ev_mission_target"])
    res[tag] = (np.array(sc), np.array(mi), np.array(al))
    print(f"{tag}: score={np.median(sc):>10,.0f} missoes={np.mean(mi):.2f}+-{np.std(mi):.2f} "
          f"alvos={np.mean(al):.1f}", flush=True)
    env.close()

a, b = res["ppo_visao_v1"], res["ppo_missao"]
print()
print("score    : Mann-Whitney p =", f"{stats.mannwhitneyu(a[0], b[0]).pvalue:.4f}")
print("missoes  : Mann-Whitney p =", f"{stats.mannwhitneyu(a[1], b[1]).pvalue:.4f}")
print("alvos    : Mann-Whitney p =", f"{stats.mannwhitneyu(a[2], b[2]).pvalue:.4f}")
