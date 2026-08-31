"""As features de previsao bastam para jogar?

Politica sem aprendizado nenhum, so' regra: aperta a pa' do lado onde a bola vai
cruzar a linha, quando faltam poucos quadros. Se isso ja' jogar bem, a
informacao esta' toda ali e o treino tem de onde partir. Se nao jogar, as
features sao insuficientes e treinar em cima seria desperdicio.

obs: 15 = quadros ate' a linha (1 = longe/subindo) | 16 = x previsto | 17 = desce
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 6
LIMIAR = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15   # ~4 quadros

def joga(nome, escolher, mascara=False, prever=True, modelo=None):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000,
                        prever=prever, mascara_zona=mascara)
    sc, dur, ac = [], [], []
    for _ in range(N_EP):
        obs, info = env.reset(); a0 = info["ev_flip_acerto"]; n = 0
        term = trunc = False
        while not (term or trunc):
            a = escolher(obs) if modelo is None else int(modelo.predict(obs, deterministic=True)[0])
            obs, _, term, trunc, info = env.step(a); n += 1
        sc.append(info["score"]); dur.append(info["tempo_s"])
        ac.append((info["ev_flip_acerto"] - a0) / max(n, 1))
    env.close()
    print(f"{nome:>26}: score {int(np.median(sc)):>9,}  duracao {np.median(dur):>5.0f}s  "
          f"tacadas/passo {np.mean(ac):.3f}")
    return np.median(sc)

def regra(obs):
    v = obs["vetor"]
    q, x_prev, desce = float(v[15]), float(v[16]), float(v[17])
    if desce < .5 or q > LIMIAR:
        return 0
    return 1 if x_prev < 0 else 2          # x previsto a esquerda -> pa' esquerda

joga("heuristica (previsao)", regra)
joga("heuristica + mascara", regra, mascara=True)
joga("sempre ambos", lambda o: 3)
m = PPO.load("ppo_c9_base", device="cpu")
joga("ppo_c9_base (referencia)", None, prever=False, modelo=m)
