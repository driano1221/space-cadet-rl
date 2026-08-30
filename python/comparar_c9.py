"""Compara os tres agentes na mesma sessao, com EDA junto do agregado.

A licao do passo 5: mediana esconde efeito em sub-populacao. Aqui o score
condicionado ao pico de multiplicador vem sempre, nao so' quando questionado.

  ppo_visao_v1  8 canais, sem recompensa  -> referencia historica
  ppo_c9_base   9 canais, sem recompensa  -> isola o efeito do CANAL
  ppo_c9_mult   9 canais, com recompensa  -> isola o efeito da RECOMPENSA
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

VAL = {0: 1, 1: 2, 2: 3, 3: 5, 4: 10}
N_EP = 15
res = {}

for tag in ("ppo_c9_base", "ppo_c9_mult"):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    m = PPO.load(tag, device="cpu")
    eps, tempo, ivs = [], Counter(), []
    for ep in range(N_EP):
        obs, _ = env.reset(); term = trunc = False
        ant_a = ant_m = 0; pico = na = nt = 0; t_ult = 0.0
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
            mm, a, t = info["multiplicador"], info["mult_alvos"], info["tempo_s"]
            tempo[mm] += 1
            if a > ant_a: na += 1
            if mm > ant_m:
                nt += 1
                if t_ult: ivs.append(t - t_ult)
                t_ult = t
            pico = max(pico, mm); ant_a, ant_m = a, mm
        eps.append(dict(score=info["score"], pico=pico, alvos=na, trincas=nt))
    env.close()
    sc = np.array([e["score"] for e in eps]); pk = np.array([e["pico"] for e in eps])
    tot = sum(tempo.values())
    res[tag] = dict(sc=sc, pk=pk, eps=eps,
                    trincas=np.array([e["trincas"] for e in eps]),
                    alvos=np.array([e["alvos"] for e in eps]), ivs=np.array(ivs))
    print(f"\n=== {tag} ===")
    print(f"  score mediano={int(np.median(sc)):,}  max={int(sc.max()):,}  "
          f"cv={sc.std()/sc.mean():.2f}")
    print(f"  trincas/ep={res[tag]['trincas'].mean():.1f}  "
          f"alvos/ep={res[tag]['alvos'].mean():.1f}")
    print(f"  tempo por nivel: " + "  ".join(
        f"{VAL[k]}x={100*tempo[k]/tot:.1f}%" for k in sorted(tempo)))
    if len(res[tag]['ivs']):
        iv = res[tag]['ivs']
        print(f"  intervalo entre trincas: mediana={np.median(iv):.0f}s  "
              f"abaixo de 30s={100*(iv<30).mean():.0f}%")
    print("  score condicionado ao pico:")
    for nivel in sorted(set(pk)):
        sel = sc[pk == nivel]
        print(f"    pico {VAL[nivel]:>2}x: n={len(sel):>2}  mediano={int(np.median(sel)):>10,}")
    sys.stdout.flush()

if stats:
    a, b = res["ppo_c9_base"], res["ppo_c9_mult"]
    print("\n=== base vs mult (o efeito da RECOMPENSA) ===")
    for k in ("sc", "trincas", "alvos"):
        nome = {"sc": "score", "trincas": "trincas", "alvos": "alvos"}[k]
        print(f"  {nome:>8}: p = {stats.mannwhitneyu(a[k], b[k]).pvalue:.4f}")
