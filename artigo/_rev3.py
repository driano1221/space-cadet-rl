"""Correcoes da terceira rodada de revisao."""
import io
import os
import re

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")


def troca(arq, pares):
    p = os.path.join(CORE, arq)
    s = io.open(p, encoding="utf-8").read()
    n = 0
    for a, b in pares:
        if s.count(a) >= 1:
            s = s.replace(a, b, 1); n += 1
        elif b and b in s:
            pass
        else:
            raise AssertionError(f"{arq}: ancora -> {a[:50]}")
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"  {arq}: {n}")


# 1. frase duplicada: o script de correcao anterior rodou duas vezes
p = os.path.join(CORE, "03_instrumentar.md")
linhas = io.open(p, encoding="utf-8").read().split("\n")
achou = [i for i, l in enumerate(linhas) if l.startswith("A física roda a **120 Hz**")]
assert len(achou) <= 2, f"copias demais: {len(achou)}"
if len(achou) == 2:
    del linhas[achou[1]:achou[1] + 3]    # a copia e as duas linhas dela
    io.open(p, "w", encoding="utf-8").write(re.sub(r"\n{3,}", "\n\n", "\n".join(linhas)))
    print("  03_instrumentar.md: duplicata removida")
else:
    print("  03_instrumentar.md: sem duplicata")

# 2. "pareado" onde o proprio artigo ja explica que nao e'
troca("12_aprendi.md", [
    ("**Compare no pareado, no mesmo processo.**",
     "**Compare lado a lado, no mesmo processo.**"),
    ("A avaliação interna do treinador (n=6)\ncontra a avaliação pareada (n=10).",
     "A avaliação interna do treinador (n=6)\ncontra a avaliação em série (n=10)."),
])

# 7. o "2,4" ficou sem unidade quando VRAM virou RAM
troca("08_teto.md", [
    ("**Algoritmo off-policy.** Bloqueada por hardware: o buffer exigiria 68 GB e eu\ntenho 2,4.",
     "**Algoritmo off-policy.** Bloqueado por hardware: o buffer estimado ficaria em\n"
     "cerca de 68 GB de RAM, acima da memória disponível na máquina."),
])

# 8. optimalidade global nao foi demonstrada
troca("09_gifs.md", [
    ("Se a ação não custa e às vezes ajuda, a política\nótima é apertar quase sempre.",
     "Como apertar não custa nada e às vezes ajuda, o\nambiente favorece políticas que apertam com muita frequência."),
])

# 9. dois absolutos que a nota de metodo ja' relativiza
troca("10_descoberta.md", [
    ("Eu passei o projeto inteiro tratando pontaria como sinônimo de competência. O\njogo não recompensa pontaria. Recompensa permanência.",
     "Eu passei o projeto inteiro tratando pontaria como sinônimo de competência.\n"
     "Nesses agentes, o placar recompensava muito mais permanência do que pontaria."),
])
troca("11_ultima_rodada.md", [
    ("O limite não é de incentivo, nem de exploração, nem de tempo de treino, nem de\ninformação. É estrutural.",
     "Os resultados apontam para um limite estrutural desta configuração: não é de\n"
     "incentivo, nem de exploração, nem de tempo de treino, nem de informação."),
])

# 12 e 13. o resumo emenda 4,3x e 0,62x, e os dois numeros vem de avaliacoes
# diferentes (visao da mesa x medicao de latencia)
troca("07_reacao.md", [
    ("com $p$ da ordem de $10^{-15}$. Eu já estava pensando em como postar isso.",
     "com $p$ da ordem de $10^{-15}$. Eu já estava pensando em como postar isso.\n\n"
     "(Um aviso sobre dois números que vão aparecer juntos: o 4,3x é da avaliação\n"
     "que mediu o efeito da visão da mesa, e o 3,8x da tabela abaixo é da coleta de\n"
     "latência. Mesma política, avaliações diferentes.)"),
])

# c. a ausencia de linha de base humana aparecia em dois lugares
troca("02_pesquisa.md", [
    ("Esse segundo número\né o que eu não consigo calcular para o meu, porque nunca cheguei a coletar uma\nlinha de base humana.",
     "Esse segundo número é o que eu não consigo\ncalcular para o meu: volto a isso no capítulo sobre latência."),
])

print("revisao 3 aplicada")
