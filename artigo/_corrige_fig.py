"""Normaliza os blocos de figura em LaTeX dentro dos capitulos.

Duas armadilhas ja pagas:
1. substituir "egin{figure}" por "\\begin{figure}" e' auto-destrutivo, porque a
   forma correta contem a quebrada como substring;
2. dentro de bloco raw LaTeX o pandoc nao escapa nada, entao um "%" no texto da
   legenda comenta o resto da linha e o \\caption fica sem fechar
   ("File ended while scanning use of \\caption").
"""
import io
import os
import re

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")
BS = chr(92)


def escapa_caption(m):
    texto = m.group(1)
    # so' escapa o que ainda nao esta escapado
    texto = re.sub(r"(?<!" + re.escape(BS) + r")%", BS + "%", texto)
    texto = re.sub(r"(?<!" + re.escape(BS) + r")&", BS + "&", texto)
    return BS + "caption{" + texto + "}"


for f in sorted(os.listdir(CORE)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(CORE, f)
    s = io.open(p, encoding="utf-8").read()
    orig = s
    s = s.replace("\x08", "")
    s = s.replace(BS + "b" + BS + "begin{", BS + "begin{")
    s = s.replace(BS + BS + "begin{", BS + "begin{")
    s = s.replace(BS + BS + "end{", BS + "end{")
    s = re.sub(re.escape(BS) + r"caption\{([^}]*)\}", escapa_caption, s)
    if s != orig:
        io.open(p, "w", encoding="utf-8").write(s)
        print(f"  {f}: normalizado")

print("--- verificacao ---")
total = 0
for f in sorted(os.listdir(CORE)):
    if not f.endswith(".md"):
        continue
    s = io.open(os.path.join(CORE, f), encoding="utf-8").read()
    b = len(re.findall(re.escape(BS) + r"begin\{figure\*?\}", s))
    e = len(re.findall(re.escape(BS) + r"end\{figure\*?\}", s))
    assert b == e, f"{f}: {b} begin contra {e} end"
    for m in re.finditer(re.escape(BS) + r"caption\{([^}]*)\}", s):
        cap = m.group(1)
        cru = re.findall(r"(?<!" + re.escape(BS) + r")%", cap)
        assert not cru, f"{f}: caption com % nao escapado -> {cap[:50]}"
    total += b
    if b:
        print(f"  {f}: {b} figuras, captions limpos")
print(f"total: {total} figuras")
