"""Observacao em grade para o agente: a mesa vista como canais 2D.

O agente ate' agora recebia 15 numeros sobre bola e flippers, e nada sobre a
mesa - nao tinha como aprender a mirar num alvo que nao percebe. Aqui a mesa
vira uma grade com canais semanticos, no espirito do que se faz com CNN em
jogos: um canal por tipo de coisa, mais os canais dinamicos.

Canais:
  0 bola            (gaussiana na posicao, para dar gradiente espacial)
  1 velocidade x    (assinada, no ponto da bola)
  2 velocidade y
  3 bumpers         estatico
  4 alvos           estatico (popup + solo)
  5 rollovers       estatico
  6 luzes acesas    DINAMICO
  7 flippers        0,3 em repouso ate' 1,0 erguido (nunca zero, senao o
                    agente perde a referencia de onde eles ficam)
"""
from __future__ import annotations
import numpy as np

# A mesa tem 365x470 px. A grade preserva a proporcao.
GRADE_L, GRADE_A = 28, 36
MESA_L, MESA_A = 365, 470
N_CANAIS = 8

C_BOLA, C_VX, C_VY, C_BUMPER, C_ALVO, C_ROLLOVER, C_LUZ, C_FLIPPER = range(N_CANAIS)

_ESTATICOS = {
    "bumper": C_BUMPER,
    "alvo_popup": C_ALVO, "alvo_solo": C_ALVO,
    "rollover": C_ROLLOVER, "rollover_luz": C_ROLLOVER,
}


def _celula(tela_x, tela_y):
    """Pixel de tela -> celula da grade."""
    cx = int(np.clip(tela_x * GRADE_L / MESA_L, 0, GRADE_L - 1))
    cy = int(np.clip(tela_y * GRADE_A / MESA_A, 0, GRADE_A - 1))
    return cx, cy


class Visao:
    """Monta a grade. Os canais estaticos sao calculados uma vez."""

    def __init__(self, inventario):
        self.base = np.zeros((N_CANAIS, GRADE_A, GRADE_L), dtype=np.float32)
        self.luzes = []      # (celula_x, celula_y) de cada luz, na ordem do C++
        self.flippers = []

        for p in inventario:
            if not p.tem_sprite:
                continue
            cx, cy = _celula(p.tela_x, p.tela_y)
            canal = _ESTATICOS.get(p.tipo)
            if canal is not None:
                # marca a area do sprite, nao so' o centro
                lx = max(1, int(p.larg * GRADE_L / MESA_L))
                ly = max(1, int(p.alt * GRADE_A / MESA_A))
                x0, y0 = max(0, cx - lx // 2), max(0, cy - ly // 2)
                self.base[canal, y0:y0 + ly, x0:x0 + lx] = 1.0
            if p.tipo == "flipper":
                self.flippers.append((cx, cy))

        # a ordem das luzes no inventario e' a mesma de luzes_acesas()
        for p in inventario:
            if p.tipo in ("luz", "rollover_luz"):
                if p.tem_sprite:
                    self.luzes.append(_celula(p.tela_x, p.tela_y))
                else:
                    self.luzes.append(None)

    def montar(self, e, luzes_estado):
        """e = Estado do jogo; luzes_estado = lista 0/1 vinda do C++."""
        g = self.base.copy()

        # bola: gaussiana 3x3 para dar gradiente em vez de um ponto isolado
        if e.tela_x >= 0:
            cx, cy = _celula(e.tela_x, e.tela_y)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    y, x = cy + dy, cx + dx
                    if 0 <= y < GRADE_A and 0 <= x < GRADE_L:
                        g[C_BOLA, y, x] = 1.0 if (dx or dy) == 0 else 0.45
            g[C_VX, cy, cx] = np.clip(e.bola_vx / 40.0, -1, 1)
            g[C_VY, cy, cx] = np.clip(e.bola_vy / 40.0, -1, 1)

        # luzes acesas
        n = min(len(luzes_estado), len(self.luzes))
        for i in range(n):
            cel = self.luzes[i]
            if cel is not None and luzes_estado[i]:
                g[C_LUZ, cel[1], cel[0]] = 1.0

        # Flippers: base 0,3 quando soltos e 1,0 quando erguidos. Com valor
        # puro do angulo, o canal ficava zerado com os flippers em repouso e o
        # agente nem sabia onde eles estavam.
        for (cx, cy), ang in zip(self.flippers, (e.flip_esq_ang, e.flip_dir_ang)):
            g[C_FLIPPER, cy, cx] = 0.3 + 0.7 * float(np.clip(ang, 0, 1))

        return g
