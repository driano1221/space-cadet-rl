import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=6000,
                    comprimir=True, peso_progresso=6.0, peso_rank=30.0)
print("peso lido pelo env:", env.peso_progresso, env.peso_rank)
rng = np.random.default_rng(1)
obs, _ = env.reset()
vistos, pagos = [], 0.0
for i in range(2500):
    obs, r, term, trunc, info = env.step(int(rng.integers(4)))
    vistos.append(info["progresso"]); pagos += info["rec_prog"]
    if term or trunc: break
print("progresso ao longo do episodio:", sorted(set(vistos)))
print("recompensa de progressao paga:", pagos)
print("_prog_ant final:", env._prog_ant)
