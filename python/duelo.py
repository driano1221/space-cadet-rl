"""Agente treinado x baseline sorteado, mesmo protocolo, episodios completos.

O baseline (lado sorteado, espera fixa de 100 ms) foi medido antes com n=120
decisoes; aqui os dois rodam episodios inteiros para a comparacao ser justa.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper, ESPERAS
from stable_baselines3 import PPO
try:
    from scipy import stats
except ImportError:
    stats = None

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 10
IDX = ESPERAS.index(12) + 1          # 100 ms
rng = np.random.default_rng(5)
m = PPO.load("ppo_c9_opcoes_lado", device="cpu")

def rodar(nome, escolher):
    env = OpcoesFlipper(max_decisoes=10_000)
    sc, tac, pdec = [], [], []
    for _ in range(N_EP):
        obs, info = env.reset(); a0, s0, n = info["ev_flip_acerto"], info["score"], 0
        term = trunc = False
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(escolher(obs)); n += 1
        sc.append(info["score"]); tac.append((info["ev_flip_acerto"] - a0) / max(n, 1))
        pdec.append((info["score"] - s0) / max(n, 1))
    env.close()
    print(f"{nome:>22}: score {int(np.median(sc)):>9,}  tacadas/dec {np.mean(tac):.3f}  "
          f"pontos/dec {np.mean(pdec):>8,.0f}  decisoes/ep {n}")
    return np.array(sc), np.array(tac)

a = rodar("baseline sorteado", lambda o: IDX + (len(ESPERAS) if rng.random() < .5 else 0))
b = rodar("treinado (det)", lambda o: int(m.predict(o, deterministic=True)[0]))
c = rodar("treinado (estoc)", lambda o: int(m.predict(o, deterministic=False)[0]))
if stats:
    print(f"\n  score  treinado-det vs baseline: p = {stats.mannwhitneyu(b[0], a[0]).pvalue:.4f}")
    print(f"  tacadas treinado-det vs baseline: p = {stats.mannwhitneyu(b[1], a[1]).pvalue:.4f}")
print(f"\n  referencia ppo_c9_base (sem mascara): score 2,637,750  tacadas/acionamento 0,023")
