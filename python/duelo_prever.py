"""c9_base x c9_prever, episodios completos, cada um no seu ambiente.

O modelo com previsao espera 18 campos e o base 15, entao cada um roda no env
com a observacao que lhe corresponde - comparar no env errado nem carrega.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
try:
    from scipy import stats
except ImportError:
    stats = None

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 10
res = {}
for tag, prever in (("ppo_c9_base", False), ("ppo_c9_prever", True)):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000, prever=prever)
    m = PPO.load(tag, device="cpu")
    sc, dur, tac, erg = [], [], [], []
    for _ in range(N_EP):
        obs, info = env.reset(); a0 = info["ev_flip_acerto"]; n = on = 0
        term = trunc = False
        while not (term or trunc):
            a = int(m.predict(obs, deterministic=True)[0])
            on += (a > 0); n += 1
            obs, _, term, trunc, info = env.step(a)
        sc.append(info["score"]); dur.append(info["tempo_s"])
        tac.append((info["ev_flip_acerto"] - a0) / max(n, 1)); erg.append(on / n)
    env.close()
    res[tag] = dict(score=np.array(sc), dur=np.array(dur),
                    tac=np.array(tac), erg=np.array(erg))
    print(f"{tag:>14}: score {int(np.median(sc)):>9,}  max {int(max(sc)):>9,}  "
          f"duracao {np.median(dur):>4.0f}s  tacadas/passo {np.mean(tac):.4f}  "
          f"pa erguida {np.mean(erg):.0%}")

a, b = res["ppo_c9_base"], res["ppo_c9_prever"]
print("\n=== base -> prever ===")
for k, nome, f in (("score", "score mediano", "{:,.0f}"), ("dur", "duracao (s)", "{:.0f}"),
                   ("tac", "tacadas/passo", "{:.4f}"), ("erg", "pa erguida", "{:.1%}")):
    va, vb = np.median(a[k]), np.median(b[k])
    d = (vb / va - 1) * 100 if va else float("nan")
    print(f"  {nome:>16}: {f.format(va):>10} -> {f.format(vb):>10}  ({d:+.0f}%)")
if stats:
    print("\n  Mann-Whitney:")
    for k, nome in (("score", "score"), ("dur", "duracao"), ("tac", "tacadas")):
        print(f"    {nome:>10}: p = {stats.mannwhitneyu(a[k], b[k]).pvalue:.4f}")
print(f"\n  heuristica pura com as mesmas features: 965.875")
