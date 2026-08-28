"""Passo 9: o desempenho satura ou continua subindo com mais treino?

Salva checkpoints ao longo do caminho para medir a CURVA de aprendizado, nao
so' o ponto final. Os checkpoints sao avaliados depois, todos na mesma sessao -
a licao de que comparar avaliacoes separadas e' ler ruido.

Uso: python treinar_escala.py <passos_totais> <n_envs>
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback
from vecenv import fabrica
from cnn import VisaoMesaExtractor

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

if __name__ == "__main__":
    passos = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000_000
    n_envs = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    # 4 checkpoints: 25%, 50%, 75% e 100% do orcamento
    cada = passos // 4

    print(f"=== ESCALA | {passos:,} passos | {n_envs} ambientes | {DEVICE} ===", flush=True)
    print(f"checkpoints a cada {cada:,} passos", flush=True)

    venv = SubprocVecEnv([fabrica(i, quadros_por_passo=3, visao=True,
                                  max_passos=12000, comprimir=True,
                                  bonus_vivo=0.0) for i in range(n_envs)])
    venv = VecNormalize(venv, norm_obs=False, norm_reward=True, clip_reward=10.0)

    # configuracao identica a' do agente vencedor: so' a escala muda
    m = PPO("MultiInputPolicy", venv, verbose=0, n_steps=1024, batch_size=512,
            learning_rate=3e-4, ent_coef=0.01, gamma=0.995, n_epochs=4,
            seed=42, device=DEVICE,
            policy_kwargs=dict(features_extractor_class=VisaoMesaExtractor,
                               features_extractor_kwargs=dict(dim_saida=256),
                               normalize_images=False))

    cb = CheckpointCallback(save_freq=max(1, cada // n_envs),
                            save_path="./ckpt", name_prefix="escala")
    t0 = time.perf_counter()
    m.learn(total_timesteps=passos, callback=cb)
    dt = time.perf_counter() - t0
    print(f"treino: {dt:.0f}s ({passos/dt:.0f} passos/s)", flush=True)
    m.save("ppo_escala_final"); venv.close()
    print("checkpoints salvos em ./ckpt", flush=True)
    print("salvo.", flush=True)
