"""Treino com visao da mesa, ambientes em paralelo e CNN na GPU.

Uso: python treinar_visao_par.py <passos> <tag> [n_envs]
"""
import sys, time, csv, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from vecenv import fabrica
from cnn import VisaoMesaExtractor

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def avaliar(politica, n=40, rotulo=""):
    """Avalia em um ambiente proprio, fora do vetorizado."""
    from spacecadet_gym import SpaceCadetEnv
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    sc, du, rk, pg = [], [], [], []
    ev_alvo, ev_miss = [], []
    for _ in range(n):
        obs, _ = env.reset()
        term = trunc = False
        rmax = pmax = 0
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(politica(obs))
            rmax = max(rmax, info.get("rank", 0))
            pmax = max(pmax, info.get("progresso", 0))
        sc.append(info["score"]); du.append(info["tempo_s"])
        rk.append(rmax); pg.append(pmax)
        ev_alvo.append(info.get("ev_mission_target", 0))
        ev_miss.append(info.get("ev_missao_completa", 0))
    print(f"  {rotulo}: mediana={int(np.median(sc))} media={int(np.mean(sc))} "
          f"dp={int(np.std(sc))} min={int(np.min(sc))} max={int(np.max(sc))} "
          f"duracao={np.mean(du):.0f}s rank={np.mean(rk):.1f}/9 "
          f"prog={np.mean(pg):.1f}/18 alvos={np.mean(ev_alvo):.1f} "
          f"missoes={np.mean(ev_miss):.1f}", flush=True)
    return sc, du


if __name__ == "__main__":
    passos = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    tag = sys.argv[2] if len(sys.argv) > 2 else "visao"
    n_envs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    recompensa = sys.argv[4] if len(sys.argv) > 4 else "score"
    # Peso da progressao. Calibrado para ~25% da recompensa total: forte o
    # bastante para guiar, longe do que capturaria o objetivo (o bonus de 0,02
    # chegou a 93% e o agente parou de jogar).
    peso_prog = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
    # Fluxo de missao. Pesos calibrados pela decomposicao real da recompensa
    # para ~20% do total: o mission_target (13,7 eventos por partida) e' quem
    # guia; rampa e missao completa sao raros e entram com peso maior so' para
    # nao sumirem na soma.
    peso_alvo = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
    peso_mult = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0

    print(f"=== VISAO | recompensa={recompensa} | {passos} passos | "
          f"{n_envs} ambientes | peso_prog={peso_prog} peso_alvo={peso_alvo} "
          f"| {DEVICE} ===", flush=True)
    rng = np.random.default_rng(7)
    print("ANTES:", flush=True)
    sa, da = avaliar(lambda o: int(rng.integers(4)), 40, "aleatorio")

    venv = SubprocVecEnv([fabrica(i, quadros_por_passo=3, visao=True,
                                  max_passos=12000, comprimir=True,
                                  bonus_vivo=0.0, recompensa=recompensa,
                                  peso_progresso=peso_prog,
                                  peso_rank=peso_prog * 5,
                                  peso_alvo=peso_alvo,
                                  peso_rampa=peso_alvo * 4,
                                  peso_missao=peso_alvo * 20,
                                  peso_mult_alvo=peso_mult,
                                  peso_mult_nivel=peso_mult * 4)
                          for i in range(n_envs)])
    venv = VecNormalize(venv, norm_obs=False, norm_reward=True, clip_reward=10.0)

    m = PPO("MultiInputPolicy", venv, verbose=0, n_steps=1024, batch_size=512,
            learning_rate=3e-4, ent_coef=0.01, gamma=0.995, n_epochs=4,
            seed=42, device=DEVICE,
            policy_kwargs=dict(features_extractor_class=VisaoMesaExtractor,
                               features_extractor_kwargs=dict(dim_saida=256),
                               normalize_images=False))
    t0 = time.perf_counter()
    m.learn(total_timesteps=passos)
    dt = time.perf_counter() - t0
    print(f"treino: {dt:.0f}s ({passos/dt:.0f} passos/s)", flush=True)
    m.save(f"ppo_{tag}"); venv.close()

    print("DEPOIS:", flush=True)
    sd, dd = avaliar(lambda o: int(m.predict(o, deterministic=True)[0]), 40, "ppo")

    with open(f"resultado_{tag}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["fase", "score", "duracao"])
        for s, d in zip(sa, da): w.writerow(["antes", s, d])
        for s, d in zip(sd, dd): w.writerow(["depois", s, d])
    json.dump({"mediana_antes": float(np.median(sa)), "mediana_depois": float(np.median(sd)),
               "duracao_antes": float(np.mean(da)), "duracao_depois": float(np.mean(dd)),
               "passos": passos, "treino_s": dt, "n_envs": n_envs},
              open(f"resumo_{tag}.json", "w"), indent=2)
    print("salvo.", flush=True)
