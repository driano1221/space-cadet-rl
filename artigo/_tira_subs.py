"""Remove os subtitulos (##), deixando so os titulos de capitulo.

Alguns subtitulos marcavam virada de assunto e o texto seguinte comecava
pressupondo esse aviso. Onde isso acontece, o subtitulo vira uma frase curta de
transicao em vez de sumir, para o paragrafo nao ficar solto.
"""
import io
import os
import re

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")

# subtitulos que viram transicao no texto, em vez de sumirem
TRANSICAO = {
    "O vídeo": "Foi um vídeo que ligou uma coisa na outra.",
    "O paper que eu queria ter achado antes":
        "Já com o projeto adiantado, encontrei o trabalho que eu queria ter lido antes.",
    "Onde meu projeto se encaixa": "Vale dimensionar o tamanho da coisa.",
    "O que o agente estava vendo": "Sobrava a hipótese mais chata.",
    "O que ele descobriu": "Fui entender o que tinha acontecido.",
    "A falésia": "Fui medir onde exatamente está a armadilha.",
    "Não é ladeira, é degrau": "O formato da queda importa mais que o tamanho dela.",
    "O que isso amarra": "Esse resultado explica várias coisas soltas.",
    "O diagnóstico": "Fui atrás das mecânicas que valem os pontos grandes.",
    "O resultado da máscara": "O efeito foi imediato.",
    "A regularidade": "E aqui está a coisa mais bonita da tabela inteira.",
    "O fim": "",
}

total = 0
for f in sorted(os.listdir(CORE)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(CORE, f)
    linhas = io.open(p, encoding="utf-8").read().split("\n")
    saida = []
    for l in linhas:
        m = re.match(r"^## (.+)$", l)
        if not m:
            saida.append(l)
            continue
        total += 1
        titulo = m.group(1).strip()
        frase = TRANSICAO.get(titulo)
        if frase:
            saida.append(frase)
        elif frase == "":
            pass                      # remove sem substituir
        else:
            pass                      # subtitulo puramente organizador: some
    texto = "\n".join(saida)
    # nunca deixar tres linhas em branco seguidas
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    io.open(p, "w", encoding="utf-8").write(texto)

print(f"subtitulos removidos: {total}")
sobra = sum(io.open(os.path.join(CORE, f), encoding="utf-8").read().count("\n## ")
            for f in os.listdir(CORE) if f.endswith(".md"))
print(f"subtitulos restantes: {sobra}")
assert sobra == 0
