"""Descobre qual pacote LaTeX quebra neste MiKTeX."""
import os
import subprocess

EXE = r"C:\Users\drian\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
MODELO = "\\documentclass{scrartcl}\n\\usepackage{%s}\n\\begin{document}x\\end{document}\n"

for pac in ("microtype", "scrlayer-scrpage", "hyperref", "fancyvrb",
            "booktabs", "geometry", "xcolor", "amsmath", "graphicx", "babel"):
    with open("_t.tex", "w", encoding="utf-8") as f:
        f.write(MODELO % pac)
    r = subprocess.run([EXE, "-interaction=nonstopmode", "-halt-on-error", "_t.tex"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        erro = [l for l in r.stdout.split("\n") if l.startswith("!")][:1]
        print(f"  FALHA {pac}: {erro[0][:70] if erro else '?'}")
    else:
        print(f"  ok    {pac}")

for f in os.listdir("."):
    if f.startswith("_t."):
        os.remove(f)
