"""Procura a origem real do erro: chaves desbalanceadas e caption truncado."""
import os
import re

TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida", "artigo.tex")
BS = chr(92)
s = open(TEX, encoding="utf-8").read()

print("LTcaptype restantes:", s.count("LTcaptype"))
print("longtable restantes:", s.count(BS + "begin{longtable}"))
print("caption total:", s.count(BS + "caption{"))

# balanco de chaves acumulado, ignorando as escapadas
saldo = 0
linhas = s.split("\n")
for n, l in enumerate(linhas, 1):
    limpa = l.replace(BS + "{", "").replace(BS + "}", "")
    saldo += limpa.count("{") - limpa.count("}")
    if saldo < 0:
        print(f"\nchave fechada a mais na linha {n}: {l[:90]}")
        break
print("saldo final de chaves:", saldo)

# caption cujo argumento nao fecha na mesma linha
for n, l in enumerate(linhas, 1):
    if BS + "caption{" in l:
        if l.count("{") != l.count("}"):
            print(f"\ncaption desbalanceado na linha {n}:")
            print("  " + l[:140])
