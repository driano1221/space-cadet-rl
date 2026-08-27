import csv
from collections import Counter
p = r"C:\Users\drian\Games\pinball_rl\analise\rl_dados.csv"
rows = list(csv.DictReader(open(p)))
sc = sorted(int(r["score"]) for r in rows)
ps = [int(r["passos"]) for r in rows]
bo = [int(r["bolas_usadas"]) for r in rows]
q = lambda f: sc[int(f * (len(sc) - 1))]
print("N =", len(rows))
print("bateram teto (72000 passos):", sum(1 for x in ps if x >= 72000))
print("passos  min/mediana/max:", min(ps), sorted(ps)[len(ps)//2], max(ps))
print("bolas_usadas:", dict(sorted(Counter(bo).items())))
print("score <= 0:", sum(1 for s in sc if s <= 0))
print("quantis score 0/25/50/75/95/100:", [q(0), q(.25), q(.5), q(.75), q(.95), sc[-1]])
