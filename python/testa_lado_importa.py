"""Escolher o lado certo importa, ou tanto faz?

Se as tres politicas fixas (sempre esq / sempre dir / sorteado) derem o mesmo
resultado, o lado nao carrega sinal e devolve-lo ao agente nao ajuda - so'
dobrou o espaco de acao a` toa. Espera fixa em 100 ms (topo do plato) para
isolar o efeito do LADO.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper, ESPERAS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
IDX = ESPERAS.index(12) + 1          # 100 ms -> acao 3 (esq) / 9 (dir)
rng = np.random.default_rng(11)
print(f"{N} decisoes por politica | espera fixa 100 ms\n")
print(f"{'politica':>14} {'tacadas/dec':>12} {'pontos/dec':>12} {'drenos':>8}")

for nome, escolher in [("sempre esq", lambda: IDX),
                       ("sempre dir", lambda: IDX + len(ESPERAS)),
                       ("sorteado",   lambda: IDX + (len(ESPERAS) if rng.random() < .5 else 0))]:
    env = OpcoesFlipper(max_decisoes=10_000)
    obs, info = env.reset()
    a0, s0, n, drenos = info["ev_flip_acerto"], info["score"], 0, 0
    tac, pts = [], []
    while n < N:
        obs, _, term, trunc, info = env.step(escolher())
        tac.append(info["ev_flip_acerto"] - a0); pts.append(info["score"] - s0)
        a0, s0 = info["ev_flip_acerto"], info["score"]; n += 1
        if term or trunc:
            drenos += 1
            obs, info = env.reset(); a0, s0 = info["ev_flip_acerto"], info["score"]
    env.close()
    print(f"{nome:>14} {np.mean(tac):>12.3f} "
          f"{np.mean([x for x in pts if x>=0]):>12,.0f} {drenos:>8}")
