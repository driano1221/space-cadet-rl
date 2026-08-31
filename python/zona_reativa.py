"""Zona para decisao CONTINUA: cobre o trajeto em que a pa' ainda alcanca a bola.

A zona do env de opcoes era um gatilho - bastava a bola passar por ali uma vez
por visita, e ela ficava liberada 0,3% dos passos. Para o agente decidir a cada
25 ms, isso o deixa sem acao em 99% dos passos.

Aqui a zona e' dilatada ate' cobrir uma fracao alvo do tempo, medida no jogo. O
criterio nao e' estetico: precisa ser grande o bastante para haver decisao real,
e pequena o bastante para o spam continuar impossivel fora do alcance.
"""
import sys, os, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

CEL = 10
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analise")
linhas = list(csv.DictReader(open(os.path.join(BASE, "tacadas_tela.csv"), encoding="utf-8")))
tac = [(int(r["tela_x"]), int(r["tela_y"]), r["lado"]) for r in linhas if r["acertou"] == "1"]

def construir(min_tac, dilatacoes):
    z = {}
    for lado in ("esq", "dir"):
        pts = [(x, y) for x, y, l in tac if l == lado]
        cont = {}
        for x, y in pts:
            cont[(x // CEL, y // CEL)] = cont.get((x // CEL, y // CEL), 0) + 1
        cel = {c for c, n in cont.items() if n >= min_tac}
        for _ in range(dilatacoes):
            nova = set()
            for cx, cy in cel:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nova.add((cx + dx, cy + dy))
            cel = nova
        z[lado] = cel
    return z

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000)
m = PPO.load("ppo_c9_base", device="cpu")
obs, info = env.reset()
trilha = []
for _ in range(3000):
    obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
    trilha.append((info["tela_x"] // CEL, info["tela_y"] // CEL))
    if term or trunc:
        obs, info = env.reset()
env.close()

print(f"{'min_tac':>8} {'dilat':>6} {'celulas':>9} {'cobre tacadas':>14} {'tempo na zona':>14}")
melhor = None
for min_tac, dil in [(6, 0), (6, 1), (6, 2), (2, 2), (2, 3), (1, 3)]:
    z = construir(min_tac, dil)
    cob = np.mean([(x // CEL, y // CEL) in z[l] for x, y, l in tac])
    tempo = np.mean([c in z["esq"] or c in z["dir"] for c in trilha])
    n = len(z["esq"]) + len(z["dir"])
    print(f"{min_tac:>8} {dil:>6} {n:>9} {cob:>13.1%} {tempo:>13.1%}")
    # alvo: cobrir quase toda tacada e liberar entre 5% e 20% do tempo
    if cob > .95 and .05 <= tempo <= .20 and melhor is None:
        melhor = (min_tac, dil, z, cob, tempo)

if melhor:
    min_tac, dil, z, cob, tempo = melhor
    json.dump({"celula": CEL, "zonas": {l: sorted(map(list, c)) for l, c in z.items()}},
              open(os.path.join(BASE, "zona_reativa.json"), "w"))
    print(f"\nescolhida: min_tac={min_tac} dilatacoes={dil} -> "
          f"cobre {cob:.1%} das tacadas, libera {tempo:.1%} do tempo")
    print("gravada em zona_reativa.json")
else:
    print("\nnenhuma combinacao caiu na faixa alvo")
