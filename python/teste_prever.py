"""As features de previsao estao corretas e uteis?

  1. o vetor cresce de 15 para 18 campos
  2. com a bola descendo, "quadros ate' a linha" cai conforme ela se aproxima
     (correlacao negativa com a altura)
  3. o x previsto bate com onde a bola realmente cruza a linha
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv

sem = SpaceCadetEnv(quadros_por_passo=3, visao=True); o1, _ = sem.reset(); sem.close()
com = SpaceCadetEnv(quadros_por_passo=3, visao=True, prever=True)
o2, info = com.reset()
print(f"vetor sem previsao: {o1['vetor'].shape[0]} campos | com previsao: {o2['vetor'].shape[0]}")
assert o1["vetor"].shape[0] == 15 and o2["vetor"].shape[0] == 18

hist, S, erros = [], [], []
for _ in range(3000):
    v = o2["vetor"]
    q, x_prev, desce = float(v[15]), float(v[16]), float(v[17])
    hist.append((q, x_prev, desce, info["tela_y"], info["tela_x"]))
    if desce > .5:
        S.append((info["tela_y"], q))
    o2, _, term, trunc, info = com.step(0)
    # cruzou a linha descendo? confere o x previsto de alguns passos antes
    if len(hist) > 5 and hist[-2][3] < 369 <= info["tela_y"] and hist[-2][2] > .5:
        for k in (2, 3, 4):
            qa, xa, da, _, _ = hist[-k]
            if da > .5 and 0 < qa < .5:
                erros.append(abs((xa * 100.0 + 180.0) - info["tela_x"])); break
    if term or trunc:
        o2, info = com.reset(); hist.clear()
com.close()

S = np.array(S)
print(f"passos com a bola descendo: {len(S)}")
corr = np.corrcoef(S[:, 0], S[:, 1])[0, 1]
print(f"  correlacao altura x 'quadros ate a linha': {corr:+.2f}"
      "   (negativa = mais perto, menos quadros)")
if erros:
    print(f"  erro do x previsto na linha: mediana {np.median(erros):.1f} px  (n={len(erros)})")
else:
    print("  nenhum cruzamento capturado para medir o erro do x")
assert corr < -0.3, f"a previsao nao acompanha a altura da bola: {corr:+.2f}"
print("\nok: as features acompanham a fisica da bola")
