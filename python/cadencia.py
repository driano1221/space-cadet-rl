"""O agente consegue fechar trincas a cada 30 s?

O multiplicador cai um nivel a cada 30 s (ControlNotifyTimerExpired). Para
chegar ao 10x sao 4 trincas mantidas nesse ritmo. Se a cadencia dele for muito
mais lenta, o teto e' da fisica da mesa, nao da politica - e o shaping nao
resolve.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=16000)
m = PPO.load("ppo_visao_v1", device="cpu")

intervalos, acertos_t, trincas = [], [], 0
for ep in range(10):
    obs, _ = env.reset(); term = trunc = False
    ant_alvos, ant_mult, t_ultima = 0, 0, 0.0
    n_acertos = 0
    while not (term or trunc):
        obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        a, mm, t = info["mult_alvos"], info["multiplicador"], info["tempo_s"]
        if a > ant_alvos:
            n_acertos += 1
        if mm > ant_mult:                      # fechou uma trinca
            trincas += 1
            if t_ultima: intervalos.append(t - t_ultima)
            t_ultima = t
        ant_alvos, ant_mult = a, mm
    acertos_t.append(n_acertos)
    print(f"  ep{ep}: {n_acertos} alvos, trincas ate' agora={trincas}", flush=True)

iv = np.array(intervalos)
print(f"\n=== CADENCIA ===")
print(f"  alvos marcados por partida: {np.mean(acertos_t):.1f}")
print(f"  trincas fechadas: {trincas} em 10 partidas")
if len(iv):
    print(f"  intervalo entre trincas: mediana={np.median(iv):.0f}s  "
          f"min={iv.min():.0f}s  max={iv.max():.0f}s  n={len(iv)}")
    print(f"  quantas abaixo de 30s (o ritmo do decaimento): "
          f"{(iv<30).sum()} de {len(iv)} ({100*(iv<30).mean():.0f}%)")
else:
    print("  (nenhum intervalo medido)")
env.close()
