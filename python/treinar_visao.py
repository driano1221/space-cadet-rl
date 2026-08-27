"""Treino com visao da mesa (grade + CNN)."""
import sys, time, csv, json
sys.path.insert(0, '.')
import numpy as np
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
from spacecadet_gym import SpaceCadetEnv
from cnn import VisaoMesaExtractor
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

passos = int(sys.argv[1]) if len(sys.argv) > 1 else 600_000
tag = sys.argv[2] if len(sys.argv) > 2 else "visao"

base = SpaceCadetEnv(recompensa="score", max_passos=12000, comprimir=True,
                     bonus_vivo=0.0, quadros_por_passo=3, visao=True)
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
          f"dp={int(np.std(sc))} max={int(np.max(sc))} duracao={np.mean(du):.0f}s", flush=True)
    return sc, du

rng = np.random.default_rng(7)
print(f"dispositivo: {DEVICE}")
print(f"=== VISAO DA MESA | {passos} passos | grade 8x36x28 + CNN ===", flush=True)
print("ANTES:", flush=True)
sa, da = avaliar(lambda o: int(rng.integers(4)), 40, "aleatorio")

m = PPO("MultiInputPolicy", venv, verbose=0, n_steps=4096, batch_size=256,
        learning_rate=3e-4, ent_coef=0.01, gamma=0.995, seed=42, device=DEVICE,
        policy_kwargs=dict(features_extractor_class=VisaoMesaExtractor,
                           features_extractor_kwargs=dict(dim_saida=256),
                           normalize_images=False))
t0 = time.perf_counter()
m.learn(total_timesteps=passos)
dt = time.perf_counter() - t0
print(f"treino: {dt:.0f}s ({passos/dt:.0f} passos/s)", flush=True)

print("DEPOIS:", flush=True)
sd, dd = avaliar(lambda o: int(m.predict(o, deterministic=True)[0]), 40, "ppo")

with open(f"resultado_{tag}.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["fase", "score", "duracao"])
    for s, d in zip(sa, da): w.writerow(["antes", s, d])
    for s, d in zip(sd, dd): w.writerow(["depois", s, d])
m.save(f"ppo_{tag}")
json.dump({"mediana_antes": float(np.median(sa)), "mediana_depois": float(np.median(sd)),
           "duracao_antes": float(np.mean(da)), "duracao_depois": float(np.mean(dd)),
           "passos": passos, "treino_s": dt}, open(f"resumo_{tag}.json", "w"), indent=2)
print("salvo.", flush=True)
