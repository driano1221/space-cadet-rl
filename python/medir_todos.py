"""Mede TODOS os agentes na mesma condicao, para uma comparacao honesta.

Licao aprendida hoje: comparar numeros de avaliacoes diferentes e' ler ruido.
A variancia entre execucoes chega a 40% no mesmo agente. Aqui todos rodam com
o mesmo max_passos, o mesmo numero de episodios e na mesma sessao.
"""
import sys, os, csv, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import Counter
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

N_EP, MAX = 12, 8000          # 200 s de jogo por episodio

# (arquivo, rotulo, usa_visao, quadros)
AGENTES = [
    (None,                "Aleatorio",                    True,  3),
    ("ppo_score",         "1. score cru (50ms)",          False, 6),
    ("ppo2_score",        "2. + bonus sobrevivencia",     False, 6),
    ("ppo3_score",        "3. sem bonus",                 False, 6),
    ("ppo4_score",        "4. 25ms + flippers",           False, 3),
    ("ppo_visao_v1",      "5. VISAO DA MESA",             True,  3),
    ("ppo_sobrevivencia", "6. sobrevivencia pura",        True,  3),
    ("ppo_progressao",    "7. + progresso de rank",       True,  3),
    ("ppo_missao",        "8. + fluxo de missao",         True,  3),
]

linhas = []
for arq, rotulo, visao, quadros in AGENTES:
    try:
        env = SpaceCadetEnv(quadros_por_passo=quadros, visao=visao, max_passos=MAX)
        if arq:
            m = PPO.load(arq, device="cpu")
            pol = lambda o: int(m.predict(o, deterministic=True)[0])
        else:
            rng = np.random.default_rng(11)
            pol = lambda o: int(rng.integers(4))
        for ep in range(N_EP):
            obs, _ = env.reset(); term = trunc = False
            rmax = pmax = 0; vel = []; ys = []; ac = Counter(); n = 0
            while not (term or trunc):
                a = pol(obs); ac[a] += 1; n += 1
                obs, _, term, trunc, info = env.step(a)
                v = obs["vetor"] if isinstance(obs, dict) else obs
                vel.append(float(v[4]) * 40.0); ys.append(float(v[1]) * 14.5)
                rmax = max(rmax, info.get("rank", 0))
                pmax = max(pmax, info.get("progresso", 0))
            vel = np.array(vel); ys = np.array(ys)
            linhas.append(dict(
                agente=rotulo, ep=ep, score=info["score"], duracao=info["tempo_s"],
                rank=rmax, progresso=pmax,
                alvos=info.get("ev_mission_target", 0),
                missoes=info.get("ev_missao_completa", 0),
                bolas_sobrando=info["bolas_restantes"],
                vel_mediana=float(np.median(vel)),
                pct_parada=float(100 * (vel < 2).mean()),
                pct_topo=float(100 * (ys < -6).mean()),
                pct_ambos=float(100 * ac[3] / n), pct_nada=float(100 * ac[0] / n)))
        print(f"ok {rotulo}", flush=True)
        env.close()
    except Exception as ex:
        print(f"FALHOU {rotulo}: {type(ex).__name__}: {ex}", flush=True)

with open("comparacao_geral.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
print("salvo comparacao_geral.csv", len(linhas), "linhas")
