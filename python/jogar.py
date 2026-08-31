"""Voce joga o MESMO ambiente que o agente, e tudo fica gravado.

Nao e' o jogo original: e' o SpaceCadetEnv instrumentado, com o mesmo espaco de
acao (nada/esq/dir/ambos), a mesma taxa de decisao (13,3 Hz) e o mesmo estado
logado. Por isso a comparacao humano x agente fica pareada de verdade - nenhum
dos dois tem informacao ou frequencia que o outro nao tem.

Teclas:  <-  flipper esquerdo   |   ->  flipper direito   |   ESC sai
Uso: python jogar.py [n_partidas] [seu_nome]
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# SDL_VIDEODRIVER e' global do processo e cada subsistema le a variavel na sua
# propria inicializacao: o jogo sobe em "dummy" (sem janela dele) e a variavel
# e' removida antes do pygame.init, que entao abre a janela de verdade.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import numpy as np, pygame
from spacecadet_gym import SpaceCadetEnv
import spacecadet_env as core

N_PARTIDAS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
NOME = sys.argv[2] if len(sys.argv) > 2 else "humano"
SAIDA = os.path.join(os.path.dirname(__file__), "..", "analise", f"demos_{NOME}.jsonl")

QUADROS = 3                       # igual ao agente
DT = QUADROS / 40.0               # 75 ms por decisao, em tempo real
ESCALA = 2

env = SpaceCadetEnv(quadros_por_passo=QUADROS, visao=True, max_passos=288_000)
obs, _ = env.reset()
tela0 = np.array(core.capturar_tela())
h, w = tela0.shape[:2]

os.environ.pop("SDL_VIDEODRIVER", None)   # a partir daqui, janela real
os.environ.pop("SDL_AUDIODRIVER", None)
pygame.init()
win = pygame.display.set_mode((w * ESCALA, h * ESCALA))
pygame.display.set_caption("Space Cadet - gravando (ESC sai)")
fonte = pygame.font.SysFont("consolas", 16)
sup = pygame.Surface((w, h))

def desenhar(score, partida, extra=""):
    a = np.array(core.capturar_tela())
    pygame.surfarray.blit_array(sup, np.transpose(a, (1, 0, 2)))
    pygame.transform.scale(sup, (w * ESCALA, h * ESCALA), win)
    txt = f"partida {partida}/{N_PARTIDAS}   score {score:,}   {extra}"
    win.blit(fonte.render(txt, True, (255, 255, 0)), (8, 8))
    pygame.display.flip()

demos, partida, sair = [], 1, False
while partida <= N_PARTIDAS and not sair:
    obs, _ = env.reset()
    passos, score = [], 0
    t_prox = time.perf_counter()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                sair = True
        if sair:
            break
        k = pygame.key.get_pressed()
        a = int(k[pygame.K_LEFT]) | (int(k[pygame.K_RIGHT]) << 1)
        v = obs["vetor"].tolist()
        obs, r, term, trunc, info = env.step(a)
        score = info.get("score", score)
        passos.append({"a": a, "r": round(float(r), 4), "s": int(score), "v": [round(x, 4) for x in v]})
        desenhar(score, partida)
        t_prox += DT                       # tempo real: nao acelera nem atrasa
        dorme = t_prox - time.perf_counter()
        if dorme > 0:
            time.sleep(dorme)
        else:
            t_prox = time.perf_counter()   # perdeu o passo, nao acumula divida
        if term or trunc:
            break
    if passos:
        demos.append({"nome": NOME, "partida": partida, "score": int(score),
                      "passos_n": len(passos), "duracao_s": round(len(passos) * DT, 1),
                      "passos": passos})
        print(f"partida {partida}: {score:,} pontos em {len(passos)*DT:.0f}s "
              f"({len(passos)} decisoes)", flush=True)
        partida += 1

env.close(); pygame.quit()
with open(SAIDA, "w", encoding="utf-8") as f:
    for d in demos:
        f.write(json.dumps(d) + "\n")
if demos:
    sc = sorted(d["score"] for d in demos)
    print(f"\n{len(demos)} partidas | mediana {sc[len(sc)//2]:,} | max {sc[-1]:,}")
    print(f"gravado em {os.path.abspath(SAIDA)}")
