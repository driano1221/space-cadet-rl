"""Compara ppo_c9_base x ppo_c9_custoflip: o custo por acionamento mudou o
comportamento do flipper, e a que preco em score?

Avaliacao EM SERIE dentro de um processo por modelo: em paralelo o primeiro
episodio de cada processo sai identico (o jogo comeca sempre do mesmo estado) e
o n vira ilusao. Em serie os episodios divergem sozinhos.

Uso: python comparar_flip.py [n_episodios]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
try:
    from scipy import stats
except ImportError:
    stats = None

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 12
TAGS = tuple(sys.argv[2:4]) if len(sys.argv) > 3 else ("ppo_c9_base", "ppo_c9_custoflip")
res = {}

for tag in TAGS:
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
    m = PPO.load(tag, device="cpu")
    scores, taxas, bordas_s, mira = [], [], [], []
    acertos_s, acerto_por = [], []
    for ep in range(N_EP):
        obs, _ = env.reset()
        acoes, dperto = [], []
        ac0 = None
        term = trunc = False
        while not (term or trunc):
            v = obs["vetor"]
            a = int(m.predict(obs, deterministic=True)[0])
            acoes.append(a); dperto.append((v[11], v[12], v[13], v[14]))
            obs, _, term, trunc, info = env.step(a)
            if ac0 is None: ac0 = info["ev_flip_acerto"]
        A = np.array(acoes); n = len(A)
        if n < 50:
            continue
        segundos = n * 3 / 40
        b = int(((~((A & 1) > 0)[:-1]) & ((A & 1) > 0)[1:]).sum()
                + ((~((A & 2) > 0)[:-1]) & ((A & 2) > 0)[1:]).sum())
        scores.append(int(info["score"])); taxas.append(float((A > 0).mean()))
        tac = info["ev_flip_acerto"] - ac0
        acertos_s.append(tac / segundos); acerto_por.append(tac / max(b, 1))
        bordas_s.append(b / segundos)
        # seletividade: P(acionar | bola no quartil mais proximo) / P(acionar | resto)
        D = np.array(dperto)
        de = np.hypot(D[:, 0], D[:, 1]); on = (A & 1) > 0
        perto = de < np.percentile(de, 25)
        if perto.sum() > 10 and (~perto).sum() > 10 and on[~perto].mean() > 0:
            mira.append(on[perto].mean() / on[~perto].mean())
    env.close()
    res[tag] = dict(score=np.array(scores), taxa=np.array(taxas),
                    bordas=np.array(bordas_s), mira=np.array(mira),
                    acertos=np.array(acertos_s), taxa_acerto=np.array(acerto_por))
    print(f"\n=== {tag} ===  n={len(scores)}")
    print(f"  score      mediana {int(np.median(scores)):>10,}  media {int(np.mean(scores)):>10,}")
    print(f"  flipper on {np.mean(taxas):>10.1%} dos passos")
    print(f"  acionam.   {np.mean(bordas_s):>10.2f} por segundo")
    print(f"  TACADAS    {np.mean(acertos_s):>10.2f} por segundo  ({np.mean(acerto_por):.1%} dos acionamentos)")
    if len(mira):
        print(f"  seletiv.   {np.mean(mira):>10.2f}x  (>1 = aciona mais com bola perto)")

a, b = res[TAGS[0]], res[TAGS[1]]
print("\n=== base -> custoflip ===")
for k, nome, fmt in [("score", "score mediano", ","), ("bordas", "acionamentos/s", ".2f"),
                     ("acertos", "tacadas/s", ".2f"), ("taxa_acerto", "acerto/acionam.", ".1%"),
                     ("taxa", "flipper ligado", ".1%")]:
    va, vb = np.median(a[k]), np.median(b[k])
    d = (vb / va - 1) * 100 if va else float("nan")
    if fmt == ",":
        print(f"  {nome:>16}: {int(va):>10,} -> {int(vb):>10,}  ({d:+.0f}%)")
    else:
        print(f"  {nome:>16}: {va:>10{fmt}} -> {vb:>10{fmt}}  ({d:+.0f}%)")
if stats:
    print("\n  Mann-Whitney (bilateral):")
    for k, nome in [("score", "score"), ("bordas", "acionamentos/s"), ("acertos", "tacadas/s")]:
        print(f"    {nome:>16}: p = {stats.mannwhitneyu(a[k], b[k]).pvalue:.4f}")
