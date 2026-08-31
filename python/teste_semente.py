"""Ate' onde a semente reproduz?

O modulo nativo tem RNG proprio (std::rand) e `definir_semente` o fixa no reset.
Mas o estado da mesa persiste entre episodios, entao o primeiro reset apos
semear ainda carrega residuo. Este teste mede ate' onde vai a reprodutibilidade,
em vez de assumir que ela e' total.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spacecadet_gym import SpaceCadetEnv

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)

def rollout(seed, n=150):
    obs, _ = env.reset(seed=seed)
    for i in range(n):
        obs, _, t, tr, info = env.step((i * 7) % 4)
        if t or tr:
            break
    return (info["score"], info["tela_x"], info["tela_y"])

# tres rollouts seguidos com a MESMA semente
r = [rollout(123) for _ in range(4)]
for i, x in enumerate(r):
    print(f"  reset {i+1} (seed 123): {x}")
estaveis = len(set(r[1:])) == 1
print(f"\nreset 1 igual ao 2: {r[0] == r[1]}")
print(f"resets 2+ estaveis entre si: {estaveis}")
env.close()
if estaveis:
    print("\nok: a semente reproduz A PARTIR do segundo reset; o primeiro\n"
          "    carrega residuo do estado anterior da mesa")
else:
    print("\nATENCAO: a semente nao estabiliza nem apos o segundo reset -\n"
          "    ha' outra fonte de estado nao semeada")
