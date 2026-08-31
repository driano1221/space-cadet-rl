"""Reavalia os agentes de opcoes com politica ESTOCASTICA.

A avaliacao anterior usava deterministic=True, que sempre escolhe o topo de uma
distribuicao quase uniforme (confianca media 0,22-0,34 com 7 acoes) - ou seja,
media uma politica degenerada que a rede nao aprendeu. Amostrando da
distribuicao, os clipes deram 13x mais pontos, entao o numero anterior
subestimava o agente.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from env_opcoes import OpcoesFlipper, ESPERAS
from stable_baselines3 import PPO
try:
    from scipy import stats
except ImportError:
    stats = None

N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 10
res = {}
for tag in ("ppo_c9_opcoes", "ppo_c9_opcoes_macro"):
    for det in (True, False):
        env = OpcoesFlipper(max_decisoes=10_000)
        m = PPO.load(tag, device="cpu")
        sc, tac, esc = [], [], []
        for _ in range(N_EP):
            obs, info = env.reset(); a0 = info["ev_flip_acerto"]; n = 0
            term = trunc = False
            while not (term or trunc):
                a = int(m.predict(obs, deterministic=det)[0]); esc.append(a)
                obs, _, term, trunc, info = env.step(a); n += 1
            sc.append(info["score"]); tac.append((info["ev_flip_acerto"] - a0) / max(n, 1))
        env.close()
        nome = f"{tag.replace('ppo_c9_','')} {'det' if det else 'estoc'}"
        res[nome] = np.array(sc)
        d = np.bincount(esc, minlength=7) / max(len(esc), 1)
        print(f"{nome:>18}: score mediano {int(np.median(sc)):>9,}  "
              f"max {int(max(sc)):>9,}  tacadas/dec {np.mean(tac):.3f}")
        print(f"{'':>18}  escolhas " + " ".join(
            f"{'nada' if i==0 else str(ESPERAS[i-1]*25)}:{p:.0%}" for i, p in enumerate(d)))

print("\n=== estocastico vs deterministico ===")
for tag in ("opcoes", "opcoes_macro"):
    a, b = res[f"{tag} det"], res[f"{tag} estoc"]
    p = stats.mannwhitneyu(a, b).pvalue if stats else float("nan")
    print(f"  {tag:>14}: {int(np.median(a)):>9,} -> {int(np.median(b)):>9,}  "
          f"({np.median(b)/max(np.median(a),1):.1f}x)  p={p:.4f}")
print(f"\n  referencia ppo_c9_base (10 ep, sem mascara): 2,637,750")
