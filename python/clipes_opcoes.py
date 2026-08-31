"""GIFs do agente de opcoes, capturando os quadros DENTRO das macro-acoes.

Uso: python clipes_opcoes.py <modelo> <n_clipes> <segundos>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from env_opcoes import OpcoesFlipper, ESPERAS
from stable_baselines3 import PPO
import spacecadet_env as core

TAG = sys.argv[1] if len(sys.argv) > 1 else "ppo_c9_opcoes"
N_CLIPES = int(sys.argv[2]) if len(sys.argv) > 2 else 4
SEG = float(sys.argv[3]) if len(sys.argv) > 3 else 12
# deterministic=True sempre pega o topo de uma distribuicao quase plana, entao
# todo clipe sai igual. Amostrando da distribuicao aparece o que a rede
# realmente aprendeu - e clipes diferentes entre si.
DET = (len(sys.argv) > 4 and sys.argv[4] == "det")
SAIDA = os.path.join(os.path.dirname(__file__), "..", "analise",
                     "clipes_opcoes_" + TAG.replace("ppo_c9_", ""))
os.makedirs(SAIDA, exist_ok=True)

# O jogo roda a 120 quadros/s (kPassoMs = 1000/120 = 8,33 ms), nao 40 como eu
# vinha assumindo - por isso os GIFs anteriores sairam 3x mais lentos que o
# jogo real. Capturando 1 a cada 6 quadros e gravando com 50 ms por frame
# (6 x 8,33), a reproducao fica na velocidade verdadeira.
QUADRO_MS = 1000.0 / 120.0
A_CADA = 6
DUR_MS = int(round(A_CADA * QUADRO_MS))      # 50 ms -> 20 fps, tempo real
quadros, contador = [], {"n": 0}

def captura(info, acao_aplicada):
    contador["n"] += 1
    if contador["n"] % A_CADA == 0:
        quadros.append(Image.fromarray(np.array(core.capturar_tela(), dtype=np.uint8)))

env = OpcoesFlipper(max_decisoes=10_000, ao_avancar=captura)
m = PPO.load(TAG, device="cpu")
obs, info = env.reset()

alvo = int(SEG * 120 / A_CADA)     # SEG segundos de jogo de verdade
for i in range(N_CLIPES):
    quadros.clear(); contador["n"] = 0
    s0, a0, esc = info["score"], info["ev_flip_acerto"], []
    while len(quadros) < alvo:
        a = int(m.predict(obs, deterministic=DET)[0]); esc.append(a)
        obs, _, term, trunc, info = env.step(a)
        if term or trunc:
            # a partida acabou no meio do clipe: o score volta a zero e a
            # subtracao daria negativo. Reancora nos valores do novo episodio.
            obs, info = env.reset()
            s0, a0 = info["score"], info["ev_flip_acerto"]
    pts, tac = info["score"] - s0, info["ev_flip_acerto"] - a0
    nome = os.path.join(SAIDA, f"opcoes_{i:02d}_{pts//1000}k_{tac}tac.gif")
    quadros[0].save(nome, save_all=True, append_images=quadros[1:len(quadros)],
                    duration=DUR_MS, loop=0, optimize=True)
    d = np.bincount(esc, minlength=13)
    print(f"  clipe {i}: {len(quadros)} quadros, {pts:,} pontos, {tac} tacadas, "
          f"{len(esc)} decisoes {d.tolist()}", flush=True)
env.close()
print(f"clipes em {os.path.abspath(SAIDA)}")
