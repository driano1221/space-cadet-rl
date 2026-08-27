"""EDA do agente de missao: procurar anomalia, nao so' medias.

Rank 1,9 abaixo do aleatorio (2,6) nao fecha com score 3x maior. Ou ha' bug de
leitura, ou o comportamento e' degenerado de alguma forma nova.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N = 12
for tag in ("ppo_missao", "ppo_visao_v1"):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=16000)
    m = PPO.load(tag, device="cpu")
    vel, ys, acoes = [], [], Counter()
    ranks, progs, scores, duracoes, bolas = [], [], [], [], []
    for ep in range(N):
        obs, _ = env.reset(); term = trunc = False
        rmax = pmax = 0
        while not (term or trunc):
            a = int(m.predict(obs, deterministic=True)[0]); acoes[a] += 1
            obs, _, term, trunc, info = env.step(a)
            v = obs["vetor"]
            vel.append(float(v[4]) * 40.0); ys.append(float(v[1]) * 14.5)
            rmax = max(rmax, info["rank"]); pmax = max(pmax, info["progresso"])
        ranks.append(rmax); progs.append(pmax); scores.append(info["score"])
        duracoes.append(info["tempo_s"]); bolas.append(info["bolas_restantes"])
    vel = np.array(vel); ys = np.array(ys); n = sum(acoes.values())
    print(f"=== {tag} ===")
    print(f"  score mediano={np.median(scores):>10,.0f} duracao={np.mean(duracoes):.0f}s")
    print(f"  rank por episodio: {ranks}")
    print(f"  prog por episodio: {progs}")
    print(f"  bolas restantes ao fim: {Counter(bolas)}")
    print(f"  velocidade mediana={np.median(vel):.2f} | quase parada={100*(vel<2).mean():.1f}%")
    print(f"  no topo={100*(ys<-6).mean():.1f}% | no fundo={100*(ys>6).mean():.1f}%")
    nomes = ["nada","esq","dir","ambos"]
    print("  acoes: " + "  ".join(f"{nomes[k]}={100*acoes[k]/n:.0f}%" for k in range(4)))
    env.close()
