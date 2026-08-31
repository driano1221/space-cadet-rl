"""Da' para prever onde a bola estara' daqui a N quadros?

Se a extrapolacao errar muito, dar "previsao" ao agente e' dar ruido. Testa
tres modelos contra a trajetoria real:
  parado  - a bola fica onde esta' (baseline burro, mede o quanto ela anda)
  linear  - posicao + velocidade * t
  gravidade - linear + aceleracao media medida nos proprios dados

Erro em pixels. A bola tem ~7 px de raio: errar mais que isso ja' inviabiliza
mirar com a previsao.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

HORIZ = [4, 8, 12, 24]          # 33, 67, 100, 200 ms a 120 fps
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6000

env = SpaceCadetEnv(quadros_por_passo=1, visao=True, max_passos=288_000)
m = PPO.load("ppo_c9_base", device="cpu")
obs, info = env.reset()
T = []                                  # (x, y, vx, vy) por quadro, do episodio
episodios = [T]
for _ in range(N):
    v = obs["vetor"]
    T.append((info["tela_x"], info["tela_y"], float(v[2]), float(v[3])))
    obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
    if term or trunc:
        obs, info = env.reset(); T = []; episodios.append(T)
env.close()

# aceleracao media (px/quadro^2) a partir das diferencas de posicao
acs = []
for T in episodios:
    if len(T) < 3: continue
    P = np.array([(t[0], t[1]) for t in T], dtype=float)
    acs.append(np.diff(P, n=2, axis=0))
AC = np.concatenate(acs) if acs else np.zeros((1, 2))
ax, ay = np.median(AC[:, 0]), np.median(AC[:, 1])
print(f"aceleracao mediana: ax={ax:+.3f}  ay={ay:+.3f} px/quadro^2\n")
print(f"{'horizonte':>10} {'parado':>9} {'linear':>9} {'gravidade':>11}  (erro mediano em px)")

for h in HORIZ:
    e_par, e_lin, e_gra = [], [], []
    for T in episodios:
        if len(T) < h + 3: continue
        P = np.array([(t[0], t[1]) for t in T], dtype=float)
        V = np.diff(P, axis=0)                       # velocidade real em px/quadro
        for i in range(1, len(P) - h):
            real = P[i + h]
            e_par.append(np.linalg.norm(real - P[i]))
            lin = P[i] + V[i - 1] * h
            e_lin.append(np.linalg.norm(real - lin))
            gra = P[i] + V[i - 1] * h + 0.5 * np.array([ax, ay]) * h * h
            e_gra.append(np.linalg.norm(real - gra))
    print(f"{h:>7}q {np.median(e_par):>9.1f} {np.median(e_lin):>9.1f} {np.median(e_gra):>11.1f}")
print("\nraio da bola ~7 px: erro acima disso inviabiliza mirar pela previsao")
