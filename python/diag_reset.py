import sys, numpy as np
sys.path.insert(0, '.')
from spacecadet_gym import SpaceCadetEnv

env = SpaceCadetEnv()
print("obs de 6 resets seguidos (mesma seed):")
obs = []
for i in range(6):
    o, _ = env.reset(seed=123)
    obs.append(o)
    print(f"  {i}: x={o[0]:+.4f} y={o[1]:+.4f} vx={o[2]:+.4f} vy={o[3]:+.4f} bolas={o[5]:.2f}")

a = np.array(obs)
print("\ndesvio-padrao por componente:", np.round(a.std(axis=0), 5))
print("resets identicos entre si:", all(np.array_equal(obs[0], o) for o in obs[1:]))

print("\nmesma sequencia de acoes a partir do reset, 2 vezes:")
for tentativa in range(2):
    env.reset(seed=123)
    total = 0.0
    for k in range(50):
        o, r, term, trunc, info = env.step(k % 4)
        total += r
    print(f"  tentativa {tentativa}: score={info['score']} recompensa={total:.2f} t={info['tempo_s']:.2f}s")
