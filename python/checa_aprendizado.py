"""Como o aprendizado esta' configurado de fato: inicializacao, desconto, sinal.

Confere tres coisas:
  1. no inicio, as jogadas tem mesma probabilidade?
  2. qual o horizonte efetivo do gamma, comparado ao tamanho do episodio?
  3. o sinal e' "pontos positivos = bom" ou "melhor que o esperado = bom"?
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
from stable_baselines3 import PPO
from env_opcoes2 import OpcoesDuplo, ESPERAS
from cnn import VisaoMesaExtractor

env = OpcoesDuplo(max_decisoes=400)
m = PPO("MultiInputPolicy", env, verbose=0, gamma=0.95, ent_coef=0.03,
        policy_kwargs=dict(features_extractor_class=VisaoMesaExtractor,
                           features_extractor_kwargs=dict(dim_saida=256)),
        seed=42, device="cpu")
obs, _ = env.reset()
lote = {k: np.stack([v] * 32) for k, v in obs.items()}
with torch.no_grad():
    dist = m.policy.get_distribution(m.policy.obs_to_tensor(lote)[0])
    probs = [d.probs.numpy()[0] for d in dist.distribution]
env.close()

print("1. probabilidade de cada jogada numa rede NOVA (flipper esquerdo):")
rot = ["nada"] + [f"{round(e*1000/120)}ms" for e in ESPERAS]
for r, p in zip(rot, probs[0]):
    print(f"     {r:>7}: {p:.3f}")
print(f"   uniforme seria {1/7:.3f} | desvio maximo {np.abs(probs[0]-1/7).max():.3f}")

g = 0.95
print(f"\n2. desconto gamma = {g}")
print(f"   horizonte efetivo 1/(1-gamma) = {1/(1-g):.0f} decisoes")
print(f"   peso da decisao +5: {g**5:.2f} | +10: {g**10:.2f} | +20: {g**20:.2f}")
print(f"   episodios medidos tem ~13 decisoes -> quase SEM desconto dentro do episodio")
