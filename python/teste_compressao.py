"""As duas reguas dao valores diferentes para o MESMO jogo?

Roda a mesma sequencia de acoes nos dois modos e compara. Se a soma por quadro
nao for maior que a raiz do total, a distorcao que motivou a variante nao existe
e nao ha' o que testar.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper

N, ACAO = 60, 3
res = {}
for modo in ("quadro", "macro"):
    env = OpcoesFlipper(max_decisoes=10_000, compressao=modo)
    obs, info = env.reset()
    s0, recs = info["score"], []
    for _ in range(N):
        obs, r, term, trunc, info = env.step(ACAO)
        recs.append(r)
        if term or trunc:
            obs, info = env.reset()
    env.close()
    res[modo] = np.array(recs)
    print(f"{modo:>7}: soma {res[modo].sum():8.2f}  media {res[modo].mean():6.3f}  "
          f"max {res[modo].max():6.2f}  zerados {(res[modo]==0).mean():.0%}")

q, m = res["quadro"], res["macro"]
assert q.sum() > m.sum(), "quadro deveria somar mais (somar raizes > raiz da soma)"
print(f"\nrazao quadro/macro: {q.sum()/max(m.sum(),1e-9):.2f}x")
print("ok: as duas reguas medem o mesmo jogo com valores diferentes")
