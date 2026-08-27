"""Por que a recompensa de progressao piorou tudo?
Mede a decomposicao real da recompensa e a distribuicao de acoes."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

for tag, peso in (("ppo_visao_v1", 0.0), ("ppo_progressao", 6.0)):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=8000,
                        comprimir=True, peso_progresso=peso, peso_rank=peso*5)
    m = PPO.load(tag, device="cpu")
    obs, _ = env.reset()
    base = prog = 0.0; acoes = Counter()
    for i in range(3000):
        a = int(m.predict(obs, deterministic=True)[0]); acoes[a] += 1
        obs, r, term, trunc, info = env.step(a)
        base += info["rec_base"]; prog += info["rec_prog"]
        if term or trunc: obs, _ = env.reset()
    tot = base + prog or 1
    nomes = ["nada","esq","dir","ambos"]
    n = sum(acoes.values())
    print(f"{tag}:")
    print(f"  recompensa: score={base:7.1f} ({100*base/tot:4.1f}%) | "
          f"progressao={prog:6.1f} ({100*prog/tot:4.1f}%)")
    print(f"  acoes: " + "  ".join(f"{nomes[k]}={100*acoes[k]/n:.0f}%" for k in range(4)))
    env.close()
