"""Treino com as correcoes para recompensa esparsa de cauda pesada:
raiz no ganho, normalizacao da recompensa e entropia maior."""
import sys, time, csv, json
sys.path.insert(0, '.')
import numpy as np
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

recompensa = sys.argv[1] if len(sys.argv) > 1 else "score"
passos = int(sys.argv[2]) if len(sys.argv) > 2 else 400_000

base = SpaceCadetEnv(recompensa=recompensa, max_passos=12000,
                     comprimir=True, bonus_vivo=0.0, quadros_por_passo=3)
venv = VecNormalize(DummyVecEnv([lambda: base]), norm_obs=False,
                    norm_reward=True, clip_reward=10.0)

def avaliar(pol, n=40, rotulo=""):
    sc, du = [], []
    for _ in range(n):
        obs, _ = base.reset()
        term = trunc = False
        while not (term or trunc):
            obs, _, term, trunc, info = base.step(pol(obs))
        sc.append(info["score"]); du.append(info["tempo_s"])
    print(f"  {rotulo}: mediana={int(np.median(sc))} media={int(np.mean(sc))} "
          f"duracao={np.mean(du):.0f}s", flush=True)
    return sc, du

rng = np.random.default_rng(7)
print(f"=== {recompensa} | {passos} passos | raiz + normalizacao, quadros=3, observacao com flippers ===", flush=True)
print("ANTES:", flush=True)
sa, da = avaliar(lambda o: int(rng.integers(4)), 40, "aleatorio")

m = PPO("MlpPolicy", venv, verbose=0, n_steps=4096, batch_size=256,
        learning_rate=3e-4, ent_coef=0.01, gamma=0.995, seed=42, device="cpu")
t0 = time.perf_counter()
m.learn(total_timesteps=passos)
dt = time.perf_counter() - t0
print(f"treino: {dt:.0f}s ({passos/dt:.0f} passos/s)", flush=True)

print("DEPOIS:", flush=True)
sd, dd = avaliar(lambda o: int(m.predict(o, deterministic=True)[0]), 40, "ppo")

with open(f"resultado4_{recompensa}.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["fase", "score", "duracao"])
    for s, d in zip(sa, da): w.writerow(["antes", s, d])
    for s, d in zip(sd, dd): w.writerow(["depois", s, d])
m.save(f"ppo4_{recompensa}")
json.dump({"mediana_antes": float(np.median(sa)), "mediana_depois": float(np.median(sd)),
           "duracao_antes": float(np.mean(da)), "duracao_depois": float(np.mean(dd)),
           "passos": passos, "treino_s": dt},
          open(f"resumo4_{recompensa}.json", "w"), indent=2)
print("salvo.", flush=True)
