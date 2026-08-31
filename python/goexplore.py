"""Ideia 1: Go-Explore por replay.

O gargalo do agente nao e' executar a sequencia longa - e' CHEGAR ao estado de
onde ela continua. Go-Explore guarda a sequencia que levou mais longe, volta a
ela por replay e explora dali, concentrando o esforco na fronteira.

Viavel porque `core.definir_semente()` torna o replay reproduzivel bit a bit.

Duas correcoes em relacao a primeira versao:
  - a fronteira e' o MAXIMO atingido no episodio, nao o estado corrente. O campo
    `progresso` conta luzes do rank ATUAL e zera a cada promocao (media 0,0 com
    maximo 9 num episodio de 10 mil passos), entao o valor instantaneo nao diz
    quao longe se chegou.
  - explora com a politica treinada mais ruido, em vez de aleatoria pura: a
    aleatoria nao mantem a bola viva o suficiente para a fronteira avancar.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
import spacecadet_env as core

ITER = int(sys.argv[1]) if len(sys.argv) > 1 else 30
RAMO = 400          # 400 passos x 25 ms = 10 s de jogo por exploracao
RUIDO = 0.15        # fracao de acoes aleatorias durante a exploracao

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000, prever=True)
core.definir_semente(4242)
m = PPO.load("ppo_c9_prever", device="cpu")
rng = np.random.default_rng(7)

def politica(obs):
    if rng.random() < RUIDO:
        return int(rng.integers(0, 4))
    return int(m.predict(obs, deterministic=True)[0])

def rodar(prefixo):
    """replay do prefixo + exploracao; devolve (acoes, (rank_max, prog_max, score))"""
    obs, info = env.reset()
    for a in prefixo:
        obs, _, term, trunc, info = env.step(a)
        if term or trunc:
            return None
    acoes = list(prefixo)
    rmax, pmax = info["rank"], info["progresso"]
    for _ in range(RAMO):
        a = politica(obs)
        acoes.append(a)
        obs, _, term, trunc, info = env.step(a)
        rmax = max(rmax, info["rank"]); pmax = max(pmax, info["progresso"])
        if term or trunc:
            break
    return acoes, (rmax, pmax, info["score"])

env.reset()                                # descarta o 1o episodio
arquivo = ([], (0, 0, 0))
print(f"{'iter':>5} {'passos':>8} {'seg':>6} {'rank':>5} {'progMax':>8} {'score':>10}")
for it in range(ITER):
    r = rodar(arquivo[0])
    if r is None:
        arquivo = ([], (0, 0, 0)); continue
    acoes, mk = r
    if mk > arquivo[1]:
        arquivo = (acoes, mk)
        print(f"{it:>5} {len(acoes):>8} {len(acoes)*25/1000:>5.0f}s "
              f"{mk[0]:>5} {mk[1]:>8} {mk[2]:>10,}", flush=True)
env.close()

rk, pg, sc = arquivo[1]
print(f"\nfronteira: rank {rk}/9  progresso maximo {pg}  score {sc:,}  "
      f"em {len(arquivo[0])*25/1000:.0f}s de jogo")
print("referencia (10 episodios do agente): rank 1,8/9  progresso max 6,2")
