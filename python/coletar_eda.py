"""Coleta trajetoria completa das politicas para EDA.
Grava um CSV por politica com o estado a cada decisao."""
import sys, csv
sys.path.insert(0, '.')
import numpy as np
from spacecadet_gym import SpaceCadetEnv
import spacecadet_env as core

QUADROS, N_EP = 3, 25

def heuristica(e, alcance=5.0):
    esq = (abs(e.bola_rel_esq_x) < alcance and -4.0 < e.bola_rel_esq_y < 0.5 and e.bola_vy > 0)
    dir_ = (abs(e.bola_rel_dir_x) < alcance and -4.0 < e.bola_rel_dir_y < 0.5 and e.bola_vy > 0)
    return esq, dir_

SpaceCadetEnv(quadros_por_passo=QUADROS)

def coleta(nome, politica, seed=11):
    rng = np.random.default_rng(seed)
    with open(f"eda_{nome}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["episodio", "passo", "tempo_s", "x", "y", "vx", "vy", "speed",
                    "score", "bolas_restantes", "luzes", "mult",
                    "acao_esq", "acao_dir", "flip_esq", "flip_dir",
                    "rel_esq_x", "rel_esq_y", "rel_dir_x", "rel_dir_y", "tela_x", "tela_y"])
        for ep in range(N_EP):
            e = core.resetar()
            passos, limite = 0, int(90000 / QUADROS)
            while not e.fim and passos < limite:
                a, b = (rng.random() < .3, rng.random() < .3) if politica == "aleatoria" else heuristica(e)
                a, b = bool(a), bool(b)
                e = core.passo(a, b, quadros=QUADROS)
                passos += 1
                if passos % 4 == 0:                     # 1 linha a cada 100 ms
                    w.writerow([ep, passos, round(e.tempo_s, 2),
                                round(e.bola_x, 4), round(e.bola_y, 4),
                                round(e.bola_vx, 4), round(e.bola_vy, 4), round(e.bola_speed, 4),
                                e.score, e.bolas_restantes, e.luzes_acesas, e.multiplicador,
                                int(a), int(b), round(e.flip_esq_ang, 3), round(e.flip_dir_ang, 3),
                                round(e.bola_rel_esq_x, 3), round(e.bola_rel_esq_y, 3),
                                round(e.bola_rel_dir_x, 3), round(e.bola_rel_dir_y, 3),
                                e.tela_x, e.tela_y])
            print(f"  {nome} ep{ep}: score={e.score} t={e.tempo_s:.0f}s", flush=True)

coleta("aleatoria", "aleatoria")
coleta("heuristica", "heuristica")
print("pronto")
