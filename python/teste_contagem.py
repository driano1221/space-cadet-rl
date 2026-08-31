"""A recompensa cobre mesmo o intervalo decisao -> bola de volta na zona?

Tres coisas que precisam valer:
  1. o valor devolvido bate com o ganho de score REAL do intervalo
  2. os intervalos sao contiguos: nao ha' pontos perdidos entre uma decisao e a
     seguinte, nem contados duas vezes
  3. a decisao termina com a bola na zona (ou com o episodio encerrado)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper, ESPERAS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
rng = np.random.default_rng(3)

env = OpcoesFlipper(max_decisoes=10_000, compressao="macro")
obs, info = env.reset()
erros_valor, buracos, fora_da_zona, resets = [], [], 0, 0
score_ant = info["score"]

for i in range(N):
    antes = info["score"]
    # o score no fim da decisao anterior tem de ser o score no inicio desta
    if antes != score_ant:
        buracos.append((i, score_ant, antes))
    obs, rec, term, trunc, info = env.step(int(rng.integers(0, 13)))
    depois = info["score"]
    if term or trunc:
        resets += 1
        obs, info = env.reset(); score_ant = info["score"]
        continue
    # com compressao "macro": rec = sqrt(ganho/1000) -> ganho = rec^2 * 1000
    ganho_real = depois - antes
    ganho_rec = rec ** 2 * 1000
    if abs(ganho_rec - ganho_real) > max(1.0, ganho_real * 1e-6):
        erros_valor.append((i, ganho_real, ganho_rec))
    if not env._na_zona(info):
        fora_da_zona += 1
    score_ant = depois
env.close()

print(f"{N} decisoes | {resets} episodios encerrados no meio")
print(f"1. valor bate com o ganho real:  {len(erros_valor)} divergencias")
for e in erros_valor[:3]:
    print(f"     decisao {e[0]}: real {e[1]:,.0f} vs recompensa {e[2]:,.0f}")
print(f"2. intervalos contiguos:         {len(buracos)} buracos")
for b in buracos[:3]:
    print(f"     decisao {b[0]}: terminou em {b[1]:,} e a seguinte comecou em {b[2]:,}")
print(f"3. terminou com a bola na zona:  {N - resets - fora_da_zona}/{N - resets}")
assert not erros_valor, "a recompensa nao corresponde ao ganho de score do intervalo"
assert not buracos, "ha' pontos perdidos ou contados duas vezes entre decisoes"
print("\nok: a contagem cobre o intervalo inteiro, sem buraco nem dupla contagem")
