"""Constroi a zona de gatilho a partir das tacadas reais e mede se ela e' usavel.

Nao usa retangulo: o formato real sao DUAS nuvens com um vao no meio, e o vao e'
o dreno - um retangulo unico liberaria o flipper exatamente onde ele e' inutil.
A zona vira uma grade de celulas marcadas onde houve tacada, dilatada em uma
celula para dar margem de antecipacao.

Gera zona_flipper.json e mede quantos quadros a bola passa dentro por visita.
"""
import sys, os, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

CEL = 10            # lado da celula em pixels
# Com MIN_TAC=2 e dilatacao, a zona ficou grande e a bola entrava pela borda de
# cima levando ~1 s ate' o alcance da pa' - a espera otima saiu em 1000 ms, o
# que denuncia gatilho cedo demais. Aqui so' o NUCLEO denso, sem dilatar.
MIN_TAC = 6         # celula so' vale no nucleo de alta densidade
BASE = os.path.join(os.path.dirname(__file__), "..", "analise")

linhas = list(csv.DictReader(open(os.path.join(BASE, "tacadas_tela.csv"), encoding="utf-8")))
tac = [(int(r["tela_x"]), int(r["tela_y"]), r["lado"]) for r in linhas if r["acertou"] == "1"]
print(f"{len(tac)} tacadas")

zonas = {}
for lado in ("esq", "dir"):
    pts = [(x, y) for x, y, l in tac if l == lado]
    cont = {}
    for x, y in pts:
        cont[(x // CEL, y // CEL)] = cont.get((x // CEL, y // CEL), 0) + 1
    validas = {c for c, n in cont.items() if n >= MIN_TAC}
    # dilata uma celula: margem para o agente decidir antes da bola chegar
    dilatada = set(validas)          # sem dilatar: o gatilho tem de ser tardio
    cobertas = sum(1 for x, y in pts if (x // CEL, y // CEL) in dilatada)
    zonas[lado] = sorted(map(list, dilatada))
    print(f"  {lado}: {len(validas)} celulas ({len(dilatada)} dilatadas) "
          f"= {len(dilatada)*CEL*CEL} px2 | cobre {cobertas/len(pts):.1%} das tacadas")

json.dump({"celula": CEL, "zonas": zonas},
          open(os.path.join(BASE, "zona_flipper.json"), "w"))
print("zona_flipper.json gravado")

# --- a bola fica tempo suficiente dentro da zona? ---------------------------
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

Z = {l: {tuple(c) for c in cs} for l, cs in zonas.items()}
def dentro(x, y, lado):
    return (x // CEL, y // CEL) in Z[lado]

env = SpaceCadetEnv(quadros_por_passo=1, visao=True, max_passos=288_000)  # 25 ms
m = PPO.load("ppo_c9_base", device="cpu")
obs, _ = env.reset()
visitas = {"esq": [], "dir": []}
atual = {"esq": 0, "dir": 0}
for _ in range(12000):                       # 12000 quadros = 300 s de jogo
    obs, _, term, trunc, info = env.step(int(m.predict(obs, deterministic=True)[0]))
    for lado in ("esq", "dir"):
        if dentro(info["tela_x"], info["tela_y"], lado):
            atual[lado] += 1
        elif atual[lado]:
            visitas[lado].append(atual[lado]); atual[lado] = 0
    if term or trunc:
        obs, _ = env.reset()
env.close()

print("\n=== tempo da bola dentro da zona (1 quadro = 25 ms) ===")
for lado in ("esq", "dir"):
    v = np.array(visitas[lado])
    if not len(v):
        print(f"  {lado}: nenhuma visita!"); continue
    print(f"  {lado}: {len(v)} visitas em 300s ({len(v)/300*60:.0f}/min) | "
          f"duracao mediana {np.median(v)*25:.0f} ms  p10 {np.percentile(v,10)*25:.0f} ms  "
          f"p90 {np.percentile(v,90)*25:.0f} ms")
    print(f"      visitas curtas demais para decidir (<25 ms): {(v < 1).mean():.1%} | "
          f"que comportam espera de 150 ms: {(v >= 6).mean():.1%}")
