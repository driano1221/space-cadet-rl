"""Corrige as duas legendas trocadas e move o mapa para o capitulo certo.

O mapa de densidade estava no capitulo de instrumentacao com a legenda "a grade
de nove canais", que descreve outra coisa. Ele pertence ao capitulo do berco:
as duas manchas sobre os flippers sao exatamente o fenomeno descrito ali.
"""
import io
import os
import re

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")

# --- remove o bloco do mapa do capitulo 3, por linhas ---
p = os.path.join(CORE, "03_instrumentar.md")
linhas = io.open(p, encoding="utf-8").read().split("\n")
ini = next(i for i, l in enumerate(linhas) if "mapa_mesa.png" in l)
# o bloco vai do ```{=latex} anterior ate o ``` seguinte
a = next(i for i in range(ini, -1, -1) if linhas[i].startswith("```{=latex}"))
b = next(i for i in range(ini, len(linhas)) if linhas[i].strip() == "```")
del linhas[a:b + 1]
texto = re.sub(r"\n{3,}", "\n\n", "\n".join(linhas))
io.open(p, "w", encoding="utf-8").write(texto)
print("cap 3: bloco do mapa removido")

# --- corrige a legenda da varredura e insere o mapa no capitulo 6 ---
p = os.path.join(CORE, "06_berco.md")
s = io.open(p, encoding="utf-8").read()

velha = [l for l in s.split("\n") if l.startswith("\\caption{Dois agentes")]
assert len(velha) == 1, f"legenda do conflito: {len(velha)} ocorrencias"
s = s.replace(velha[0],
              "\\caption{Varredura da probabilidade de manter o flipper pressionado. "
              "Score e sobrevivência apontam para lados opostos, e de 95\\% para "
              "100\\% o score cai 15 vezes.}")

alvo = "Quatro caminhos independentes caem nesse buraco:"
assert s.count(alvo) == 1, "ancora do berco"
figura = ("```{=latex}\n"
          "\\begin{figure*}[tb]\\centering\n"
          "\\includegraphics[width=16.9cm]{img/mapa_mesa.png}\n"
          "\\caption{Onde a bola passa o tempo, por política. As duas manchas "
          "escuras sobre os flippers, no painel da direita, são o berço: a bola "
          "parada entre as pás.}\n"
          "\\end{figure*}\n"
          "```\n\n")
s = s.replace(alvo, figura + alvo)
io.open(p, "w", encoding="utf-8").write(s)
print("cap 6: legenda corrigida e mapa inserido")
