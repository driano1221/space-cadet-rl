"""A informacao temporal ajuda? Teste barato, sem treinar agente nenhum.

Hipotese: o agente nao encadeia acoes porque ve um unico instante. Se for
verdade, um historico de N quadros deve prever melhor o futuro do que 1 quadro.

Treinamos um classificador simples para prever, a partir da observacao:
  "uma trinca do multiplicador vai fechar nos proximos 3 segundos?"

Se 8 quadros preveem muito melhor que 1, a informacao existe e vale treinar o
agente com memoria. Se preveem igual, a hipotese morre aqui - em 30 min, em vez
de 75 de treino.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

HORIZONTE = 120      # 3 s a 40 decisoes/s
N_EP = 12

print("coletando trajetorias...", flush=True)
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
m = PPO.load("ppo_c9_base", device="cpu")

vets, eventos = [], []
for ep in range(N_EP):
    obs, _ = env.reset(); term = trunc = False
    v_ep, ev_ep = [], []
    ant_m = 0
    while not (term or trunc):
        v_ep.append(obs["vetor"].copy())
        obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
        mm = info["multiplicador"]
        ev_ep.append(1 if mm > ant_m else 0)   # fechou trinca neste passo
        ant_m = mm
    vets.append(np.array(v_ep)); eventos.append(np.array(ev_ep))
    print(f"  ep{ep}: {len(v_ep)} passos, {int(ev_ep and np.sum(ev_ep))} trincas", flush=True)
env.close()

def monta(n_quadros):
    """X = historico de n_quadros; y = vai fechar trinca em ate' HORIZONTE?"""
    X, y = [], []
    for v, ev in zip(vets, eventos):
        # rotulo: existe evento na janela futura?
        futuro = np.array([ev[i:i + HORIZONTE].max() if i < len(ev) else 0
                           for i in range(len(ev))])
        for i in range(n_quadros - 1, len(v)):
            X.append(v[i - n_quadros + 1:i + 1].ravel())
            y.append(futuro[i])
    return np.array(X), np.array(y)

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

print(f"\n{'quadros':>8} {'AUC':>8} {'ganho':>8}")
base = None
for n in (1, 2, 4, 8, 16):
    X, y = monta(n)
    if y.sum() < 20 or (1 - y).sum() < 20:
        print(f"{n:>8}  (poucos eventos: {int(y.sum())} positivos)"); continue
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.3, random_state=0, stratify=y)
    clf = LogisticRegression(max_iter=2000, C=1.0).fit(Xtr, ytr)
    auc = roc_auc_score(yte, clf.predict_proba(Xte)[:, 1])
    if base is None: base = auc
    print(f"{n:>8} {auc:>8.3f} {auc - base:>+8.3f}", flush=True)
print("\nAUC 0,5 = adivinhacao. Ganho > 0,05 com mais quadros = memoria ajuda.")
