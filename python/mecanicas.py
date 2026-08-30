"""As tres mecanicas que a pesquisa revelou e nunca medimos.

1. O multiplicador so' vale para pontos diretos da mesa (bumpers/alvos), nao
   para bonus e missoes. O agente bate mais em bumper quando o multiplicador
   esta alto? Se nao, e' por isso que a recompensa do passo 5 nao converteu.
2. Medal targets dao BOLA EXTRA sem limite - efeito multiplicativo no tempo de
   jogo. Ele consegue alguma?
3. Hyperspace: 4 luzes ativam o Center Post, que salva a bola. Ele entra?
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP = 12
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
m = PPO.load("ppo_c9_base", device="cpu")

# bumpers por segundo, separado por nivel de multiplicador ativo
por_nivel = {}       # nivel -> [passos, bumpers, pontos]
tot = dict(medal=[], extras=[], hyper=[], score=[], dur=[])

for ep in range(N_EP):
    obs, _ = env.reset(); term = trunc = False
    ant = dict(bump=0, score=0)
    while not (term or trunc):
        obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        nv = info["multiplicador"]
        d = por_nivel.setdefault(nv, [0, 0, 0])
        d[0] += 1
        d[1] += max(0, info["bumpers"] - ant["bump"])
        d[2] += max(0, info["score"] - ant["score"])
        ant["bump"], ant["score"] = info["bumpers"], info["score"]
    for k, v in (("medal", info["medal"]), ("extras", info["bolas_extras"]),
                 ("hyper", info["hyperspace"]), ("score", info["score"]),
                 ("dur", info["tempo_s"])):
        tot[k].append(v)
env.close()

VAL = {0: 1, 1: 2, 2: 3, 3: 5, 4: 10}
print(f"\n{'nivel':>6} {'passos':>8} {'bumpers/1000 passos':>21} {'pontos/passo':>14}")
for nv in sorted(por_nivel):
    p, b, sc = por_nivel[nv]
    print(f"{VAL[nv]:>5}x {p:>8,} {1000*b/p:>21.1f} {sc/p:>14,.0f}")

print(f"\nmedal targets derrubados: {np.mean(tot['medal']):.1f} por partida")
print(f"bolas extras conseguidas: {np.mean(tot['extras']):.2f} por partida  "
      f"(max {max(tot['extras'])})")
print(f"entradas no hyperspace:   {np.mean(tot['hyper']):.1f} por partida")
print(f"score mediano {int(np.median(tot['score'])):,} em {np.mean(tot['dur']):.0f}s")
