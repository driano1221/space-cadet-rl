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
                 visao: bool = False,
                 peso_progresso: float = 0.0, peso_rank: float = 0.0,
                 peso_alvo: float = 0.0, peso_rampa: float = 0.0,
                 peso_missao: float = 0.0,
                 peso_mult_alvo: float = 0.0, peso_mult_nivel: float = 0.0,
                 atraso_ms: float = 0.0):
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
        # Recompensa por progressao. As luzes de progresso sao o sinal denso
        # (o agente ja acende ~11,5 das 18 por partida); a missao completa e'
        # rara demais para treinar em cima sozinha.
        self.peso_progresso = peso_progresso
        self.peso_rank = peso_rank
        # Fluxo de missao. Os pesos crescem com a raridade do evento, mas quem
        # guia o aprendizado e' o mission_target (13,7 por partida); rampa
        # (3,5) e missao completa (0,7) sao raros demais para carregar sozinhos.
        self.peso_alvo = peso_alvo
        self.peso_rampa = peso_rampa
        self.peso_missao = peso_missao
        self._ev_ant = (0, 0, 0)
        # Multiplicador: tres alvos fecham uma trinca e sobem um nivel, mas o
        # nivel cai sozinho a cada 30 s. Por isso a trinca vale MAIS que os
        # tres alvos somados - e' o premio por completar, nao por acertar.
        self.peso_mult_alvo = peso_mult_alvo
        self.peso_mult_nivel = peso_mult_nivel
        # Atraso de reacao: a acao decidida agora so' chega ao jogo depois de
        # `atraso_ms`. Um humano tem 200-300 ms; o agente tem 0. Serve para
        # medir quanto do desempenho vem de reflexo e quanto de estrategia.
        ms_por_passo = quadros_por_passo * 1000.0 / 120.0
        self.atraso_passos = int(round(atraso_ms / ms_por_passo))
        self._fila_acoes = []
        self._malvos_ant = 0
        self._mnivel_ant = 0
        self._prog_ant = 0
        self._rank_ant = 1

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
        # zera os acumuladores de progressao junto com a partida
        self._prog_ant = int(getattr(e, "progresso", 0))
        self._rank_ant = int(getattr(e, "rank", 1))
        self._fila_acoes = []
        self._malvos_ant = int(getattr(e, "mult_alvos", 0))
        self._mnivel_ant = int(getattr(e, "multiplicador", 0))
        self._ev_ant = (int(getattr(e, "ev_mission_target", 0)),
                        int(getattr(e, "ev_launch_ramp", 0)),
                        int(getattr(e, "ev_missao_completa", 0)))
        self._passos = 0
        return self._observacao(e), {"score": e.score}

    def step(self, action: int):
        # Com atraso, a acao decidida agora entra numa fila e so' e' aplicada
        # depois de N passos; enquanto a fila nao enche, o jogo repete a acao
        # mais antiga disponivel (equivalente a "ainda nao reagiu").
        if self.atraso_passos > 0:
            self._fila_acoes.append(action)
            aplicada = self._fila_acoes.pop(0) if len(self._fila_acoes) > self.atraso_passos else 0
        else:
            aplicada = action
        esq = bool(aplicada & 1)
        dir_ = bool(aplicada & 2)
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

        # --- progressao -------------------------------------------------
        # Cada luz de progresso acesa vale `peso_progresso`; cada rank novo,
        # `peso_rank`. Ao subir de rank as luzes zeram, entao o delta e'
        # ignorado quando negativo, senao a subida viraria punicao.
        prog = int(getattr(e, "progresso", 0))
        rank = int(getattr(e, "rank", 1))
        rec_prog = 0.0
        if self.peso_progresso:
            d = prog - self._prog_ant
            if d > 0:
                rec_prog += self.peso_progresso * d
        if self.peso_rank and rank > self._rank_ant:
            rec_prog += self.peso_rank * (rank - self._rank_ant)
        # --- fluxo de missao: premia os passos intermediarios -----------
        ev = (int(getattr(e, "ev_mission_target", 0)),
              int(getattr(e, "ev_launch_ramp", 0)),
              int(getattr(e, "ev_missao_completa", 0)))
        pesos = (self.peso_alvo, self.peso_rampa, self.peso_missao)
        rec_ev = 0.0
        for atual, ant, peso in zip(ev, self._ev_ant, pesos):
            if peso and atual > ant:
                rec_ev += peso * (atual - ant)
        self._ev_ant = ev

        # --- multiplicador ------------------------------------------------
        malvos = int(getattr(e, "mult_alvos", 0))
        mnivel = int(getattr(e, "multiplicador", 0))
        rec_mult = 0.0
        if self.peso_mult_alvo and malvos > self._malvos_ant:
            rec_mult += self.peso_mult_alvo * (malvos - self._malvos_ant)
        if self.peso_mult_nivel and mnivel > self._mnivel_ant:
            # Progressiva: 1x->2x e' facil e frequente; 3x->5x e' onde esta o
            # valor e quase nunca acontece. Peso plano fazia o agente farmar a
            # primeira trinca e parar. Multiplicadores 0,5 / 1 / 2 / 4.
            escala = (0.5, 1.0, 2.0, 4.0)
            for nv in range(self._mnivel_ant + 1, mnivel + 1):
                rec_mult += self.peso_mult_nivel * escala[min(nv - 1, 3)]
        self._malvos_ant, self._mnivel_ant = malvos, mnivel

        rec_base = rec
        rec += rec_prog + rec_ev + rec_mult
        self._prog_ant, self._rank_ant = prog, rank

        terminado = bool(e.fim)
        truncado = self._passos >= self.max_passos
        info = {"score": e.score, "tempo_s": e.tempo_s,
                "rank": rank, "progresso": prog,
                "multiplicador": int(getattr(e, "multiplicador", 0)),
                "mult_alvos": int(getattr(e, "mult_alvos", 0)),
                # eventos do fluxo de missao, acumulados no episodio
                "ev_mission_target": int(getattr(e, "ev_mission_target", 0)),
                "ev_launch_ramp": int(getattr(e, "ev_launch_ramp", 0)),
                "ev_missao_completa": int(getattr(e, "ev_missao_completa", 0)),
                # decomposicao da recompensa: e' o que revela captura do
                # objetivo por um termo secundario
                "rec_base": rec_base, "rec_prog": rec_prog, "rec_ev": rec_ev,
                "rec_mult": rec_mult,
                "bolas_restantes": e.bolas_restantes,
                # posicao em pixels, para render externo (animacoes)
                "tela_x": e.tela_x, "tela_y": e.tela_y,
                "speed": e.bola_speed,
                # progressao: rank, avanco no rank e combustivel
                "rank": e.rank, "rank_total": e.rank_total,
                "progresso": e.progresso, "progresso_total": e.progresso_total,
                "combustivel": e.combustivel}
        return self._observacao(e), float(rec), terminado, truncado, info

    def capturar(self):
        """Quadro atual do jogo como array RGB (altura, largura, 3).
        E' o framebuffer real: inclui flippers, luzes e sprites."""
        return _core.capturar_tela()

    def close(self):
        pass        # a thread do jogo vive enquanto o processo viver
