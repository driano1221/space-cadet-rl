"""Passo 8 (tempo de reacao) + passo 6 (loop do launch pad), numa coleta so'.

O agente reage em 25 ms; um humano leva 200-300 ms e com variacao. Injetando
atraso medimos quanto do desempenho vem de reflexo sobre-humano e quanto vem de
entender o jogo. Se ele desabar com 250 ms, a vantagem era velocidade.

Aproveitamos a mesma coleta para o passo 6: ele passa repetidamente pelo launch
pad (a exploracao que as regras mencionam) ou nao?
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP = 10
ATRASOS = (0, 50, 100, 150, 250, 400)
m = PPO.load("ppo_c9_base", device="cpu")
linhas = []

print(f"{'atraso':>8} {'score mediano':>15} {'duracao':>9} {'rampas/ep':>11} {'queda':>8}")
base = None
for ms in ATRASOS:
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000, atraso_ms=ms)
    sc, du, ra = [], [], []
    for ep in range(N_EP):
        obs, _ = env.reset(); term = trunc = False
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        sc.append(info["score"]); du.append(info["tempo_s"])
        ra.append(info["ev_launch_ramp"])
        linhas.append(dict(atraso=ms, ep=ep, score=info["score"],
                           duracao=info["tempo_s"], rampas=info["ev_launch_ramp"]))
    env.close()
    med = np.median(sc)
    if base is None: base = med
    print(f"{ms:>6} ms {int(med):>15,} {np.mean(du):>8.0f}s {np.mean(ra):>11.1f} "
          f"{100*(med/base - 1):>+7.0f}%", flush=True)

with open("reacao.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
print("\nsalvo reacao.csv")
print("Referencia humana: 200-300 ms de latencia visual-motora.")
