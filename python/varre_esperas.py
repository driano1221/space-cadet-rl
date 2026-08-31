"""Varre esperas numa faixa ampla, com politica fixa e lado aleatorio.

Duas correcoes desde a varredura anterior: (1) o jogo roda a 120 quadros/s, nao
40 - a faixa antiga era 0-50 ms, nao 0-150 ms; (2) o lado do flipper agora e'
escolhido, e nao mais sempre "esq" por bug de ordenacao.

O lado e' sorteado para isolar o efeito da ESPERA: se o desempenho mudar com
ela, ha' o que o RL calibrar; se nao, a resolucao temporal nao e' o gargalo.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import env_opcoes

MS = [0, 25, 50, 100, 150, 200, 300, 450]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
QUADRO_MS = 1000.0 / 120.0
rng = np.random.default_rng(7)

print(f"{N} decisoes por politica | 1 quadro = {QUADRO_MS:.2f} ms\n")
print(f"{'espera':>9} {'tacadas/dec':>12} {'pontos/dec':>12} {'drenos':>8}")

linhas = []
for ms in MS:
    q = int(round(ms / QUADRO_MS))
    env_opcoes.ESPERAS = [q] * 6          # todas as opcoes com a mesma espera
    from importlib import reload
    env = env_opcoes.OpcoesFlipper(max_decisoes=10_000)
    obs, info = env.reset()
    a0, s0, n, drenos = info["ev_flip_acerto"], info["score"], 0, 0
    tac, pts = [], []
    while n < N:
        # lado sorteado: acao 1 (esq) ou 7 (dir), ambas com a espera fixada
        acao = 1 if rng.random() < .5 else 7
        obs, _, term, trunc, info = env.step(acao)
        tac.append(info["ev_flip_acerto"] - a0); pts.append(info["score"] - s0)
        a0, s0 = info["ev_flip_acerto"], info["score"]
        n += 1
        if term or trunc:
            drenos += 1
            obs, info = env.reset(); a0, s0 = info["ev_flip_acerto"], info["score"]
    env.close()
    t, p = np.mean(tac), np.mean([x for x in pts if x >= 0])
    linhas.append((ms, t, p, drenos))
    print(f"{ms:>7} ms {t:>12.3f} {p:>12,.0f} {drenos:>8}")

melhor = max(linhas, key=lambda r: r[1])
pior = min(linhas, key=lambda r: r[1])
print(f"\nmelhor: {melhor[0]} ms ({melhor[1]:.3f} tacadas/dec)")
print(f"pior:   {pior[0]} ms ({pior[1]:.3f})")
if pior[1] > 0:
    print(f"razao melhor/pior: {melhor[1]/pior[1]:.2f}x")
print("faixa antiga ia so' ate' 50 ms" if melhor[0] > 50 else "o otimo cabia na faixa antiga")
