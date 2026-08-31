"""As 13 acoes acionam mesmo o flipper que prometem?

Bug corrigido: antes o lado vinha da zona, e como as zonas se sobrepoem em ~60%
o ambiente escolhia sempre "esq". Aqui a checagem e' direta - o angulo da pa'
so' pode subir do lado pedido.

obs: indice 9 = angulo do flipper esquerdo, 10 = do direito.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper, ESPERAS

env = OpcoesFlipper(max_decisoes=10_000)
print(f"acoes: {env.action_space.n} (1 + 2 x {len(ESPERAS)} esperas)")
assert env.action_space.n == 13, env.action_space.n

move = {"esq": [], "dir": []}
for acao in (1, 7):            # primeira espera de cada lado
    lado = "esq" if acao <= 6 else "dir"
    obs, _ = env.reset()
    pico_e, pico_d = [], []
    for _ in range(40):
        ang_e0, ang_d0 = obs["vetor"][9], obs["vetor"][10]
        env._pico = None
        obs, _, term, trunc, _ = env.step(acao)
        pico_e.append(obs["vetor"][9]); pico_d.append(obs["vetor"][10])
        if term or trunc:
            obs, _ = env.reset()
    move[lado] = (float(np.max(pico_e)), float(np.max(pico_d)))
    print(f"  acao {acao} (lado {lado}): pico do angulo  esq={move[lado][0]:.2f}  dir={move[lado][1]:.2f}")
env.close()
# a pa' pedida tem de subir mais que a outra
assert move["esq"][0] > move["esq"][1], f"acao esquerda moveu o direito: {move['esq']}"
assert move["dir"][1] > move["dir"][0], f"acao direita moveu o esquerdo: {move['dir']}"
print("ok: cada acao aciona o flipper que promete")
