"""EDA do agente treinado. A assinatura do berco e' velocidade baixa e tempo
no fundo da mesa - aqui olhamos exatamente isso, a partir do vetor de
observacao (indice 4 = velocidade normalizada, indice 1 = y normalizado).
"""
import sys, csv, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP = 10
env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=24000)  # 600s
m = PPO.load("ppo_sobrevivencia", device="cpu")

resumo, vels, ys, acoes = [], [], [], []
for ep in range(N_EP):
    obs, _ = env.reset()
    term = trunc = False
    while not (term or trunc):
        a = int(m.predict(obs, deterministic=True)[0])
        obs, _, term, trunc, info = env.step(a)
        v = obs["vetor"]
        vels.append(float(v[4]) * 40.0)      # desnormaliza
        ys.append(float(v[1]) * 14.5)
        acoes.append(a)
    resumo.append((info["score"], info["tempo_s"], int(trunc)))
    print(f"  ep{ep}: score={info['score']:>9,} t={info['tempo_s']:6.0f}s "
          f"{'(TETO)' if trunc else ''}", flush=True)

sc = np.array([r[0] for r in resumo]); du = np.array([r[1] for r in resumo])
vels = np.array(vels); ys = np.array(ys); acoes = np.array(acoes)
print(f"\n=== TETO DE 600s ===")
print(f"  mediana={int(np.median(sc)):,}  max={int(sc.max()):,}")
print(f"  duracao media={du.mean():.0f}s  ainda no teto={sum(r[2] for r in resumo)}/{N_EP}")
print(f"  pontos/s={int((sc/du).mean()):,}")
print(f"\n=== TESTE DO BERCO ===")
print(f"  velocidade mediana={np.median(vels):.2f}  (berco=0,17 | aleatorio=9,49)")
print(f"  % quase parada (v<2)={100*(vels<2).mean():.1f}%  (berco=82,7% | aleatorio=10,9%)")
print(f"  % no topo (y<-6)={100*(ys<-6).mean():.1f}%  (berco=1,5% | aleatorio=20,7%)")
print(f"  % no fundo (y>6)={100*(ys>6).mean():.1f}%  (berco=97,6% | aleatorio=39,5%)")
nomes = ["nenhum","esq","dir","ambos"]
print(f"\n  acoes:", {nomes[i]: f"{100*(acoes==i).mean():.1f}%" for i in range(4)})
with open("agente_eda.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["score","duracao","truncado"]); w.writerows(resumo)
