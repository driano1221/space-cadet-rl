"""Berco ou cradle? Parar a bola nem sempre e' defeito.

O paper de CMU observou o agente deles "slowing down the ball until it is
captured on a flipper. It then takes a precise shot" - isso e' o *cradle*,
tecnica legitima de pinball. O que medimos como berco era parar E FICAR.

A distincao correta nao e' parar ou nao parar, e' o que vem DEPOIS:

  parada -> nada          = berco (degenerado)
  parada -> tiro para cima = cradle (tecnica)

Uso: python cradle.py <modelo> [n_ep]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

V_PARADA = 2.0      # abaixo disso a bola esta "presa"
MIN_PASSOS = 8      # ~200 ms parada para contar como parada deliberada
V_TIRO = 8.0        # acima disso saiu com forca
JANELA = 40         # ~1 s apos soltar, para ver onde a bola foi

def analisa(tag, n_ep=10):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    if tag == "aleatorio":
        rng = np.random.default_rng(9); pol = lambda o: int(rng.integers(4))
    else:
        m = PPO.load(tag, device="cpu")
        pol = lambda o: int(m.predict(o, deterministic=True)[0])

    paradas, cradles, dur_paradas, v_saida = 0, 0, [], []
    for ep in range(n_ep):
        obs, _ = env.reset(); term = trunc = False
        vs, ys = [], []
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(pol(obs))
            v = obs["vetor"]
            vs.append(float(v[4]) * 40.0); ys.append(float(v[1]) * 14.5)
        vs, ys = np.array(vs), np.array(ys)
        # acha blocos contiguos de velocidade baixa
        lento = vs < V_PARADA
        i = 0
        while i < len(lento):
            if not lento[i]:
                i += 1; continue
            j = i
            while j < len(lento) and lento[j]:
                j += 1
            if j - i >= MIN_PASSOS:
                paradas += 1
                dur_paradas.append((j - i) * 0.025)
                # o que aconteceu depois de soltar?
                fim = min(j + JANELA, len(vs))
                if fim > j:
                    vmax = vs[j:fim].max()
                    subiu = ys[j:fim].min() < ys[j] - 3      # foi para cima
                    v_saida.append(vmax)
                    if vmax > V_TIRO and subiu:
                        cradles += 1
            i = j
    env.close()
    pct = 100 * cradles / paradas if paradas else 0
    print(f"{tag:<18} paradas={paradas:>3}  cradles={cradles:>3} ({pct:>4.0f}%)  "
          f"dur.media={np.mean(dur_paradas) if dur_paradas else 0:>5.2f}s  "
          f"v.saida={np.mean(v_saida) if v_saida else 0:>5.1f}")
    return dict(paradas=paradas, cradles=cradles, pct=pct)

if __name__ == "__main__":
    print(f"{'agente':<18} {'paradas':>10}  {'cradles':>14}  {'duracao':>13}  {'saida':>11}")
    for tag in sys.argv[1:] or ["aleatorio", "ppo_visao_v1", "ppo_sobrevivencia"]:
        analisa(tag, 10)
