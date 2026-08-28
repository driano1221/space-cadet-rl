"""Avalia os checkpoints do passo 9 na MESMA sessao, para medir a curva de
aprendizado sem o ruido de comparar avaliacoes separadas.

Uso: python avaliar_curva.py [n_episodios]
"""
import sys, os, csv, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 15
MAX = 12000

ckpts = sorted(glob.glob("ckpt/escala_*_steps.zip"),
               key=lambda p: int(re.search(r"_(\d+)_steps", p).group(1)))
# inclui o agente vencedor de 2,5M como referencia externa
alvos = [("ppo_visao_v1", 2_500_000, "referencia (treino anterior)")]
alvos += [(p, int(re.search(r"_(\d+)_steps", p).group(1)), "checkpoint") for p in ckpts]

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=MAX)
rng = np.random.default_rng(11)

# baseline aleatorio, medido na mesma sessao
sc = []
for _ in range(N_EP):
    obs, _ = env.reset(); t = tr = False
    while not (t or tr):
        obs, _, t, tr, info = env.step(int(rng.integers(4)))
    sc.append(info["score"])
print(f"aleatorio: mediana={int(np.median(sc)):,}", flush=True)

linhas = [dict(modelo="aleatorio", passos=0, tipo="baseline", ep=i, score=s,
               duracao=0, alvos=0, missoes=0, vel=0.0, parada=0.0, topo=0.0)
          for i, s in enumerate(sc)]

for caminho, passos, tipo in alvos:
    m = PPO.load(caminho.replace(".zip", ""), device="cpu")
    for ep in range(N_EP):
        obs, _ = env.reset(); t = tr = False
        vel, ys, ac, n = [], [], Counter(), 0
        while not (t or tr):
            a = int(m.predict(obs, deterministic=True)[0]); ac[a] += 1; n += 1
            obs, _, t, tr, info = env.step(a)
            v = obs["vetor"]; vel.append(float(v[4]) * 40.0); ys.append(float(v[1]) * 14.5)
        vel = np.array(vel); ys = np.array(ys)
        linhas.append(dict(modelo=os.path.basename(caminho), passos=passos, tipo=tipo,
                           ep=ep, score=info["score"], duracao=info["tempo_s"],
                           alvos=info["ev_mission_target"], missoes=info["ev_missao_completa"],
                           vel=float(np.median(vel)), parada=float(100*(vel<2).mean()),
                           topo=float(100*(ys<-6).mean())))
    m_sc = [l["score"] for l in linhas if l["passos"] == passos and l["tipo"] == tipo]
    print(f"{passos:>10,} passos ({tipo}): mediana={int(np.median(m_sc)):,}", flush=True)

with open("curva_escala.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
print("salvo curva_escala.csv", flush=True)
