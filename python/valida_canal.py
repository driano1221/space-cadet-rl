"""Valida o canal 8: ele muda quando os alvos sao marcados?

Uma edicao que compila nao prova que o canal carrega informacao. Aqui olhamos
se os valores mudam junto com mult_bits, e se a posicao bate com a dos alvos.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from visao import C_MULT, N_CANAIS

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=9000)
obs, _ = env.reset()
print("n_canais na observacao:", obs["grade"].shape[0], "(esperado 9)")

rng = np.random.default_rng(4)
vistos = {}
for i in range(6000):
    obs, _, t, tr, info = env.step(int(rng.integers(4)))
    g = obs["grade"][C_MULT]
    chave = info.get("mult_alvos", 0)
    if chave not in vistos:
        vistos[chave] = (g.sum(), sorted(set(np.round(g[g > 0], 2).tolist())))
    if t or tr:
        obs, _ = env.reset()

print("\nmult_alvos -> (soma do canal, valores presentes)")
for k in sorted(vistos):
    soma, vals = vistos[k]
    print(f"  {k} alvo(s) marcado(s): soma={soma:6.1f}  valores={vals}")

celulas = np.argwhere(obs["grade"][C_MULT] > 0)
print(f"\ncelulas ocupadas pelo canal: {len(celulas)}")
if len(celulas):
    print(f"  faixa y: {celulas[:,0].min()}-{celulas[:,0].max()}  "
          f"faixa x: {celulas[:,1].min()}-{celulas[:,1].max()}")
    print("  (os alvos estao em tela y=67-75 de 470 -> topo da mesa, y baixo na grade)")
env.close()
