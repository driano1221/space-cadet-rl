"""Benchmark: quanto a resolucao temporal importa?

Para cada valor de quadros_por_passo comparamos duas politicas:
  - aleatoria (30% de chance de apertar por decisao)
  - heuristica, que usa a posicao da bola relativa ao flipper e so' aperta
    quando ela esta chegando - e' a politica que depende de timing fino.

Se a heuristica melhorar com quadros menores e a aleatoria nao, fica mostrado
que a resolucao temporal e' o gargalo, e nao o algoritmo.
"""
import sys, csv, time
sys.path.insert(0, '.')
import numpy as np
from spacecadet_gym import SpaceCadetEnv
import spacecadet_env as core

N_EP = 30
VALORES = [1, 2, 3, 4, 6, 12]

def heuristica(e, alcance=5.0):
    """Aperta o flipper do lado em que a bola esta chegando."""
    esq = (abs(e.bola_rel_esq_x) < alcance and -4.0 < e.bola_rel_esq_y < 0.5
           and e.bola_vy > 0)
    dir_ = (abs(e.bola_rel_dir_x) < alcance and -4.0 < e.bola_rel_dir_y < 0.5
            and e.bola_vy > 0)
    return esq, dir_

def roda(quadros, politica, n=N_EP, seed=11):
    rng = np.random.default_rng(seed)
    scores, duracoes = [], []
    for _ in range(n):
        e = core.resetar()
        passos, limite = 0, int(90000 / quadros)
        while not e.fim and passos < limite:
            if politica == "aleatoria":
                a, b = rng.random() < .3, rng.random() < .3
            else:
                a, b = heuristica(e)
            e = core.passo(bool(a), bool(b), quadros=quadros)
            passos += 1
        scores.append(e.score); duracoes.append(e.tempo_s)
    return np.median(scores), np.mean(scores), np.mean(duracoes)

SpaceCadetEnv()          # inicializa a thread do jogo
print(f"{'quadros':>8} {'ms/decisao':>11} | {'aleat.mediana':>14} | {'heur.mediana':>13} {'heur.duracao':>13}")
linhas = []
for q in VALORES:
    ma, _, da = roda(q, "aleatoria")
    mh, _, dh = roda(q, "heuristica")
    linhas.append((q, q * 1000 / 120, ma, da, mh, dh))
    print(f"{q:>8} {q*1000/120:>11.1f} | {int(ma):>14} | {int(mh):>13} {dh:>12.0f}s", flush=True)

with open("benchmark_quadros.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["quadros", "ms_por_decisao", "aleat_mediana", "aleat_duracao",
                "heur_mediana", "heur_duracao"])
    w.writerows(linhas)
print("\nsalvo em benchmark_quadros.csv")
