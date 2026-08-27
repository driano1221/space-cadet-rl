"""Mede o throughput com N ambientes em paralelo."""
import sys, time
sys.path.insert(0, '.')
import numpy as np
from stable_baselines3.common.vec_env import SubprocVecEnv
from vecenv import fabrica

if __name__ == "__main__":
    for n in (1, 2, 4, 6):
        venv = SubprocVecEnv([fabrica(i, quadros_por_passo=3, visao=True,
                                      max_passos=12000) for i in range(n)])
        venv.reset()
        t0 = time.perf_counter()
        PASSOS = 400
        for _ in range(PASSOS):
            venv.step(np.random.randint(0, 4, size=n))
        dt = time.perf_counter() - t0
        total = PASSOS * n
        print(f"  {n} ambientes: {total/dt:7.0f} passos/s  ({dt:.1f}s para {total} passos)", flush=True)
        venv.close()
