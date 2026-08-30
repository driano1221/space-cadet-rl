"""Compara o agente do multiplicador contra o vencedor, pareado.

O score e' o menos informativo: o que decide e' a cadencia das trincas. Se o
intervalo mediano cair abaixo de 30 s, ele venceu o decaimento.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
try:
    from scipy import stats
except ImportError:
    stats = None

N_EP = 15
res = {}
for tag in ("ppo_visao_v1", "ppo_mult2"):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    m = PPO.load(tag, device="cpu")
    scores, picos, ivs, trincas_ep, alvos_ep, tempo = [], [], [], [], [], Counter()
    for ep in range(N_EP):
        obs, _ = env.reset(); term = trunc = False
        ant_a = ant_m = 0; t_ult = 0.0; nt = na = 0
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
            a, mm, t = info["mult_alvos"], info["multiplicador"], info["tempo_s"]
            tempo[mm] += 1
            if a > ant_a: na += 1
            if mm > ant_m:
                nt += 1
                if t_ult: ivs.append(t - t_ult)
                t_ult = t
            ant_a, ant_m = a, mm
        scores.append(info["score"]); picos.append(max(picos[-1:] + [0], default=0) if False else 0)
        trincas_ep.append(nt); alvos_ep.append(na)
    tot = sum(tempo.values())
    res[tag] = dict(score=np.array(scores), trincas=np.array(trincas_ep),
                    alvos=np.array(alvos_ep), ivs=np.array(ivs),
                    p_alto=100*sum(v for k, v in tempo.items() if k >= 2)/tot)
    r = res[tag]
    print(f"\n=== {tag} ===")
    print(f"  score mediano : {int(np.median(r['score'])):,}")
    print(f"  trincas/partida: {r['trincas'].mean():.1f}   alvos/partida: {r['alvos'].mean():.1f}")
    print(f"  intervalo entre trincas: mediana={np.median(r['ivs']):.0f}s  "
          f"abaixo de 30s: {100*(r['ivs']<30).mean():.0f}%")
    print(f"  tempo em nivel 3x ou mais: {r['p_alto']:.1f}%", flush=True)
    env.close()

if stats:
    a, b = res["ppo_visao_v1"], res["ppo_mult2"]
    print("\n=== TESTES ===")
    for k in ("score", "trincas", "alvos"):
        print(f"  {k:>8}: p = {stats.mannwhitneyu(a[k], b[k]).pvalue:.4f}")
    print(f"  intervalo: p = {stats.mannwhitneyu(a['ivs'], b['ivs']).pvalue:.4f}")
