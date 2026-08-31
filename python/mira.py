"""P(acionar flipper) em funcao da posicao RELATIVA da bola, em 2D.

A hipotenusa normalizada mistura eixos de escala diferente e mascara a zona de
alcance real. Aqui o mapa e' por celula (rel_x, rel_y), sem assumir geometria.
Compara com uma politica aleatoria de mesma taxa de acionamento.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

TAG, N = sys.argv[1], int(sys.argv[2])
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
m = PPO.load(TAG, device="cpu")
obs, _ = env.reset()

X, Y, A, VY = [], [], [], []
for _ in range(N):
    v = obs["vetor"]
    X.append([v[11], v[13]]); Y.append([v[12], v[14]]); VY.append(v[3])
    a = int(m.predict(obs, deterministic=True)[0])
    A.append(a)
    obs, _, term, trunc, _ = env.step(a)
    if term or trunc:
        obs, _ = env.reset()
env.close()

X = np.array(X); Y = np.array(Y); A = np.array(A)
np.savez(os.path.join(os.path.dirname(__file__), "..", "analise", "mira.npz"),
         X=X, Y=Y, A=A)

for i, (lado, bit) in enumerate([("ESQUERDO", 1), ("DIREITO", 2)]):
    on = (A & bit) > 0
    x, y = X[:, i], Y[:, i]
    print(f"\n=== flipper {lado} ===  taxa global {on.mean():.1%}")
    # grade 5x5 nos quantis (celulas equilibradas, sem assumir escala)
    qx = np.quantile(x, np.linspace(0, 1, 6)); qy = np.quantile(y, np.linspace(0, 1, 6))
    ix = np.clip(np.digitize(x, qx[1:-1]), 0, 4); iy = np.clip(np.digitize(y, qy[1:-1]), 0, 4)
    print("      linhas = rel_y (bola acima -> abaixo), colunas = rel_x")
    for r in range(5):
        cel = []
        for c in range(5):
            msk = (iy == r) & (ix == c)
            cel.append(f"{on[msk].mean():5.0%}" if msk.sum() > 30 else "    .")
        print(f"   y{r}  " + " ".join(cel))
    # amplitude: se ele mira, alguma celula destoa muito da taxa global
    taxas = [on[(iy == r) & (ix == c)].mean()
             for r in range(5) for c in range(5) if ((iy == r) & (ix == c)).sum() > 30]
    print(f"   min {min(taxas):.0%}  max {max(taxas):.0%}  amplitude {max(taxas)-min(taxas):.0%}")
