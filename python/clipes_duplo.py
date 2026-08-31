"""GIFs do agente de decisao dupla, com velocidade ajustavel.

Uso: python clipes_duplo.py <modelo> <n_clipes> <segundos> [velocidade]
  velocidade 1 = tempo real | 2 = duas vezes mais rapido
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from env_opcoes2 import OpcoesDuplo, ESPERAS
from stable_baselines3 import PPO
import spacecadet_env as core

TAG = sys.argv[1] if len(sys.argv) > 1 else "ppo_c9_duplo"
N_CLIPES = int(sys.argv[2]) if len(sys.argv) > 2 else 6
SEG = float(sys.argv[3]) if len(sys.argv) > 3 else 20
VEL = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0

QUADRO_MS = 1000.0 / 120.0          # o jogo roda a 120 fps
A_CADA = int(round(6 * VEL))        # pula mais quadros para acelerar
DUR_MS = 50                         # 20 fps de reproducao
SAIDA = os.path.join(os.path.dirname(__file__), "..", "analise",
                     "clipes_" + TAG.replace("ppo_", ""))
os.makedirs(SAIDA, exist_ok=True)

quadros, cont = [], {"n": 0}
def captura(info, acao_quadro):
    cont["n"] += 1
    if cont["n"] % A_CADA == 0:
        quadros.append(Image.fromarray(np.array(core.capturar_tela(), dtype=np.uint8)))

env = OpcoesDuplo(max_decisoes=10_000, ao_avancar=captura)
m = PPO.load(TAG, device="cpu")
obs, info = env.reset()
alvo = int(SEG * 120 / A_CADA)

for i in range(N_CLIPES):
    quadros.clear(); cont["n"] = 0
    s0, a0, usos = info["score"], info["ev_flip_acerto"], []
    while len(quadros) < alvo:
        a = m.predict(obs, deterministic=True)[0]
        e, d = int(a[0]) > 0, int(a[1]) > 0
        usos.append("ambos" if e and d else "esq" if e else "dir" if d else "nada")
        obs, _, term, trunc, info = env.step(a)
        if term or trunc:
            obs, info = env.reset()
            s0, a0 = info["score"], info["ev_flip_acerto"]
    pts, tac = info["score"] - s0, info["ev_flip_acerto"] - a0
    nome = os.path.join(SAIDA, f"duplo_{i:02d}_{max(pts,0)//1000}k_{max(tac,0)}tac.gif")
    quadros[0].save(nome, save_all=True, append_images=quadros[1:],
                    duration=DUR_MS, loop=0, optimize=True)
    from collections import Counter
    c = Counter(usos)
    print(f"  clipe {i}: {len(quadros)}q, {pts:,} pts, {tac} tacadas, "
          f"{len(usos)} decisoes {dict(c)}", flush=True)
env.close()
print(f"velocidade {VEL}x | clipes em {os.path.abspath(SAIDA)}")
