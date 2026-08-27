import csv, statistics as st
base = r"C:\Users\drian\Games\pinball_rl\SpaceCadetPinball\bin\Release"
nomes = {0: "nula (nunca aperta)", 1: "aleatoria", 2: "sempre apertado"}
print(f"{'politica':<22}{'n':>5}{'mediana':>10}{'media':>10}{'p90':>10}{'dur.med(s)':>12}")
res = {}
for p in (0, 1, 2):
    rows = list(csv.DictReader(open(f"{base}/rl_dados_p{p}.csv")))
    sc = sorted(int(r["score"]) for r in rows)
    dur = [float(r["segundos_jogo"]) for r in rows]
    res[p] = sc
    print(f"{nomes[p]:<22}{len(sc):>5}{st.median(sc):>10}{int(st.mean(sc)):>10}"
          f"{sc[int(.9*(len(sc)-1))]:>10}{st.mean(dur):>12.1f}")
print()
print("razao mediana aleatoria/nula :", round(st.median(res[1]) / st.median(res[0]), 2), "x")
print("razao mediana sempre/nula    :", round(st.median(res[2]) / st.median(res[0]), 2), "x")
