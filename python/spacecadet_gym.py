"""Ambiente Gymnasium para o 3D Pinball Space Cadet.

O jogo roda em uma thread propria dentro do processo, controlada passo a passo
pelo modulo C++ `spacecadet_env`.

LIMITE 1: ha' uma unica instancia do jogo por processo (o estado do jogo e'
global no codigo original). Para rodar ambientes em paralelo, use SubprocVecEnv,
que coloca cada ambiente em um processo separado - VecEnv em threads NAO
funciona aqui.

LIMITE 2: o ambiente e' ESTOCASTICO no reset. `seed` nao torna o estado inicial
reproduzivel, porque o jogo nao expoe um reset completo: `pb::replay_level` parte
do estado em que a partida anterior terminou, e a bola sai do canal do plunger em
momentos ligeiramente diferentes. A fisica em si e' deterministica - a mesma
sequencia de acoes a partir do mesmo estado da' o mesmo resultado -, mas o estado
inicial de cada episodio varia. Na pratica isso e' desejavel para RL, porque
evita que o agente decore um unico inicio; so' impede reprodutibilidade exata
episodio a episodio.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import gymnasium as gym
from gymnasium import spaces

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "SpaceCadetPinball", "bin")
if _BIN not in sys.path:
    sys.path.insert(0, os.path.abspath(_BIN))

import spacecadet_env as _core  # noqa: E402
from visao import Visao, GRADE_L, GRADE_A, N_CANAIS  # noqa: E402

# Limites observados em ~3,4 milhoes de passos de coleta.
_LIM = {"x": 7.5, "y": 14.5, "v": 40.0, "luzes": 40.0, "mult": 6.0, "rel_y": 28.0}


class SpaceCadetEnv(gym.Env):
    """Duas acoes binarias (flipper esquerdo e direito) -> 4 combinacoes."""

    metadata = {"render_modes": []}

    def __init__(self, quadros_por_passo: int = 6, max_passos: int = 12000,
                 recompensa: str = "score", base_path: str = "",
                 comprimir: bool = True, bonus_vivo: float = 0.0,
                 visao: bool = False):
        super().__init__()
        if recompensa not in ("score", "sobrevivencia"):
            raise ValueError("recompensa deve ser 'score' ou 'sobrevivencia'")
        self.quadros = quadros_por_passo
        self.max_passos = max_passos
        self.recompensa = recompensa
        # O ganho de score e' esparso (97% dos passos valem zero) e tem cauda
        # muito pesada (picos 25x o desvio). Sem comprimir a escala, o PPO
        # colapsa para a acao de menor variancia - ou seja, nunca apertar.
        self.comprimir = comprimir
        self.bonus_vivo = bonus_vivo

        self.action_space = spaces.Discrete(4)          # 00, 01, 10, 11
        self.usa_visao = visao
        if visao:
            # A grade da o layout da mesa (onde estao bumpers, alvos, luzes);
            # o vetor mantem os valores precisos que a grade quantiza.
            self.observation_space = spaces.Dict({
                "grade": spaces.Box(low=-1.0, high=1.0,
                                    shape=(N_CANAIS, GRADE_A, GRADE_L), dtype=np.float32),
                "vetor": spaces.Box(low=-1.0, high=1.0, shape=(15,), dtype=np.float32),
            })
        else:
            self.observation_space = spaces.Box(
                low=-1.0, high=1.0, shape=(15,), dtype=np.float32)

        if not _core.ativo():
            # O jogo procura o PINBALL.DAT primeiro no diretorio de trabalho.
            # Mudamos para a pasta do binario so' durante a inicializacao.
            anterior = os.getcwd()
            try:
                os.chdir(base_path or os.path.abspath(_BIN))
                ok = _core.iniciar("")
            finally:
                os.chdir(anterior)
            if not ok:
                raise RuntimeError(
                    "nao consegui iniciar a thread do jogo - confira se o "
                    f"PINBALL.DAT esta em {os.path.abspath(_BIN)}")
        self._score_ant = 0
        self._passos = 0
        self._visao = Visao(_core.inventario()) if visao else None

    def _observacao(self, e):
        vetor = self._obs(e)
        if not self.usa_visao:
            return vetor
        return {"grade": self._visao.montar(e, _core.luzes_acesas()), "vetor": vetor}

    @staticmethod
    def _obs(e) -> np.ndarray:
        return np.array([
            e.bola_x / _LIM["x"],
            e.bola_y / _LIM["y"],
            np.clip(e.bola_vx / _LIM["v"], -1, 1),
            np.clip(e.bola_vy / _LIM["v"], -1, 1),
            np.clip(e.bola_speed / _LIM["v"], -1, 1),
            e.bolas_restantes / 3.0,
            min(e.bolas_em_jogo, 3) / 3.0,
            min(e.luzes_acesas, _LIM["luzes"]) / _LIM["luzes"],
            min(e.multiplicador, _LIM["mult"]) / _LIM["mult"],
            # estado dos flippers: e' na pa' que o timing decide a tacada
            np.clip(e.flip_esq_ang, -1, 1),
            np.clip(e.flip_dir_ang, -1, 1),
            np.clip(e.bola_rel_esq_x / _LIM["x"], -1, 1),
            np.clip(e.bola_rel_esq_y / _LIM["rel_y"], -1, 1),
            np.clip(e.bola_rel_dir_x / _LIM["x"], -1, 1),
            np.clip(e.bola_rel_dir_y / _LIM["rel_y"], -1, 1),
        ], dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        e = _core.resetar()
        self._score_ant = e.score
        self._passos = 0
        return self._observacao(e), {"score": e.score}

    def step(self, action: int):
        esq = bool(action & 1)
        dir_ = bool(action & 2)
        e = _core.passo(esq, dir_, quadros=self.quadros)
        self._passos += 1

        ganho = e.score - self._score_ant
        self._score_ant = e.score

        if self.recompensa == "score":
            rec = np.sqrt(ganho / 1000.0) if self.comprimir else ganho / 1000.0
            rec += self.bonus_vivo
        else:
            # premia ficar vivo: a receita que induz o agente a travar os
            # flippers em vez de jogar
            rec = 0.01

        terminado = bool(e.fim)
        truncado = self._passos >= self.max_passos
        info = {"score": e.score, "tempo_s": e.tempo_s,
                "bolas_restantes": e.bolas_restantes}
        return self._observacao(e), float(rec), terminado, truncado, info

    def close(self):
        pass        # a thread do jogo vive enquanto o processo viver
