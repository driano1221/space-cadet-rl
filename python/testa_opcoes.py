"""Antes de treinar: cada espera produz resultado diferente?

Se as 7 acoes derem a mesma taxa de tacada, nao ha' o que o RL calibrar - a
resolucao temporal nao seria o gargalo e a ideia morre aqui, de graca.
Politica fixa: sempre a mesma espera, e mede tacadas e pontos por decisao.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper, ESPERAS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 120     # decisoes por politica
print(f"{N} decisoes por politica | espera em ms: {[e*25 for e in ESPERAS]}\n")
print(f"{'politica':>14} {'tacadas/decisao':>16} {'pontos/decisao':>16} {'n':>5}")

res = {}
for acao in range(7):
    env = OpcoesFlipper(max_decisoes=10_000)
    obs, info = env.reset()
    ac0, s0, n = info["ev_flip_acerto"], info["score"], 0
    tac, pts = [], []
    while n < N:
        obs, r, term, trunc, info = env.step(acao)
        tac.append(info["ev_flip_acerto"] - ac0); pts.append(info["score"] - s0)
        ac0, s0 = info["ev_flip_acerto"], info["score"]
        n += 1
        if term or trunc:
            obs, info = env.reset(); ac0, s0 = info["ev_flip_acerto"], info["score"]
    env.close()
    nome = "nao apertar" if acao == 0 else f"esperar {ESPERAS[acao-1]*25} ms"
    tac, pts = np.array(tac), np.array(pts)
    res[nome] = (tac.mean(), pts.mean())
    print(f"{nome:>14} {tac.mean():>16.3f} {pts.mean():>16,.0f} {len(tac):>5}")

melhor = max(res.items(), key=lambda kv: kv[1][0])
pior = min(res.items(), key=lambda kv: kv[1][0])
print(f"\nmelhor tacada/decisao: {melhor[0]} ({melhor[1][0]:.3f})")
print(f"pior:                  {pior[0]} ({pior[1][0]:.3f})")
raz = melhor[1][0] / max(pior[1][0], 1e-9)
print(f"razao melhor/pior: {raz:.2f}x  "
      f"-> {'HA o que calibrar' if raz > 1.5 else 'as esperas mal se distinguem'}")
