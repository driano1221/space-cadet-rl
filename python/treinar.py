"""Treina um agente PPO e mede contra o baseline aleatorio.

Uso: python treinar.py <recompensa> <passos>
  recompensa: 'score' ou 'sobrevivencia'
"""
import sys, time, csv, json
sys.path.insert(0, '.')
import numpy as np


def _saida(nome):
    """Resultados vao para analise/resultados/, nao para a pasta de scripts."""
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analise", "resultados")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, nome)
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

recompensa = sys.argv[1] if len(sys.argv) > 1 else "score"
passos = int(sys.argv[2]) if len(sys.argv) > 2 else 120_000

env = Monitor(SpaceCadetEnv(recompensa=recompensa, max_passos=6000))

def avaliar(politica, n=40, rotulo=""):
    """Devolve scores e duracoes de n episodios."""
    scores, duracoes = [], []
    for _ in range(n):
        obs, _ = env.reset()
        term = trunc = False
        while not (term or trunc):
            a = politica(obs)
            obs, _, term, trunc, info = env.step(a)
        scores.append(info["score"]); duracoes.append(info["tempo_s"])
    print(f"  {rotulo}: mediana={int(np.median(scores))} "
          f"media={int(np.mean(scores))} duracao={np.mean(duracoes):.0f}s", flush=True)
    return scores, duracoes

print(f"=== recompensa: {recompensa} | {passos} passos ===", flush=True)
rng = np.random.default_rng(7)
print("ANTES (politica aleatoria):", flush=True)
sc_antes, dur_antes = avaliar(lambda o: int(rng.integers(4)), 40, "aleatorio")

modelo = PPO("MlpPolicy", env, verbose=0, n_steps=2048, batch_size=256,
             learning_rate=3e-4, seed=42, device="cpu")
t0 = time.perf_counter()
modelo.learn(total_timesteps=passos, progress_bar=False)
treino_s = time.perf_counter() - t0
print(f"treino: {treino_s:.0f}s ({passos/treino_s:.0f} passos/s)", flush=True)

print("DEPOIS (PPO treinado):", flush=True)
sc_depois, dur_depois = avaliar(
    lambda o: int(modelo.predict(o, deterministic=True)[0]), 40, "ppo")

with open(_saida(f"resultado_{recompensa}.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["fase", "score", "duracao"])
    for s, d in zip(sc_antes, dur_antes): w.writerow(["antes", s, d])
    for s, d in zip(sc_depois, dur_depois): w.writerow(["depois", s, d])

modelo.save(f"ppo_{recompensa}")
json.dump({"recompensa": recompensa, "passos": passos, "treino_s": treino_s,
           "mediana_antes": float(np.median(sc_antes)),
           "mediana_depois": float(np.median(sc_depois)),
           "duracao_antes": float(np.mean(dur_antes)),
           "duracao_depois": float(np.mean(dur_depois))},
          open(_saida(f"resumo_{recompensa}.json"), "w"), indent=2)
print("salvo.", flush=True)
