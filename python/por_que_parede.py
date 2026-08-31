"""Por que a pa' como parede pontua mais que bater?

Duas explicacoes possiveis, e elas pedem numeros diferentes:
  (a) o agente mascarado PONTUA MENOS POR SEGUNDO (bater manda a bola para
      lugares ruins), ou
  (b) ele SOBREVIVE MENOS (as partidas acabam antes, e o total cai por isso)

Mede duracao, pontos por segundo e tempo com a pa' erguida nos dois.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from stable_baselines3 import PPO

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5

def base(n):
    from spacecadet_gym import SpaceCadetEnv
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
    m = PPO.load("ppo_c9_base", device="cpu")
    linhas = []
    for _ in range(n):
        obs, _ = env.reset(); erguido = passos = 0
        term = trunc = False
        while not (term or trunc):
            a = int(m.predict(obs, deterministic=True)[0])
            erguido += (a > 0); passos += 1
            obs, _, term, trunc, info = env.step(a)
        linhas.append((info["score"], info["tempo_s"], erguido / passos))
    env.close(); return linhas

def mascarado(n):
    from env_opcoes import OpcoesFlipper
    env = OpcoesFlipper(max_decisoes=10_000)
    m = PPO.load("ppo_c9_opcoes_lado", device="cpu")
    quadros = {"total": 0, "erguido": 0}
    env.ao_avancar = lambda info, a: (quadros.__setitem__("total", quadros["total"] + 1),
                                      quadros.__setitem__("erguido", quadros["erguido"] + (a > 0)))
    linhas = []
    for _ in range(n):
        quadros["total"] = quadros["erguido"] = 0
        obs, _ = env.reset()
        term = trunc = False
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        linhas.append((info["score"], info["tempo_s"],
                       quadros["erguido"] / max(quadros["total"], 1)))
    env.close(); return linhas

print(f"{'agente':>12} {'score':>10} {'duracao':>9} {'pontos/s':>10} {'pa erguida':>11}")
for nome, f in (("base", base), ("mascarado", mascarado)):
    L = f(N)
    sc = np.array([x[0] for x in L]); dur = np.array([x[1] for x in L])
    erg = np.array([x[2] for x in L])
    print(f"{nome:>12} {int(np.median(sc)):>10,} {np.median(dur):>8.0f}s "
          f"{np.median(sc/np.maximum(dur,1)):>10,.0f} {np.mean(erg):>10.0%}")
