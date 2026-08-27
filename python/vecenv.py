"""Ambientes em paralelo.

O estado do jogo e' global no codigo original, entao so' cabe UMA instancia por
processo. DummyVecEnv (varios envs no mesmo processo) nao funciona aqui - tem
que ser SubprocVecEnv, um processo por ambiente.
"""
import os
import sys


def fabrica(rank: int, **kwargs):
    """Devolve uma funcao que cria o ambiente dentro do processo filho."""
    def cria():
        aqui = os.path.dirname(os.path.abspath(__file__))
        if aqui not in sys.path:
            sys.path.insert(0, aqui)
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        # cada processo usa 1 thread de BLAS: sao muitos processos competindo
        os.environ["OMP_NUM_THREADS"] = "1"
        from spacecadet_gym import SpaceCadetEnv
        env = SpaceCadetEnv(**kwargs)
        env.reset(seed=1000 + rank)
        return env
    return cria
