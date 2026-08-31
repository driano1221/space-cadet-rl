"""Treina no espaco de acao por opcoes (ideia do Adriano).

Cada decisao e' "quanto esperar antes da tacada", tomada quando a bola entra na
zona. Politica fixa ja' da' ~0,3 tacadas/decisao (13x o agente atual): o que o
treino testa e' se escolher a espera POR ESTADO - bola rapida x lenta - rende
mais do que qualquer valor fixo, e se as tacadas viram pontos.

Uso: python treinar_opcoes.py <decisoes> <tag> [n_envs]
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from cnn import VisaoMesaExtractor

DEVICE = os.environ.get("PINBALL_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")


def fabrica_opcoes(rank, compressao="quadro"):
    def cria():
        aqui = os.path.dirname(os.path.abspath(__file__))
        if aqui not in sys.path:
            sys.path.insert(0, aqui)
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        from env_opcoes import OpcoesFlipper
        return OpcoesFlipper(max_decisoes=400, compressao=compressao)
    return cria


def _rotulo(i):
    """1 quadro = 8,33 ms (o jogo roda a 120 fps) e as acoes 7..12 sao o lado direito."""
    from env_opcoes import ESPERAS
    lado = "E" if (i - 1) // len(ESPERAS) == 0 else "D"
    ms = round(ESPERAS[(i - 1) % len(ESPERAS)] * 1000 / 120)
    return f"{lado}{ms}ms"


def avaliar(modelo, n_ep=6):
    from env_opcoes import OpcoesFlipper, ESPERAS
    env = OpcoesFlipper(max_decisoes=10_000)   # avaliacao usa score bruto
    sc, tac, esc = [], [], []
    for _ in range(n_ep):
        obs, info = env.reset(); a0 = info["ev_flip_acerto"]; n = 0
        term = trunc = False
        while not (term or trunc):
            a = int(modelo.predict(obs, deterministic=True)[0]) if modelo else 0
            esc.append(a)
            obs, _, term, trunc, info = env.step(a); n += 1
        sc.append(info["score"]); tac.append((info["ev_flip_acerto"] - a0) / max(n, 1))
    env.close()
    d = np.bincount(esc, minlength=7) / max(len(esc), 1)
    return (int(np.median(sc)), float(np.mean(tac)),
            "  ".join(f"{'nada' if i==0 else _rotulo(i)}:{p:.0%}"
                      for i, p in enumerate(d)))


if __name__ == "__main__":
    decisoes = int(sys.argv[1]) if len(sys.argv) > 1 else 45_000
    tag = sys.argv[2] if len(sys.argv) > 2 else "opcoes"
    n_envs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    compressao = sys.argv[4] if len(sys.argv) > 4 else "quadro"
    print(f"=== OPCOES | {decisoes} decisoes | {n_envs} ambientes | "
          f"compressao={compressao} | {DEVICE} ===", flush=True)

    venv = SubprocVecEnv([fabrica_opcoes(i, compressao) for i in range(n_envs)])
    m = PPO("MultiInputPolicy", venv, verbose=0,
            policy_kwargs=dict(features_extractor_class=VisaoMesaExtractor,
                               features_extractor_kwargs=dict(dim_saida=256)),
            n_steps=256, batch_size=256, learning_rate=3e-4, ent_coef=0.01,
            # gamma menor: aqui cada passo JA' e' uma tacada inteira, entao o
            # horizonte em decisoes e' curto - 0,995 daria peso a 200 tacadas.
            gamma=0.95, n_epochs=4, seed=42, device=DEVICE)
    ckpt = CheckpointCallback(save_freq=max(10_000 // n_envs, 1),
                              save_path=os.path.join(os.path.dirname(__file__), "ckpt"),
                              name_prefix=tag)
    t0 = time.time()
    m.learn(total_timesteps=decisoes, callback=ckpt)
    print(f"treino: {time.time()-t0:.0f}s ({decisoes/(time.time()-t0):.1f} decisoes/s)", flush=True)
    m.save(f"ppo_{tag}"); venv.close()

    print("DEPOIS:", flush=True)
    s, t, dist = avaliar(m)
    print(f"  score mediano={s:,}  tacadas/decisao={t:.3f}", flush=True)
    print(f"  escolhas: {dist}", flush=True)
    print("salvo.", flush=True)
