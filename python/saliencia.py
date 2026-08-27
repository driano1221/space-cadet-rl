"""O que a CNN olha? Mapa de saliencia sobre a grade da mesa.

Calcula o gradiente da acao escolhida em relacao a cada celula da entrada. Onde
o gradiente e' grande, aquela celula influenciou a decisao. E' a forma direta de
responder "para onde os pesos convergiram" quando a observacao e' espacial.

Uso: python saliencia.py <tag_do_modelo> [n_amostras]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, r"C:\Users\drian\Games\pinball_patch\src")
import numpy as np
import torch
from spacecadet_gym import SpaceCadetEnv
from visao import GRADE_L, GRADE_A, N_CANAIS
from stable_baselines3 import PPO

NOMES = ["bola", "vel x", "vel y", "bumpers", "alvos", "rollovers", "luzes", "flippers"]


def coletar(tag, n=600):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
    m = PPO.load(tag, device="cpu")
    politica = m.policy
    politica.set_training_mode(False)

    acum = np.zeros((N_CANAIS, GRADE_A, GRADE_L), dtype=np.float64)
    acoes = np.zeros(4, dtype=int)
    obs, _ = env.reset()
    for i in range(n):
        lote = {k: torch.as_tensor(v[None]).float() for k, v in obs.items()}
        lote["grade"].requires_grad_(True)
        dist = politica.get_distribution(lote)
        logits = dist.distribution.logits
        a = int(logits.argmax())
        acoes[a] += 1
        politica.zero_grad()
        logits[0, a].backward()
        acum += lote["grade"].grad[0].abs().numpy()

        obs, _, term, trunc, _ = env.step(a)
        if term or trunc:
            obs, _ = env.reset()
    return acum / n, acoes


def desenhar(sal, acoes, saida):
    from PIL import Image, ImageDraw
    from datlib import Dat, BAK
    mesa = Dat(BAK).to_image(Dat(BAK).bitmap("table"))
    W, H = mesa.size
    CEL = 9
    tira = Image.new("RGB", ((N_CANAIS + 1) * (GRADE_L*CEL + 16) + 16,
                             GRADE_A*CEL + 44), (18, 18, 18))
    dr = ImageDraw.Draw(tira)
    tira.paste(mesa.resize((GRADE_L*CEL, GRADE_A*CEL)), (16, 34))
    dr.text((20, 12), "MESA", fill=(255, 220, 120))

    vmax = sal.max() or 1.0
    for c in range(N_CANAIS):
        img = Image.new("RGB", (GRADE_L*CEL, GRADE_A*CEL), (10, 10, 10))
        d2 = ImageDraw.Draw(img)
        for y in range(GRADE_A):
            for x in range(GRADE_L):
                v = sal[c, y, x] / vmax
                if v <= 0.01:
                    continue
                d2.rectangle([x*CEL, y*CEL, x*CEL+CEL-1, y*CEL+CEL-1],
                             fill=(int(255*min(1, v*2.2)), int(120*min(1, v*1.6)), 30))
        x0 = 16 + (c+1)*(GRADE_L*CEL + 16)
        tira.paste(img, (x0, 34))
        peso = 100 * sal[c].sum() / sal.sum()
        dr.text((x0 + 3, 12), f"{NOMES[c]} {peso:.0f}%", fill=(255, 220, 120))
    tira.save(saida)


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "ppo_visao_v1"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    sal, acoes = coletar(tag, n)
    tot = sal.sum()
    print("peso de cada canal na decisao:")
    for c in range(N_CANAIS):
        print(f"  {NOMES[c]:10s} {100*sal[c].sum()/tot:5.1f}%")
    nomes_a = ["nenhum", "esq", "dir", "ambos"]
    print("\nacoes:", {nomes_a[i]: f"{100*acoes[i]/acoes.sum():.1f}%" for i in range(4)})
    saida = r"C:\Users\drian\Games\pinball_rl\analise\saliencia.png"
    desenhar(sal, acoes, saida)
    print("\nsaliencia.png salvo")
