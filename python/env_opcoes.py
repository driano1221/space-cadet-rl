"""Espaco de acao por OPCOES: o agente escolhe quanto esperar, nao se aperta.

Ideia do Adriano. Duas coisas que isso resolve:

1. RESOLUCAO. No env normal ele decide de 75 em 75 ms e nao consegue expressar
   "aperta daqui a 50 ms". A curva de reacao mostra que e' exatamente nessa faixa
   que o desempenho desaba (1,55M a 0 ms contra 320k a 50 ms), ou seja, a jogada
   boa nao cabia no vocabulario dele. Aqui o passo interno e' de 1 quadro (25 ms)
   e a espera e' escolhida em multiplos disso.

2. CREDITO. Uma decisao, um resultado: os pontos ate' a bola voltar a' zona. Sem
   diluir entre 40 passos com gamma=0,995, que foi o gargalo diagnosticado.

A zona de gatilho vem de zona_flipper.json (celulas onde houve tacada real,
dilatadas). Nao e' retangulo: o formato real sao duas nuvens com o dreno no meio.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from spacecadet_gym import SpaceCadetEnv

# espera em quadros de 25 ms: 0, 25, 50, 75, 100, 150 ms
# A primeira varredura deu tacadas/decisao monotonicamente crescente ate' o
# ultimo valor testado (150 ms), sinal de que o otimo estava fora da faixa: a
# zona pega a bola bem antes do alcance da pa'. Faixa esticada ate' 500 ms, que
# ainda cabe na visita mediana de 625 ms.
# O jogo roda a 120 quadros/s, entao 1 quadro = 8,33 ms. A faixa anterior
# ([0,1,2,3,4,6] quadros) cobria apenas 0-50 ms - toda dentro do plato onde as
# esperas se equivalem, o que explica o agente nao ter calibrado nada.
# Varredura com politica fixa (n=100 por valor):
#     0ms 0,54 | 50ms 0,60 | 100ms 0,61 | 150ms 0,55 | 200ms 0,49
#   300ms 0,37 | 450ms 0,16   <- desaba, e os drenos sobem de 2 para 6
# A faixa nova cruza a borda do plato: ha' opcoes boas E opcoes ruins, que e'
# a condicao para existir calibragem.
ESPERAS = [0, 6, 12, 18, 24, 36]       # 0, 50, 100, 150, 200, 300 ms
PULSO = 4               # 100 ms de flipper erguido por tacada
MAX_ESPERA_ZONA = 1200  # quadros (30 s) sem a bola entrar na zona -> segue o jogo


class OpcoesFlipper(gym.Env):
    """Semi-MDP: cada step e' uma tacada inteira, nao um quadro."""

    metadata = {"render_modes": []}

    def __init__(self, caminho_zona: str = "", max_decisoes: int = 400,
                 compressao: str = "quadro", ao_avancar=None, **kwargs):
        super().__init__()
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analise")
        z = json.load(open(caminho_zona or os.path.join(base, "zona_flipper.json")))
        self.cel = z["celula"]
        self.zona = {l: {tuple(c) for c in cs} for l, cs in z["zonas"].items()}
        kwargs.setdefault("quadros_por_passo", 1)      # 25 ms de resolucao
        kwargs.setdefault("visao", True)
        kwargs.setdefault("max_passos", 288_000)
        self.env = SpaceCadetEnv(**kwargs)
        self.max_decisoes = max_decisoes
        # Como o score vira recompensa dentro de uma macro-acao:
        #   "quadro" - soma sqrt(ganho) de cada quadro (igual aos treinos
        #              anteriores, mantem a comparabilidade). Somar raizes nao e'
        #              a raiz da soma: 5 eventos de mil pontos valem 5,00 e um de
        #              cinco mil vale 2,24 - premia pontinho picado.
        #   "macro"  - aplica sqrt uma vez sobre o ganho TOTAL da tacada, tratando
        #              jogada grande e jogada picada pelo mesmo valor.
        if compressao not in ("quadro", "macro"):
            raise ValueError("compressao deve ser 'quadro' ou 'macro'")
        self.compressao = compressao
        # Chamado a cada QUADRO interno. Como uma decisao engloba varios quadros,
        # sem isto nao da' para gravar video do agente - o controle so' volta ao
        # chamador uma vez por tacada.
        self.ao_avancar = ao_avancar
        # 0 = nao apertar; 1..6 = apertar apos ESPERAS[i-1] quadros
        self.action_space = spaces.Discrete(1 + 2 * len(ESPERAS))
        self.observation_space = self.env.observation_space

    def _na_zona(self, info):
        """A bola esta' em alguma zona de tacada?

        As duas zonas se sobrepoem em ~60% (a bola desce pelo mesmo funil), e a
        versao antiga devolvia sempre "esq" por ser o primeiro da lista - o
        agente acionava a pa' errada na maior parte das entradas, o que o Adriano
        viu nos videos. A posicao tambem nao separa os lados (o melhor limiar em
        x acerta 56%, contra 50% de chute), entao QUAL flipper usar virou decisao
        do agente, nao do ambiente.
        """
        c = (info["tela_x"] // self.cel, info["tela_y"] // self.cel)
        return c in self.zona["esq"] or c in self.zona["dir"]

    def _avancar(self, esq=False, dir_=False):
        a = (1 if esq else 0) | (2 if dir_ else 0)
        obs, rec, term, trunc, info = self.env.step(a)
        self._score = info["score"]
        if self.ao_avancar is not None:
            self.ao_avancar(info, a)
        return obs, rec, term or trunc, info

    def _ate_a_zona(self):
        """Roda sem apertar ate' a bola entrar numa zona (ou o episodio acabar)."""
        rec = 0.0
        for _ in range(MAX_ESPERA_ZONA):
            if self._na_zona(self._info):
                return True, rec, False
            self._obs, r, fim, self._info = self._avancar()
            rec += r
            if fim:
                return False, rec, True
        return False, rec, False       # bola presa em algum lugar

    def reset(self, *, seed=None, options=None):
        self._obs, self._info = self.env.reset()
        self._score = self._info["score"]
        self._decisoes = 0
        _, _, fim = self._ate_a_zona()
        return self._obs, dict(self._info)

    def step(self, acao):
        acao = int(acao)
        rec = 0.0
        score_ini = self._info["score"]
        na_zona = self._na_zona(self._info)
        # acao 0 = nao apertar; 1..12 = (lado, espera) com lado = (acao-1) // 6
        lado = "esq" if (acao - 1) // len(ESPERAS) == 0 else "dir"
        espera = ESPERAS[(acao - 1) % len(ESPERAS)]

        if acao > 0 and na_zona:
            for _ in range(espera):                        # espera escolhida
                self._obs, r, fim, self._info = self._avancar()
                rec += r
                if fim:
                    return (self._obs, self._recompensa(rec, score_ini),
                            True, False, dict(self._info))
            for _ in range(PULSO):                         # a tacada
                self._obs, r, fim, self._info = self._avancar(
                    esq=(lado == "esq"), dir_=(lado == "dir"))
                rec += r
                if fim:
                    return (self._obs, self._recompensa(rec, score_ini),
                            True, False, dict(self._info))

        # sai da zona antes de contar a proxima visita como nova decisao
        for _ in range(MAX_ESPERA_ZONA):
            if not self._na_zona(self._info):
                break
            self._obs, r, fim, self._info = self._avancar()
            rec += r
            if fim:
                return (self._obs, self._recompensa(rec, score_ini),
                        True, False, dict(self._info))

        _, r, fim = self._ate_a_zona()
        rec += r
        self._decisoes += 1
        trunc = self._decisoes >= self.max_decisoes
        return self._obs, self._recompensa(rec, score_ini), fim, trunc, dict(self._info)

    def _recompensa(self, rec_somada, score_ini):
        """rec_somada ja' vem comprimida por quadro; em 'macro' e' descartada."""
        if self.compressao == "quadro":
            return rec_somada
        return float(np.sqrt(max(self._info["score"] - score_ini, 0) / 1000.0))

    def close(self):
        self.env.close()
