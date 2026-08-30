"""Quantas bolas extras o agente REALMENTE ganha?

A medicao anterior lia ExtraBalls no fim do episodio - mas esse campo e' um
saldo: sobe ao ganhar e desce ao usar (control.cpp:2796). Sempre dava zero.
Agora contamos as concessoes (table_add_extra_ball).

Mecanica: derrubar os 3 medal targets acende uma luz; na TERCEIRA vez que o
conjunto e' completado, ganha bola extra. Depois os alvos resetam.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP = 12
for tag in ("aleatorio", "ppo_c9_base"):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    if tag == "aleatorio":
        rng = np.random.default_rng(7); pol = lambda o: int(rng.integers(4))
    else:
        m = PPO.load(tag, device="cpu"); pol = lambda o: int(m.predict(o, deterministic=True)[0])
    med, ext, dur, sc = [], [], [], []
    for ep in range(N_EP):
        obs, _ = env.reset(); term = trunc = False
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(pol(obs))
        med.append(info["medal"]); ext.append(info["extra_ganha"])
        dur.append(info["tempo_s"]); sc.append(info["score"])
    env.close()
    med, ext = np.array(med), np.array(ext)
    print(f"\n=== {tag} ===")
    print(f"  medal targets/partida: {med.mean():.1f}   conjuntos completos: ~{med.mean()/3:.1f}")
    print(f"  bolas extras GANHAS:   {ext.mean():.2f}  (max {ext.max()}, "
          f"partidas com pelo menos uma: {(ext>0).sum()}/{N_EP})")
    print(f"  score mediano {int(np.median(sc)):,} em {np.mean(dur):.0f}s", flush=True)
