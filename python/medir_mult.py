"""O agente usa os multiplicadores? Quanto valem?

score_multipliers = {1, 2, 3, 5, 10}: cada acerto passa por score x mult.
Tres perguntas: ele ativa? quanto rende cada nivel? ha gradiente para otimizar?
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

VALORES = {0: 1, 1: 2, 2: 3, 3: 5, 4: 10}
N_EP = 12

def roda(politica, nome):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    tempo = Counter()          # passos em cada nivel
    ganho = Counter()          # pontos ganhos em cada nivel
    subidas, linhas = 0, []
    for ep in range(N_EP):
        obs, _ = env.reset(); term = trunc = False
        ant_m, ant_s, pico = 0, 0, 0
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(politica(obs))
            m = info["multiplicador"]; s = info["score"]
            tempo[m] += 1; ganho[m] += max(0, s - ant_s)
            if m > ant_m: subidas += 1
            pico = max(pico, m); ant_m, ant_s = m, s
        linhas.append(dict(ep=ep, score=info["score"], pico=pico))
    env.close()
    tot = sum(tempo.values())
    print(f"\n=== {nome} ===")
    print(f"  score mediano: {int(np.median([l['score'] for l in linhas])):,}")
    print(f"  subidas de nivel por partida: {subidas/N_EP:.1f}")
    print(f"  pico por partida: {[l['pico'] for l in linhas]}")
    print(f"  {'nivel':>6} {'x':>4} {'% do tempo':>11} {'pontos/passo':>14}")
    for m in sorted(tempo):
        pp = ganho[m] / tempo[m] if tempo[m] else 0
        print(f"  {m:>6} {VALORES.get(m,'?'):>4} {100*tempo[m]/tot:>10.1f}% {pp:>14,.0f}")
    return linhas

rng = np.random.default_rng(5)
roda(lambda o: int(rng.integers(4)), "aleatorio")
m = PPO.load("ppo_visao_v1", device="cpu")
roda(lambda o: int(m.predict(o, deterministic=True)[0]), "PPO com visao")
