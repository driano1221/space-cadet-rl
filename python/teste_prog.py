"""Valida a recompensa de progressao: quanto dela vem de cada fonte?

A licao do bonus de 0,02: um termo secundario pode dominar a recompensa sem
que se perceba. Aqui medimos a proporcao antes de treinar.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv

for peso in (1.0, 3.0, 10.0):
    rng = np.random.default_rng(5)          # mesma sequencia de acoes
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=8000,
                        comprimir=True, peso_progresso=peso, peso_rank=peso * 5)
    obs, _ = env.reset()
    base = prog = 0.0
    term = trunc = False
    while not (term or trunc):
        obs, r, term, trunc, info = env.step(int(rng.integers(4)))
        base += info["rec_base"]; prog += info["rec_prog"]
    tot = base + prog
    print(f"peso={peso:5.1f} | score={base:7.1f} ({100*base/tot:4.1f}%) | "
          f"progressao={prog:7.1f} ({100*prog/tot:4.1f}%) | "
          f"rank={info['rank']} prog={info['progresso']}/18")
    env.close()
