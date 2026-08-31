"""Treina com decisao independente por flipper (MultiDiscrete([7,7])).

Uso: python treinar_duplo.py <decisoes> <tag> [n_envs]
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from cnn import VisaoMesaExtractor

DEVICE = os.environ.get("PINBALL_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")


def fabrica(rank):
    def cria():
        aqui = os.path.dirname(os.path.abspath(__file__))
        if aqui not in sys.path:
            sys.path.insert(0, aqui)
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        from env_opcoes2 import OpcoesDuplo
        return OpcoesDuplo(max_decisoes=400)
    return cria


def avaliar(escolher, n_ep=8):
    from env_opcoes2 import OpcoesDuplo, ESPERAS
    env = OpcoesDuplo(max_decisoes=10_000)
    sc, tac, usos = [], [], {"esq": 0, "dir": 0, "ambos": 0, "nada": 0}
    for _ in range(n_ep):
        obs, info = env.reset(); a0, n = info["ev_flip_acerto"], 0
        term = trunc = False
        while not (term or trunc):
            a = escolher(obs)
            e, d = int(a[0]) > 0, int(a[1]) > 0
            usos["ambos" if e and d else "esq" if e else "dir" if d else "nada"] += 1
            obs, _, term, trunc, info = env.step(a); n += 1
        sc.append(info["score"]); tac.append((info["ev_flip_acerto"] - a0) / max(n, 1))
    env.close()
    t = sum(usos.values())
    return (int(np.median(sc)), float(np.mean(tac)),
            "  ".join(f"{k}:{v/t:.0%}" for k, v in usos.items()))


if __name__ == "__main__":
    decisoes = int(sys.argv[1]) if len(sys.argv) > 1 else 45_000
    tag = sys.argv[2] if len(sys.argv) > 2 else "duplo"
    n_envs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    # gamma controla o alcance do credito. Com 0,95 o horizonte efetivo e' de 20
    # decisoes e os episodios tem ~13 - ou seja, quase sem desconto: uma tacada
    # ruim seguida de tres boas parece boa. Valores menores dao credito LOCAL,
    # que e' o que a ideia original pedia ("os pontos ate' voltar a' area").
    gamma = float(sys.argv[4]) if len(sys.argv) > 4 else 0.95
    print(f"=== DUPLO | {decisoes} decisoes | {n_envs} ambientes | "
          f"gamma={gamma} | {DEVICE} ===", flush=True)

    rng = np.random.default_rng(0)
    s, t, u = avaliar(lambda o: rng.integers(0, 7, size=2))
    print(f"ANTES (aleatorio): score {s:,}  tacadas/dec {t:.3f}  uso {u}", flush=True)

    venv = SubprocVecEnv([fabrica(i) for i in range(n_envs)])
    m = PPO("MultiInputPolicy", venv, verbose=0,
            policy_kwargs=dict(features_extractor_class=VisaoMesaExtractor,
                               features_extractor_kwargs=dict(dim_saida=256)),
            n_steps=256, batch_size=256, learning_rate=3e-4,
            # entropia mais alta que os treinos anteriores: com 49 combinacoes e
            # 45 mil decisoes, o risco e' colapsar cedo numa so' - foi o que
            # aconteceu com 13 acoes ("ESQ 100ms" em 100% das decisoes).
            ent_coef=0.03, gamma=gamma, n_epochs=4, seed=42, device=DEVICE)
    ckpt = CheckpointCallback(save_freq=max(10_000 // n_envs, 1),
                              save_path=os.path.join(os.path.dirname(__file__), "ckpt"),
                              name_prefix=tag)
    t0 = time.time()
    m.learn(total_timesteps=decisoes, callback=ckpt)
    print(f"treino: {time.time()-t0:.0f}s ({decisoes/(time.time()-t0):.1f} decisoes/s)", flush=True)
    m.save(f"ppo_{tag}"); venv.close()

    print("DEPOIS:", flush=True)
    for nome, det in (("det", True), ("estoc", False)):
        s, t, u = avaliar(lambda o: m.predict(o, deterministic=det)[0])
        print(f"  {nome:>5}: score {s:,}  tacadas/dec {t:.3f}  uso {u}", flush=True)
    print("salvo.", flush=True)
