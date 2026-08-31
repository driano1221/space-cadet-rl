"""Cada flipper com a sua propria zona e a sua propria decisao (ideia do Adriano).

Por que a versao anterior falhou: a acao era UMA escolha entre (lado, espera).
O agente aprendeu que o esquerdo rende mais que o direito (0,750 contra 0,458
com politica fixa) e colapsou em "ESQ 100ms" em 100% das decisoes - a pa'
direita nunca se movia, e a bola que descia por ali era perdida. Nos videos da'
para ver a bola passar pela direita sem resposta.

Nao adianta escolher o lado pela posicao: as zonas se sobrepoem ~60% (a bola
desce pelo mesmo funil) e o melhor limiar em x acerta 56,3% contra 50% de chute.

Aqui a acao e' MultiDiscrete([7, 7]): uma decisao independente por flipper,
cada uma "nao apertar" ou uma das 6 esperas. O agente pode acionar os dois com
tempos diferentes, um so', ou nenhum - e cada pa' so' responde se a bola estiver
na zona DELA. Sortear ja' batia qualquer lado fixo (0,808 contra 0,750 e 0,458),
entao ha' ganho real em usar os dois.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from spacecadet_gym import SpaceCadetEnv

ESPERAS = [0, 6, 12, 18, 24, 36]       # 0, 50, 100, 150, 200, 300 ms (120 fps)
PULSO = 12                              # 100 ms de pa' erguida
MAX_ESPERA_ZONA = 3600                  # 30 s sem a bola entrar em zona nenhuma


class OpcoesDuplo(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, caminho_zona: str = "", max_decisoes: int = 400,
                 compressao: str = "macro", ao_avancar=None, **kwargs):
        super().__init__()
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analise")
        z = json.load(open(caminho_zona or os.path.join(base, "zona_flipper.json")))
        self.cel = z["celula"]
        self.zona = {l: {tuple(c) for c in cs} for l, cs in z["zonas"].items()}
        kwargs.setdefault("quadros_por_passo", 1)
        kwargs.setdefault("visao", True)
        kwargs.setdefault("max_passos", 288_000)
        self.env = SpaceCadetEnv(**kwargs)
        self.max_decisoes = max_decisoes
        self.compressao = compressao
        self.ao_avancar = ao_avancar
        self.action_space = spaces.MultiDiscrete([1 + len(ESPERAS)] * 2)
        self.observation_space = self.env.observation_space

    def _celula(self, info):
        return (info["tela_x"] // self.cel, info["tela_y"] // self.cel)

    def _zonas_ativas(self, info):
        c = self._celula(info)
        return (c in self.zona["esq"], c in self.zona["dir"])

    def _avancar(self, esq=False, dir_=False):
        a = (1 if esq else 0) | (2 if dir_ else 0)
        obs, rec, term, trunc, info = self.env.step(a)
        if self.ao_avancar is not None:
            self.ao_avancar(info, a)
        return obs, rec, term or trunc, info

    def _ate_a_zona(self):
        rec = 0.0
        for _ in range(MAX_ESPERA_ZONA):
            if any(self._zonas_ativas(self._info)):
                return True, rec, False
            self._obs, r, fim, self._info = self._avancar()
            rec += r
            if fim:
                return False, rec, True
        return False, rec, False

    def _recompensa(self, rec_somada, score_ini):
        if self.compressao == "quadro":
            return rec_somada
        return float(np.sqrt(max(self._info["score"] - score_ini, 0) / 1000.0))

    def reset(self, *, seed=None, options=None):
        self._obs, self._info = self.env.reset()
        self._decisoes = 0
        self._ate_a_zona()
        return self._obs, dict(self._info)

    def step(self, acao):
        a_esq, a_dir = int(acao[0]), int(acao[1])
        rec = 0.0
        score_ini = self._info["score"]
        z_esq, z_dir = self._zonas_ativas(self._info)

        # cada pa' so' responde se a bola estiver na zona dela
        esp_e = ESPERAS[a_esq - 1] if (a_esq > 0 and z_esq) else None
        esp_d = ESPERAS[a_dir - 1] if (a_dir > 0 and z_dir) else None

        if esp_e is not None or esp_d is not None:
            # avanca quadro a quadro; cada flipper sobe quando o SEU tempo chega
            fim_e = (esp_e + PULSO) if esp_e is not None else -1
            fim_d = (esp_d + PULSO) if esp_d is not None else -1
            for t in range(max(fim_e, fim_d)):
                on_e = esp_e is not None and esp_e <= t < fim_e
                on_d = esp_d is not None and esp_d <= t < fim_d
                self._obs, r, fim, self._info = self._avancar(esq=on_e, dir_=on_d)
                rec += r
                if fim:
                    return (self._obs, self._recompensa(rec, score_ini),
                            True, False, dict(self._info))

        for _ in range(MAX_ESPERA_ZONA):          # sai da zona antes da proxima
            if not any(self._zonas_ativas(self._info)):
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
        return (self._obs, self._recompensa(rec, score_ini), fim, trunc, dict(self._info))

    def close(self):
        self.env.close()
