"""Ate' onde o agente vai sem o teto de 300 s?

Todas as medicoes ate' agora truncam a partida em 12.000 passos. O recorde
humano de 126 milhoes vem de partidas de horas, com bolas extras acumuladas -
estamos medindo um sprint e comparando com uma maratona.

Aqui o teto sobe para 2 horas de tempo de jogo. A partida termina quando as
bolas acabam, como no jogo de verdade.

Uso: python sem_teto.py [modelo] [n_ep]
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

TETO = 288_000          # 2 h de tempo de jogo a 40 decisoes/s
tag = sys.argv[1] if len(sys.argv) > 1 else "ppo_c9_base"
N_EP = int(sys.argv[2]) if len(sys.argv) > 2 else 8

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=TETO)
m = PPO.load(tag, device="cpu")
print(f"=== {tag} | teto de {TETO*0.025/60:.0f} min de jogo ===", flush=True)

linhas = []
for ep in range(N_EP):
    obs, _ = env.reset(); term = trunc = False
    marcos = {}
    while not (term or trunc):
        obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        # registra quando cruza cada marco de score
        for alvo in (2_000_000, 5_000_000, 10_000_000):
            if alvo not in marcos and info["score"] >= alvo:
                marcos[alvo] = info["tempo_s"]
    linhas.append(dict(ep=ep, score=info["score"], tempo=info["tempo_s"],
                       extras=info["extra_ganha"], medal=info["medal"],
                       rank=info["rank"], missoes=info["ev_missao_completa"],
                       truncado=int(trunc)))
    marc = "  ".join(f"{a//1_000_000}M@{t:.0f}s" for a, t in sorted(marcos.items()))
    print(f"  ep{ep}: {info['score']:>10,} em {info['tempo_s']:>5.0f}s  "
          f"extras={info['extra_ganha']} rank={info['rank']} "
          f"{'(TETO)' if trunc else ''}  {marc}", flush=True)

sc = np.array([l["score"] for l in linhas]); tp = np.array([l["tempo"] for l in linhas])
print(f"\nmediana {int(np.median(sc)):,}  max {int(sc.max()):,}")
print(f"duracao media {tp.mean():.0f}s  max {tp.max():.0f}s")
print(f"bolas extras: {sum(l['extras'] for l in linhas)} no total")
print(f"chegaram ao teto de 2h: {sum(l['truncado'] for l in linhas)}/{N_EP}")
with open(f"sem_teto_{tag}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
