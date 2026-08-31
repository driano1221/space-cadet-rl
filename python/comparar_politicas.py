"""As duas politicas sao mesmo identicas, ou so' as trajetorias avaliadas coincidem?

A avaliacao e' deterministica: se ambas escolhem a mesma acao no estado inicial,
a trajetoria inteira se repete e os numeros saem iguais mesmo com redes
diferentes. O teste honesto e' passar os MESMOS estados - inclusive estados que
a avaliacao nunca visita - pelos dois modelos e comparar.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper, ESPERAS
from stable_baselines3 import PPO

N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
a = PPO.load("ppo_c9_opcoes", device="cpu")
b = PPO.load("ppo_c9_opcoes_macro", device="cpu")

# estados variados: politica ALEATORIA para visitar o que a avaliacao nao visita
env = OpcoesFlipper(max_decisoes=10_000)
rng = np.random.default_rng(0)
obs, _ = env.reset()
estados = []
while len(estados) < N:
    estados.append({k: v.copy() for k, v in obs.items()})
    obs, _, term, trunc, _ = env.step(int(rng.integers(0, 7)))
    if term or trunc:
        obs, _ = env.reset()
env.close()

lote = {k: np.stack([e[k] for e in estados]) for k in estados[0]}
aa = a.predict(lote, deterministic=True)[0]
bb = b.predict(lote, deterministic=True)[0]

print(f"n = {len(estados)} estados visitados por politica aleatoria")
print(f"acoes iguais: {(aa == bb).mean():.1%}")
for nome, x in (("quadro", aa), ("macro", bb)):
    d = np.bincount(x, minlength=7) / len(x)
    print(f"  {nome:>6}: " + "  ".join(
        f"{'nada' if i==0 else str(ESPERAS[i-1]*25)+'ms'}:{p:.0%}" for i, p in enumerate(d)))

# probabilidades, nao so' o argmax: redes diferentes podem concordar no topo
import torch
with torch.no_grad():
    t = {k: torch.as_tensor(v) for k, v in lote.items()}
    pa = a.policy.get_distribution(a.policy.obs_to_tensor(lote)[0]).distribution.probs.numpy()
    pb = b.policy.get_distribution(b.policy.obs_to_tensor(lote)[0]).distribution.probs.numpy()
print(f"\nprobabilidade media da acao escolhida:")
print(f"  quadro {pa.max(1).mean():.3f}   macro {pb.max(1).mean():.3f}")
print(f"  diferenca media entre as distribuicoes: {np.abs(pa - pb).mean():.4f}")
print(f"  -> {'redes distintas que concordam no argmax' if np.abs(pa-pb).mean() > 1e-4 else 'REDES PRATICAMENTE IGUAIS - suspeitar'}")
