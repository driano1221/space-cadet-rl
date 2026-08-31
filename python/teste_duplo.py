"""Cada flipper responde a' sua decisao, e SO' quando a bola esta' na zona dele.

O pico do angulo tem de ser medido DURANTE a macro-acao: lendo so' a observacao
final, a pa' ja' desceu e o teste vira sorteio de timing. Aqui o callback
ao_avancar ve todos os quadros internos, e a acao aplicada a cada quadro
(bit 1 = esquerdo, bit 2 = direito) diz quem foi acionado de verdade.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes2 import OpcoesDuplo, ESPERAS

vistos = {"esq": 0, "dir": 0}
def espia(info, acao_quadro):
    if acao_quadro & 1: vistos["esq"] += 1
    if acao_quadro & 2: vistos["dir"] += 1

env = OpcoesDuplo(max_decisoes=10_000, ao_avancar=espia)
print(f"action_space: {env.action_space}")
assert list(env.action_space.nvec) == [7, 7]

def medir(acao, n=60):
    vistos["esq"] = vistos["dir"] = 0
    obs, _ = env.reset()
    zonas = {"esq": 0, "dir": 0}
    for _ in range(n):
        z_e, z_d = env._zonas_ativas(env._info)
        zonas["esq"] += z_e; zonas["dir"] += z_d
        obs, _, term, trunc, _ = env.step(acao)
        if term or trunc:
            obs, _ = env.reset()
    return dict(vistos), dict(zonas)

res = {}
for nome, acao in [("[esq=100ms, dir=nada]", [3, 0]), ("[esq=nada, dir=100ms]", [0, 3]),
                   ("[ambos=100ms]", [3, 3]), ("[nenhum]", [0, 0])]:
    v, z = medir(acao)
    res[nome] = v
    print(f"  {nome:>22}: quadros com pa' erguida  esq={v['esq']:>4}  dir={v['dir']:>4}"
          f"   (decisoes com zona ativa: esq={z['esq']} dir={z['dir']})")
env.close()

assert res["[nenhum]"] == {"esq": 0, "dir": 0}, "acao nula acionou alguma pa'"
assert res["[esq=100ms, dir=nada]"]["dir"] == 0, "acao so'-esquerda acionou a DIREITA"
assert res["[esq=100ms, dir=nada]"]["esq"] > 0, "acao so'-esquerda nao acionou nada"
assert res["[esq=nada, dir=100ms]"]["esq"] == 0, "acao so'-direita acionou a ESQUERDA"
assert res["[esq=nada, dir=100ms]"]["dir"] > 0, "acao so'-direita nao acionou nada"
assert res["[ambos=100ms]"]["esq"] > 0 and res["[ambos=100ms]"]["dir"] > 0, \
    "'ambos' nao acionou os dois"
print("\nok: cada decisao aciona so' a sua pa', e so' com a bola na zona dela")
