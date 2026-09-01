"""Exporta todas as paginas e procura defeitos de diagramacao.

Checa automaticamente o que da' para checar sem olhar: texto que passa da
margem, figura maior que a area util, e sobras de marcacao Markdown.
"""
import os
import re

import fitz

AQUI = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(AQUI, "saida", "artigo.pdf")
PAGS = os.path.join(AQUI, "saida", "paginas")
os.makedirs(PAGS, exist_ok=True)

d = fitz.open(PDF)
MARGEM = 1.8 * 28.35          # 1,8 cm em pontos
larg, alt = d[0].rect.width, d[0].rect.height
problemas = []

for n in range(d.page_count):
    pg = d[n]
    pg.get_pixmap(dpi=110).save(os.path.join(PAGS, f"pag_{n+1:02d}.png"))

    # texto fora das margens
    for b in pg.get_text("blocks"):
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
        if x1 > larg - MARGEM + 6 or x0 < MARGEM - 6:
            amostra = " ".join(txt.split())[:55]
            if amostra:
                problemas.append(f"pag {n+1}: texto fora da margem: {amostra}")
                break

    # imagem mais larga que a area util
    for img in pg.get_images(full=True):
        r = pg.get_image_rects(img[0])
        for rect in r:
            if rect.width > larg - 2 * MARGEM + 8:
                problemas.append(f"pag {n+1}: figura passa da area util "
                                 f"({rect.width:.0f} pt)")

    # sobra de markdown que nao virou formatacao
    t = pg.get_text()
    for marca in ("**", "```", "](", "\\begin", "\\caption"):
        if marca in t:
            problemas.append(f"pag {n+1}: marcacao crua no texto: {marca}")

print(f"{d.page_count} paginas exportadas em saida/paginas/")
if problemas:
    print(f"\n{len(problemas)} problemas:")
    for p in problemas[:20]:
        print("  " + p)
else:
    print("nenhum problema automatico detectado")
