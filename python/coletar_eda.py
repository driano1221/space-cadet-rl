"""Coleta dados brutos dos tres agentes para o EDA visual.

Gera dois CSV:
  eda_episodios.csv    - uma linha por episodio (score, duracao, tacadas, rank...)
  eda_acionamentos.csv - uma linha por acionamento, com a posicao relativa da
                         bola no INICIO do movimento e se aquele acionamento
                         conectou. E' a nuvem que define a area util.

O acerto e' atribuido ao acionamento quando ev_flip_acerto sobe dentro de uma
janela curta depois da borda - o contador vem da fisica do jogo, nao de
heuristica, entao a atribuicao e' confiavel (ao contrario da tentativa por
salto de velocidade, que dava lift 1,2x sobre o acaso).
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 10
TAGS = sys.argv[2:] or ["ppo_c9_base", "ppo_c9_custoflip",
                        "ppo_c9_acerto", "ppo_c9_prever"]
JANELA = 3
SAIDA = os.path.join(os.path.dirname(__file__), "..", "analise")

ep_rows, ac_rows = [], []
for tag in TAGS:
    # o modelo com previsao espera 18 campos na observacao; o resto, 15
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000,
                        prever=tag.endswith("prever"))
    m = PPO.load(tag, device="cpu")
    for ep in range(N_EP):
        obs, _ = env.reset()
        V, A, AC = [], [], []
        term = trunc = False
        while not (term or trunc):
            V.append(obs["vetor"].copy())
            a = int(m.predict(obs, deterministic=True)[0]); A.append(a)
            obs, _, term, trunc, info = env.step(a)
            AC.append(info["ev_flip_acerto"])
        V = np.array(V); A = np.array(A); AC = np.array(AC)
        n = len(A)
        if n < 50:
            continue
        seg = n * 3 / 40
        d_ac = np.diff(AC, prepend=AC[0])
        tot_ac = int(AC[-1] - AC[0])
        bordas_tot = 0
        for lado, bit, ix, iy in [("esq", 1, 11, 12), ("dir", 2, 13, 14)]:
            on = (A & bit) > 0
            bordas = np.where((~on[:-1]) & on[1:])[0] + 1
            bordas_tot += len(bordas)
            for i in bordas:
                acertou = bool(d_ac[i:min(i + JANELA, n)].sum() > 0)
                ac_rows.append(dict(modelo=tag, episodio=ep, lado=lado,
                                    rel_x=round(float(V[i, ix]), 4),
                                    rel_y=round(float(V[i, iy]), 4),
                                    bola_y=round(float(V[i, 1]), 4),
                                    vel=round(float(V[i, 4]), 4),
                                    acertou=int(acertou)))
        ep_rows.append(dict(modelo=tag, episodio=ep, score=int(info["score"]),
                            tempo_s=round(float(info["tempo_s"]), 1),
                            duracao_s=round(seg, 1), passos=n,
                            flipper_ligado=round(float((A > 0).mean()), 4),
                            acionamentos_s=round(bordas_tot / seg, 3),
                            tacadas_s=round(tot_ac / seg, 3),
                            acerto_por_acionamento=round(tot_ac / max(bordas_tot, 1), 4),
                            ambos=round(float((A == 3).mean()), 4)))
        print(f"  {tag} ep{ep}: {info['score']:>9,}  {tot_ac:>3} tacadas  "
              f"{bordas_tot:>4} acionam.", flush=True)
    env.close()

for nome, rows in [("eda_episodios.csv", ep_rows), ("eda_acionamentos.csv", ac_rows)]:
    cam = os.path.join(SAIDA, nome)
    with open(cam, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"{nome}: {len(rows)} linhas")
