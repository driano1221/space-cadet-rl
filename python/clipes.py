"""Gera GIFs do agente jogando, com a tela REAL do jogo.

Usa render::vscreen (o framebuffer que o jogo compoe), nao o bitmap estatico -
entao aparecem flippers se movendo, luzes acendendo, placar e mensagens.

Uso: python clipes.py <modelo> <n_clipes> <segundos_por_clipe>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
import spacecadet_env as core

TAG = sys.argv[1] if len(sys.argv) > 1 else "ppo_c9_base"
N_CLIPES = int(sys.argv[2]) if len(sys.argv) > 2 else 10
SEG = float(sys.argv[3]) if len(sys.argv) > 3 else 12
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analise",
                     "clipes_" + TAG.replace("ppo_", ""))
os.makedirs(SAIDA, exist_ok=True)

A_CADA = 2          # 1 captura a cada 2 decisoes de 25 ms
FPS = 20            # 50 ms por frame = tempo real (jogo roda a 120 quadros/s)
PREVER = TAG.endswith("prever")      # esse modelo espera 18 campos
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000, prever=PREVER)
m = PPO.load(TAG, device="cpu")

def captura():
    a = np.array(core.capturar_tela(), dtype=np.uint8)
    return Image.fromarray(a)

obs, _ = env.reset()
feitos = 0
passos_clipe = int(SEG * 40)

while feitos < N_CLIPES:
    # joga um trecho guardando quadros
    quadros, info = [], None
    marco_ini = None
    for k in range(passos_clipe):
        obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        if marco_ini is None:
            marco_ini = info["score"]
        if k % A_CADA == 0:
            quadros.append(captura())
        if term or trunc:
            obs, _ = env.reset()
            break
    if len(quadros) < 20:
        continue
    ganho = info["score"] - marco_ini
    nome = f"{SAIDA}\clipe_{feitos:02d}_{ganho//1000}k.gif"
    quadros[0].save(nome, save_all=True, append_images=quadros[1:],
                    duration=int(1000 / FPS), loop=0, optimize=True)
    tam = os.path.getsize(nome) / 1024
    print(f"  clipe {feitos:>2}: {len(quadros):>3} quadros, {ganho:>9,} pontos "
          f"no trecho, {tam:>5.0f} KB", flush=True)
    feitos += 1
env.close()
print(f"\n{N_CLIPES} clipes em {SAIDA}")
