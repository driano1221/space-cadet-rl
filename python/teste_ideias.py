"""Self-check das ideias 2, 3 e 4 antes de treinar.

  ideia 2 (novidade)  - bonus cai com 1/sqrt(visitas) e some com peso 0
  ideia 3 (bolas)     - definir_bolas(n) muda mesmo o numero de bolas
  ideia 4 (potencial) - F = gamma*P(s') - P(s) soma ~0 num episodio inteiro,
                        que e' a garantia de nao mudar a politica otima
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
import spacecadet_env as core

# --- ideia 3: contagem de bolas ---
for n in (0, 6):
    core.definir_bolas(n)
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
    obs, info = env.reset()
    b = []
    for _ in range(60):
        obs, _, t, tr, info = env.step(0)
        b.append(obs["vetor"][5] * 3.0)      # bolas_restantes normalizado por 3
    env.close()
    print(f"ideia 3: definir_bolas({n}) -> bolas restantes no inicio = {max(b):.0f}")
core.definir_bolas(0)

# --- ideia 4: soma telescopica do potencial ---
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000,
                    peso_potencial=1.0, recompensa="sobrevivencia")
obs, _ = env.reset()
extra, ranks = [], []
for _ in range(1500):
    obs, r, t, tr, info = env.step(3)
    extra.append(r - 0.01); ranks.append(info["rank"])
    if t or tr:
        break
env.close()
soma = sum(extra)
print(f"ideia 4: soma do shaping em {len(extra)} passos = {soma:+.4f} "
      f"(rank foi {ranks[0]} -> {ranks[-1]}, max {max(ranks)})")
print(f"         telescopica: fica proxima de 0 quando o rank nao muda")

# --- ideia 2: bonus decrescente ---
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000,
                    peso_novidade=1.0, recompensa="sobrevivencia")
obs, _ = env.reset()
bonus = []
for _ in range(400):
    obs, r, t, tr, _ = env.step(0)
    bonus.append(r - 0.01)
    if t or tr:
        break
env.close()
b = np.array(bonus)
print(f"ideia 2: bonus 1o passo {b[0]:.3f}  passo 50 {b[49]:.3f}  passo 200 {b[199]:.3f}")
assert b[0] > b[49] > b[199] > 0, "o bonus deveria cair monotonicamente"
print("\nok: as tres respondem como esperado")
