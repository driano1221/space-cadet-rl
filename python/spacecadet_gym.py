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

import json
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
                 atraso_ms: float = 0.0,
                 peso_medal: float = 0.0,
                 custo_flip: float = 0.0,
                 peso_acerto: float = 0.0,
                 mascara_zona: bool = False,
                 prever: bool = False,
                 peso_potencial: float = 0.0,
                 peso_novidade: float = 0.0,
                 bolas: int = 0):
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
        # Custo por ACIONAR o flipper (borda desligado->ligado). Sem ele o
        # flipper e' gratis e a politica otima e' apertar quase sempre:
        # medido 3,9 acionamentos/s e P(acionar) plana em 24 das 25 celulas
        # do mapa de posicao relativa. Nao penaliza segurar - trapping e'
        # tecnica legitima, o que custa e' iniciar a tacada.
        self.custo_flip = custo_flip
        self._flip_ant = (False, False)
        # Premia a TACADA, nao a economia de apertos. Vem do collisionFlag da
        # fisica do jogo: o flipper em movimento conectou com a bola. Como a
        # funcao so' roda com deltaAngle != 0, segurar a pa' erguida nunca
        # pontua - fecha a brecha que o custo por acionamento tinha aberto.
        # Medido no agente atual: 0,15 acerto/s (2,1x o acaso), 2% dos apertos.
        self.peso_acerto = peso_acerto
        self._acerto_ant = 0
        # Mascara de zona: a pa' so' responde com a bola na regiao em que ela
        # alcanca. Diferente do env de opcoes, aqui a decisao continua sendo a
        # cada passo - o agente ve a bola no momento em vez de prever onde ela
        # estara' daqui a 100 ms. A curva de reacao mostra que ele e' reativo,
        # nao preditivo: pedir antecipacao era pedir o que ele nao tem.
        self.mascara_zona = mascara_zona
        self._zona = None
        # Previsao de trajetoria como entrada, tecnica padrao em Pong/Breakout:
        # em vez de o agente ter de extrapolar sozinho, recebe pronto QUANDO e
        # ONDE a bola cruza a linha dos flippers. Medido: a extrapolacao linear
        # erra 4,5 px em 67 ms e 7,0 px em 100 ms - dentro do raio da bola, que
        # e' a janela em que a decisao de apertar ainda muda o resultado.
        self.prever = prever
        self._tela_ant = None
        # IDEIA 4 - shaping por potencial (Ng et al. 1999): F = gamma*P(s') - P(s).
        # Diferente de todo shaping que tentamos: esta forma e' PROVADAMENTE
        # incapaz de mudar a politica otima, so' acelera o aprendizado. O
        # potencial e' o rank (monotonico), nao o progresso (que zera a cada
        # promocao).
        self.peso_potencial = peso_potencial
        self._pot_ant = 0.0
        # IDEIA 2 - bonus por novidade: recompensa por atingir combinacoes
        # (rank, multiplicador) pouco visitadas. E' exploracao dirigida, nao
        # shaping de valor - o bonus cai com 1/sqrt(visitas).
        self.peso_novidade = peso_novidade
        self._visitas = {}
        # IDEIA 3 - curriculo de bolas. Tem de ser aplicado DENTRO de cada
        # processo: com SubprocVecEnv, chamar definir_bolas no pai nao chega
        # aos filhos, que rodam instancias proprias do jogo.
        if bolas:
            _core.definir_bolas(bolas)
        if mascara_zona:
            cam = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'analise', 'zona_flipper.json')
            z = json.load(open(cam))
            self._cel = z['celula']
            self._zona = {l: {tuple(c) for c in cs} for l, cs in z['zonas'].items()}
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
        # Medal targets: derrubar os 3 fecha um conjunto; TRES conjuntos dao
        # bola extra, sem limite. O agente faz ~2,4 conjuntos por partida - fica
        # a um de distancia. Premiamos alvo (denso) e conjunto (o que importa),
        # nunca a bola extra em si, que e' rara demais para guiar.
        self.peso_medal = peso_medal
        self._medal_ant = 0
        self._conj_ant = 0
        self._malvos_ant = 0
        self._mnivel_ant = 0
        self._prog_ant = 0
        self._rank_ant = 1

        self.action_space = spaces.Discrete(4)          # 00, 01, 10, 11
        self.usa_visao = visao
        # 3 campos a mais quando a previsao esta' ligada
        n_vetor = 15 + (3 if prever else 0)
        if visao:
            # A grade da o layout da mesa (onde estao bumpers, alvos, luzes);
            # o vetor mantem os valores precisos que a grade quantiza.
            self.observation_space = spaces.Dict({
                "grade": spaces.Box(low=-1.0, high=1.0,
                                    shape=(N_CANAIS, GRADE_A, GRADE_L), dtype=np.float32),
                "vetor": spaces.Box(low=-1.0, high=1.0, shape=(n_vetor,), dtype=np.float32),
            })
        else:
            self.observation_space = spaces.Box(
                low=-1.0, high=1.0, shape=(n_vetor,), dtype=np.float32)

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

    LINHA_FLIPPER = 369      # tela_y mediano das tacadas que conectaram

    def _prever_features(self, e):
        """quando e onde a bola cruza a linha dos flippers, por extrapolacao linear"""
        if self._tela_ant is None:
            return [0.0, 0.0, 0.0]
        vx = (e.tela_x - self._tela_ant[0]) / self.quadros     # px por quadro
        vy = (e.tela_y - self._tela_ant[1]) / self.quadros
        desce = 1.0 if vy > 0.05 else 0.0
        if vy <= 0.05:                                          # subindo ou parada
            return [1.0, 0.0, desce]
        q = (self.LINHA_FLIPPER - e.tela_y) / vy                # quadros ate' a linha
        if q < 0:                                               # ja' passou
            return [1.0, 0.0, desce]
        x_prev = e.tela_x + vx * q
        return [float(np.clip(q / 30.0, 0, 1)),                 # 1 = longe ou nunca
                float(np.clip((x_prev - 180.0) / 100.0, -1, 1)),
                desce]

    def _obs(self, e) -> np.ndarray:
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
        ] + (self._prever_features(e) if self.prever else []) + [
        ], dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        e = _core.resetar()
        self._score_ant = e.score
        self._flip_ant = (False, False)
        self._acerto_ant = e.ev_flip_acerto
        self._pot_ant = int(getattr(e, 'rank', 0)) / 9.0
        # zera os acumuladores de progressao junto com a partida
        self._prog_ant = int(getattr(e, "progresso", 0))
        self._rank_ant = int(getattr(e, "rank", 1))
        self._fila_acoes = []
        self._medal_ant = int(getattr(e, "ev_medal", 0))
        self._conj_ant = self._medal_ant // 3
        self._malvos_ant = int(getattr(e, "mult_alvos", 0))
        self._mnivel_ant = int(getattr(e, "multiplicador", 0))
        self._ev_ant = (int(getattr(e, "ev_mission_target", 0)),
                        int(getattr(e, "ev_launch_ramp", 0)),
                        int(getattr(e, "ev_missao_completa", 0)))
        self._passos = 0
        self._tela = (e.tela_x, e.tela_y)
        self._tela_ant = None
        return self._observacao(e), {"score": e.score, "tela_x": e.tela_x,
                                    "tela_y": e.tela_y,
                                    "ev_flip_acerto": e.ev_flip_acerto,
                                    "tempo_s": e.tempo_s,
                                    "rank": int(getattr(e, "rank", 1)),
                                    "progresso": int(getattr(e, "progresso", 0))}

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
        if self._zona is not None:
            cel = (self._tela[0] // self._cel, self._tela[1] // self._cel)
            esq = esq and cel in self._zona['esq']
            dir_ = dir_ and cel in self._zona['dir']
        e = _core.passo(esq, dir_, quadros=self.quadros)
        self._passos += 1
        self._tela_ant = self._tela if hasattr(self, '_tela') else None
        self._tela = (e.tela_x, e.tela_y)

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

        # --- medal targets -------------------------------------------------
        medal = int(getattr(e, "ev_medal", 0))
        rec_medal = 0.0
        if self.peso_medal and medal > self._medal_ant:
            rec_medal += self.peso_medal * (medal - self._medal_ant)
            # a cada 3 alvos um conjunto fecha; premia o conjunto a mais
            conj = medal // 3
            if conj > self._conj_ant:
                rec_medal += self.peso_medal * 4.0 * (conj - self._conj_ant)
                self._conj_ant = conj
        self._medal_ant = medal

        # so' bordas: paga quem inicia a tacada, nao quem segura a pa'
        bordas = (esq and not self._flip_ant[0]) + (dir_ and not self._flip_ant[1])
        rec_flip = -self.custo_flip * bordas
        acertos = e.ev_flip_acerto - self._acerto_ant
        self._acerto_ant = e.ev_flip_acerto
        rec_flip += self.peso_acerto * acertos
        self._flip_ant = (esq, dir_)

        rec_base = rec
        # potencial: rank normalizado, com gamma igual ao do treino
        rec_pot = 0.0
        if self.peso_potencial:
            pot = rank / 9.0
            # gamma=1 no shaping: com 0,995 e potencial constante o termo fica
            # negativo todo passo ((gamma-1)*P), penalizando durar - e durar e'
            # justamente o que pontua aqui. Telescopico puro soma P_fim - P_inicio.
            rec_pot = self.peso_potencial * (pot - self._pot_ant)
            self._pot_ant = pot
        # novidade: bonus decrescente por celula (rank, multiplicador)
        rec_nov = 0.0
        if self.peso_novidade:
            cel = (rank, int(getattr(e, "multiplicador", 1)))
            n = self._visitas.get(cel, 0) + 1
            self._visitas[cel] = n
            rec_nov = self.peso_novidade / np.sqrt(n)

        rec += rec_prog + rec_ev + rec_mult + rec_medal + rec_flip + rec_pot + rec_nov
        self._prog_ant, self._rank_ant = prog, rank

        terminado = bool(e.fim)
        truncado = self._passos >= self.max_passos
        info = {"score": e.score, "tempo_s": e.tempo_s,
                "rank": int(getattr(e, "rank", 1)),
                "progresso": int(getattr(e, "progresso", 0)),
                "ev_flip_acerto": e.ev_flip_acerto,
                "tela_x": e.tela_x, "tela_y": e.tela_y,
                "rank": rank, "progresso": prog,
                "multiplicador": int(getattr(e, "multiplicador", 0)),
                "mult_alvos": int(getattr(e, "mult_alvos", 0)),
                # eventos do fluxo de missao, acumulados no episodio
                "ev_mission_target": int(getattr(e, "ev_mission_target", 0)),
                "ev_launch_ramp": int(getattr(e, "ev_launch_ramp", 0)),
                "ev_missao_completa": int(getattr(e, "ev_missao_completa", 0)),
                # decomposicao da recompensa: e' o que revela captura do
                # objetivo por um termo secundario
                "bumpers": int(getattr(e, "ev_bumper", 0)),
                "hyperspace": int(getattr(e, "ev_hyperspace", 0)),
                "medal": int(getattr(e, "ev_medal", 0)),
                "bolas_extras": int(getattr(e, "bolas_extras", 0)),
                "extra_ganha": int(getattr(e, "ev_extra_ganha", 0)),
                "rec_base": rec_base, "rec_prog": rec_prog, "rec_ev": rec_ev,
                "rec_medal": rec_medal,
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
