"""Lista os comandos LaTeX indefinidos no log da ultima compilacao."""
import os
import re

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida", "artigo.log")
texto = open(LOG, encoding="utf-8", errors="replace").read()

faltando = []
linhas = texto.split("\n")
for i, l in enumerate(linhas):
    if "Undefined control sequence" in l:
        # o comando aparece no fim da linha seguinte
        for j in range(i + 1, min(i + 4, len(linhas))):
            m = re.findall(r"\\([a-zA-Z@]+)\s*$", linhas[j])
            if m:
                faltando.append(m[-1])
                break

print("comandos indefinidos:", sorted(set(faltando)))
print("ocorrencias:", len(faltando))
