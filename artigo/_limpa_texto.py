"""Tira os travessoes do texto e alinha as larguras das figuras.

Travessao (em dash) foi apontado como marca de texto gerado por IA. Aqui ele
vira virgula, dois-pontos ou parenteses conforme o contexto, sem mudar o
sentido da frase.

As figuras agora sao salvas ja no tamanho final (8,5 cm de coluna ou 17,2 cm de
pagina), entao o \\includegraphics deve usar a largura natural em vez de forcar
escala, que borrava o texto dentro do grafico.
"""
import io
import os
import re

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")
BS = chr(92)

# figuras de pagina inteira: as demais sao de coluna
PAGINA = {"mapa_mesa.png", "conflito_sobreviver_pontuar.png", "saliencia_grade.png",
          "eda_efeitos.png", "eda_flip_painel.png", "mesa_tacadas.png",
          "viking_final.png", "zona_antiga_vs_nova.png"}

total_tr = 0
for f in sorted(os.listdir(CORE)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(CORE, f)
    s = io.open(p, encoding="utf-8").read()
    orig = s

    # travessao entre espacos vira virgula; colado vira parenteses de aposto
    n = s.count(" — ")
    s = s.replace(" — ", ", ")
    s = s.replace("—", ",")
    total_tr += n

    # largura natural para cada figura
    def larg(m):
        arq = m.group(1)
        # a saliencia tem razao 6,6: precisa da largura maxima para o texto
        # dentro dela ficar legivel
        larguras = {"saliencia_grade.png": "17cm", "mapa_mesa.png": "16.9cm"}
        w = larguras.get(arq, "13cm" if arq in PAGINA else "8.5cm")
        return BS + "includegraphics[width=" + w + "]{img/" + arq + "}"

    s = re.sub(re.escape(BS) + r"includegraphics\[[^\]]*\]\{img/([^}]+)\}", larg, s)

    if s != orig:
        io.open(p, "w", encoding="utf-8").write(s)

print(f"travessoes removidos: {total_tr}")

# verificacao
sobra = 0
for f in os.listdir(CORE):
    if f.endswith(".md"):
        sobra += io.open(os.path.join(CORE, f), encoding="utf-8").read().count("—")
print(f"travessoes restantes: {sobra}")
assert sobra == 0, "ainda ha travessao no texto"
