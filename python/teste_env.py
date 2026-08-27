"""Valida a interface Gymnasium sem exigir determinismo no reset
(o ambiente e' estocastico por construcao; ver docstring do modulo)."""
import sys, numpy as np
sys.path.insert(0, '.')
from spacecadet_gym import SpaceCadetEnv
from gymnasium import spaces

env = SpaceCadetEnv()
ok = []

obs, info = env.reset(seed=1)
ok.append(("obs no espaco declarado", env.observation_space.contains(obs)))
ok.append(("obs dtype float32", obs.dtype == np.float32))
ok.append(("obs shape (9,)", obs.shape == (9,)))
ok.append(("info e' dict", isinstance(info, dict)))
ok.append(("action_space Discrete(4)", env.action_space == spaces.Discrete(4)))

obs, rec, term, trunc, info = env.step(0)
ok.append(("step devolve 5 valores", True))
ok.append(("recompensa e' float", isinstance(rec, float)))
ok.append(("terminated e' bool", isinstance(term, bool)))
ok.append(("truncated e' bool", isinstance(trunc, bool)))
ok.append(("obs pos-step no espaco", env.observation_space.contains(obs)))

# todas as acoes sao aceitas e mantem a obs valida
val = True
for a in range(4):
    o, *_ = env.step(a)
    val &= env.observation_space.contains(o)
ok.append(("todas as 4 acoes validas", val))

# um episodio inteiro termina sozinho
env.reset(seed=2)
n, term, trunc = 0, False, False
while not (term or trunc) and n < 20000:
    _, _, term, trunc, info = env.step(np.random.randint(4))
    n += 1
ok.append(("episodio termina sozinho", term))
ok.append(("score final plausivel", info["score"] > 10000))

for nome, passou in ok:
    print(f"  [{'ok' if passou else 'FALHOU'}] {nome}")
print(f"\n{sum(p for _, p in ok)}/{len(ok)} verificacoes")
print(f"episodio: {n} passos, score {info['score']}, {info['tempo_s']:.0f}s de jogo")
