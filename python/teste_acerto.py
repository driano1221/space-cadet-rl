"""Checagem da recompensa por tacada: so' paga acerto real, e o hold nao paga."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv

P = 1.0
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, peso_acerto=P,
                    recompensa="sobrevivencia")   # base constante 0.01 isola o termo
obs, _ = env.reset()
extra_hold, extra_agita, acertos_hold, acertos_agita = [], [], 0, 0
a0 = None
for i in range(600):                       # segura ambos: nenhuma tacada deve ocorrer
    obs, r, term, trunc, info = env.step(3)
    if a0 is None: a0 = info["ev_flip_acerto"]
    extra_hold.append(r - 0.01)
    if term or trunc: obs, _ = env.reset(); a0 = None
acertos_hold = sum(1 for x in extra_hold if x > 1e-9)
obs, _ = env.reset()
for i in range(600):                       # alterna: gera movimento, logo tacadas
    obs, r, term, trunc, info = env.step(3 if i % 4 < 2 else 0)
    extra_agita.append(r - 0.01)
    if term or trunc: obs, _ = env.reset()
acertos_agita = sum(1 for x in extra_agita if x > 1e-9)
env.close()
vals = [round(x / P, 3) for x in extra_agita if x > 1e-9]
assert acertos_hold == 0, f"hold nao pode pagar tacada: {acertos_hold} pagos"
assert all(abs(v - round(v)) < 1e-6 for v in vals), f"pagamento nao inteiro: {vals[:5]}"
print(f"ok: hold pagou {acertos_hold} tacadas; alternando pagou {acertos_agita}; "
      f"valores multiplos do peso")
