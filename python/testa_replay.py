"""Com a semente fixa, rejogar a mesma sequencia reproduz o mesmo episodio?

Go-Explore precisa voltar a um estado promissor e explorar dali. Sem save state,
o caminho e' o replay - que exige determinismo. `core.definir_semente()` fixa
std::rand a cada reset (RandFloat usa std::rand).

O primeiro episodio apos iniciar() parte de um estado diferente dos demais, entao
o que importa e' a estabilidade do segundo em diante.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
import spacecadet_env as core

rng = np.random.default_rng(99)
acoes = [int(rng.integers(0, 4)) for _ in range(400)]

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
core.definir_semente(1234)
marcas = []
for tentativa in range(5):
    obs, info = env.reset()
    for a in acoes:
        obs, _, term, trunc, info = env.step(a)
        if term or trunc:
            break
    marcas.append((info["score"], info["tela_x"], info["tela_y"], round(info["tempo_s"], 1)))
    print(f"  replay {tentativa+1}: score {info['score']:>8,}  "
          f"bola ({info['tela_x']:>3},{info['tela_y']:>3})  t={info['tempo_s']:.1f}s")
env.close()

estavel = all(m == marcas[1] for m in marcas[1:])
print(f"\nreplay estavel do 2o em diante: {estavel}")
print("-> Go-Explore por replay VIAVEL" if estavel else "-> replay ainda diverge")
