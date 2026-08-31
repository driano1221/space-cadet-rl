"""Checagem do custo por acionamento: cobra borda, nao cobra hold."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spacecadet_gym import SpaceCadetEnv

C = 0.005
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, custo_flip=C, recompensa="sobrevivencia")
env.reset()
# recompensa "sobrevivencia" e' constante 0.01 -> isola o efeito do custo
r0 = env.step(0)[1]                              # nada
r_borda = env.step(1)[1]                         # off->on esquerdo
r_hold = env.step(1)[1]                          # segurando: nao cobra de novo
r_ambos = (env.step(0)[1], env.step(3)[1])       # solta, depois duas bordas
env.close()
assert abs(r0 - 0.01) < 1e-9, f"base mudou: {r0}"
assert abs(r_borda - (0.01 - C)) < 1e-9, f"borda deveria custar {C}: {r_borda}"
assert abs(r_hold - 0.01) < 1e-9, f"hold nao pode custar: {r_hold}"
assert abs(r_ambos[1] - (0.01 - 2 * C)) < 1e-9, f"duas bordas: {r_ambos[1]}"
print("ok: borda cobra, hold nao cobra, duas bordas cobram dobrado")
