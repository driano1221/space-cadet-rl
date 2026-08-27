"""A licao do passo 3: medir a FREQUENCIA do evento antes de recompensar.

Se 'passar pelo launch pad' tambem acontecer 1x por partida, o passo 4 morre
pelo mesmo motivo - e e' melhor descobrir aqui, em minutos, do que depois de
75 de treino.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=16000)
m = PPO.load("ppo_visao_v1", device="cpu")
CAMPOS = ["ev_mission_target", "ev_launch_ramp", "ev_missao_completa"]

tot = {c: [] for c in CAMPOS}; passos_ep = []
for ep in range(6):
    obs, _ = env.reset()
    term = trunc = False; n = 0
    while not (term or trunc):
        obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        n += 1
    for c in CAMPOS:
        tot[c].append(info[c])
    passos_ep.append(n)
    print(f"  ep{ep}: {n:>5} passos ({info['tempo_s']:.0f}s) | "
          + " | ".join(f"{c.replace('ev_',''):15s}={info[c]:>4}" for c in CAMPOS), flush=True)

print()
print("=" * 74)
print(f"{'evento':>18} {'por partida':>12} {'1 a cada N passos':>20} {'vs score':>12}")
print("=" * 74)
media_passos = np.mean(passos_ep)
for c in CAMPOS:
    m_ev = np.mean(tot[c])
    cada = media_passos / m_ev if m_ev else float("inf")
    rel = f"{cada/33:.0f}x mais raro" if cada != float("inf") else "nunca"
    print(f"{c.replace('ev_',''):>18} {m_ev:>12.1f} {cada:>20.0f} {rel:>12}")
print()
print("  referencia: score rende ~1 evento a cada 33 passos;")
print("  progresso de rank (que falhou) rendia 1 a cada 6.000.")
