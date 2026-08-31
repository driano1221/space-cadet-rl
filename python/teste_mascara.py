"""A mascara bloqueia o flipper fora da zona e o libera dentro?

Politica "sempre ambos": sem mascara a pa' sobe em todo passo; com mascara, so'
nos passos em que a bola esta' na zona daquele lado. A fracao de passos com a
pa' erguida tem de cair para perto da fracao de tempo que a bola passa na zona.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spacecadet_gym import SpaceCadetEnv

base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analise")
z = json.load(open(os.path.join(base, "zona_flipper.json")))
CEL = z["celula"]
Z = {l: {tuple(c) for c in cs} for l, cs in z["zonas"].items()}

for mascara in (False, True):
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000,
                        mascara_zona=mascara)
    obs, info = env.reset()
    erguido_e = erguido_d = na_zona_e = na_zona_d = n = 0
    for _ in range(1200):
        cel = (info["tela_x"] // CEL, info["tela_y"] // CEL)
        na_zona_e += cel in Z["esq"]; na_zona_d += cel in Z["dir"]
        obs, _, term, trunc, info = env.step(3)          # sempre ambos
        erguido_e += obs["vetor"][9] > 0.15
        erguido_d += obs["vetor"][10] > 0.15
        n += 1
        if term or trunc:
            obs, info = env.reset()
    env.close()
    print(f"mascara={str(mascara):>5}: pa erguida esq {erguido_e/n:>5.1%} dir {erguido_d/n:>5.1%}"
          f"   | bola na zona esq {na_zona_e/n:.1%} dir {na_zona_d/n:.1%}")
