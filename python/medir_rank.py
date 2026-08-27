"""Passo 1: qual rank o agente atinge? Quantifica a distancia ate' o recorde.

Valida antes: no inicio da partida o rank deve ser 0/1 e o combustivel cheio.
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
import spacecadet_env as core
from stable_baselines3 import PPO

N_EP = 12
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=24000)

# --- sanidade: estado inicial faz sentido? ---
obs, _ = env.reset()
_, _, _, _, i0 = env.step(0)
print(f"[sanidade] no inicio: rank={i0['rank']}/{i0['rank_total']} "
      f"progresso={i0['progresso']}/{i0['progresso_total']} "
      f"combustivel={i0['combustivel']}")
if i0["rank_total"] == 0:
    print("  ERRO: grupo de luzes do rank nao resolvido"); sys.exit(1)
TOTAL_RANK = i0["rank_total"]

def avaliar(nome, politica):
    linhas = []
    for ep in range(N_EP):
        obs, _ = env.reset()
        term = trunc = False
        rank_max = prog_max = 0
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(politica(obs))
            rank_max = max(rank_max, info["rank"])
            prog_max = max(prog_max, info["progresso"])
        linhas.append((info["score"], info["tempo_s"], rank_max, prog_max))
        print(f"  ep{ep}: score={info['score']:>9,} rank_max={rank_max} "
              f"prog_max={prog_max}", flush=True)
    sc = np.array([l[0] for l in linhas]); rk = np.array([l[2] for l in linhas])
    print(f"\n  {nome}: score mediano={int(np.median(sc)):,} | "
          f"rank medio={rk.mean():.1f} | rank max={rk.max()} de {TOTAL_RANK}")
    return linhas

rng = np.random.default_rng(5)
print("\n=== ALEATORIO ===")
la = avaliar("aleatorio", lambda o: int(rng.integers(4)))
print("\n=== PPO COM VISAO ===")
m = PPO.load("ppo_visao_v1", device="cpu")
lp = avaliar("ppo", lambda o: int(m.predict(o, deterministic=True)[0]))

with open("rank_medido.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["agente","score","duracao","rank_max","prog_max"])
    for l in la: w.writerow(["aleatorio", *l])
    for l in lp: w.writerow(["ppo", *l])
print("\nsalvo em rank_medido.csv")
