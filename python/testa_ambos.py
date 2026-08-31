"""Acionar as duas pa's ajuda ou atrapalha?

Politicas fixas, espera de 100 ms nas tres:
  ambos     - sempre as duas
  so_zona   - so' a pa' cuja zona esta' ativa (na sobreposicao, sorteia)
  alternado - so' uma, alternando a cada decisao

Se "ambos" nao render mais pontos, puni-lo faz sentido; se render, punir seria
tirar a resposta correta a' incerteza de qual pa' alcanca a bola.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes2 import OpcoesDuplo, ESPERAS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 90
E = ESPERAS.index(12) + 1          # 100 ms
rng = np.random.default_rng(13)
estado = {"alt": 0}

def politica(nome, env):
    z_e, z_d = env._zonas_ativas(env._info)
    if nome == "ambos":
        return [E, E]
    if nome == "so_zona":
        if z_e and z_d:
            return [E, 0] if rng.random() < .5 else [0, E]
        return [E, 0] if z_e else [0, E]
    estado["alt"] ^= 1
    return [E, 0] if estado["alt"] else [0, E]

print(f"{'politica':>10} {'tacadas/dec':>12} {'pontos/dec':>12} {'drenos':>8} {'dec/ep':>8}")
for nome in ("ambos", "so_zona", "alternado"):
    env = OpcoesDuplo(max_decisoes=10_000)
    obs, info = env.reset()
    a0, s0, n, drenos, dec_ep = info["ev_flip_acerto"], info["score"], 0, 0, []
    tac, pts, desde = [], [], 0
    while n < N:
        obs, _, term, trunc, info = env.step(politica(nome, env))
        tac.append(info["ev_flip_acerto"] - a0); pts.append(info["score"] - s0)
        a0, s0 = info["ev_flip_acerto"], info["score"]
        n += 1; desde += 1
        if term or trunc:
            drenos += 1; dec_ep.append(desde); desde = 0
            obs, info = env.reset(); a0, s0 = info["ev_flip_acerto"], info["score"]
    env.close()
    print(f"{nome:>10} {np.mean(tac):>12.3f} {np.mean([x for x in pts if x>=0]):>12,.0f} "
          f"{drenos:>8} {np.mean(dec_ep) if dec_ep else n:>8.0f}")
