"""Coleta as tacadas em coordenadas de TELA, para plotar sobre o tabuleiro real.

O CSV anterior so' tinha posicao relativa (bola - flipper), que nao da' para
sobrepor a mesa. Aqui uso tela_x/tela_y, os pixels onde o jogo desenha a bola,
e salvo tambem um screenshot limpo para servir de fundo.
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
import spacecadet_env as core

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 3
TAGS = sys.argv[2:] or ["ppo_c9_base", "ppo_c9_custoflip", "ppo_c9_acerto"]
SAIDA = os.path.join(os.path.dirname(__file__), "..", "analise")
JANELA = 3

rows = []
for tag in TAGS:
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
    m = PPO.load(tag, device="cpu")
    for ep in range(N_EP):
        obs, _ = env.reset()
        T, A, AC = [], [], []
        term = trunc = False
        while not (term or trunc):
            a = int(m.predict(obs, deterministic=True)[0]); A.append(a)
            obs, _, term, trunc, info = env.step(a)
            e = core.ultimo_estado() if hasattr(core, "ultimo_estado") else None
            T.append((info["tela_x"], info["tela_y"]))
            AC.append(info["ev_flip_acerto"])
        A = np.array(A); AC = np.array(AC); T = np.array(T)
        d = np.diff(AC, prepend=AC[0]); n = len(A)
        for lado, bit in [("esq", 1), ("dir", 2)]:
            on = (A & bit) > 0
            for i in np.where((~on[:-1]) & on[1:])[0] + 1:
                rows.append(dict(modelo=tag.replace("ppo_c9_", ""), lado=lado,
                                 tela_x=int(T[i, 0]), tela_y=int(T[i, 1]),
                                 acertou=int(d[i:min(i + JANELA, n)].sum() > 0)))
        print(f"  {tag} ep{ep}: {len(rows)} acionamentos acumulados", flush=True)
    env.close()

# screenshot limpo para o fundo
env = SpaceCadetEnv(quadros_por_passo=3, visao=True)
env.reset(); env.step(0)
Image.fromarray(np.array(core.capturar_tela())).save(os.path.join(SAIDA, "mesa_fundo.png"))
env.close()

cam = os.path.join(SAIDA, "tacadas_tela.csv")
with open(cam, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"tacadas_tela.csv: {len(rows)} linhas | acertos: {sum(r['acertou'] for r in rows)}")
