"""Por que a recompensa do multiplicador nao funcionou?

Nao basta o agregado. Perguntas: a recompensa foi paga? o comportamento mudou?
ele tenta os alvos e falha, ou nem tenta? o que houve nos episodios bons?
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

VAL = {0: 1, 1: 2, 2: 3, 3: 5, 4: 10}
N_EP = 14

for tag in ("ppo_visao_v1", "ppo_mult2"):
    # o env recebe os pesos para medir a decomposicao real
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000,
                        comprimir=True, peso_mult_alvo=8.0, peso_mult_nivel=32.0)
    m = PPO.load(tag, device="cpu")
    tempo, ganho = Counter(), Counter()
    eps = []; base_t = mult_t = 0.0
    for ep in range(N_EP):
        obs, _ = env.reset(); term = trunc = False
        ant_s = ant_a = 0; pico = 0; nalvos = 0; ntrincas = 0; ant_m = 0
        while not (term or trunc):
            obs, r, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
            mm, a, s = info["multiplicador"], info["mult_alvos"], info["score"]
            tempo[mm] += 1; ganho[mm] += max(0, s - ant_s)
            base_t += info["rec_base"]; mult_t += info["rec_mult"]
            if a > ant_a: nalvos += 1
            if mm > ant_m: ntrincas += 1
            pico = max(pico, mm); ant_s, ant_a, ant_m = s, a, mm
        eps.append(dict(score=info["score"], pico=pico, alvos=nalvos, trincas=ntrincas))
    tot_t = sum(tempo.values()); tot_r = base_t + mult_t or 1
    sc = np.array([e["score"] for e in eps]); pk = np.array([e["pico"] for e in eps])
    print(f"\n=== {tag} ===")
    print(f"  recompensa: score {100*base_t/tot_r:.1f}% | multiplicador {100*mult_t/tot_r:.1f}%")
    print(f"  tempo por nivel: " + "  ".join(
        f"{VAL[k]}x={100*tempo[k]/tot_t:.1f}%" for k in sorted(tempo)))
    print(f"  pico por episodio: {list(pk)}")
    print(f"  alvos/ep={np.mean([e['alvos'] for e in eps]):.1f}  "
          f"trincas/ep={np.mean([e['trincas'] for e in eps]):.1f}")
    print(f"  score mediano={int(np.median(sc)):,}  max={int(sc.max()):,}")
    if pk.max() > 0:
        for nivel in sorted(set(pk)):
            sel = sc[pk == nivel]
            print(f"    episodios com pico {VAL[nivel]}x: n={len(sel)} "
                  f"score mediano={int(np.median(sel)):,}")
    env.close()
