"""Correcoes da segunda rodada de revisao."""
import io
import os

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")


def troca(arq, pares):
    p = os.path.join(CORE, arq)
    s = io.open(p, encoding="utf-8").read()
    feitas = puladas = 0
    for a, b in pares:
        if s.count(a) == 1:
            s = s.replace(a, b); feitas += 1
        elif b and b in s:
            puladas += 1
        else:
            raise AssertionError(f"{arq}: ancora -> {a[:55]}")
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"  {arq}: {feitas} aplicadas, {puladas} ja estavam")


# 120 Hz x 40 Hz explicado onde o leitor encontra primeiro
troca("03_instrumentar.md", [
    ("`pb::frame(float dt)` executa um passo de física.",
     "A física roda a **120 Hz**, e eu agrupo três quadros por decisão: o agente\n"
     "age a **40 Hz**, uma ação a cada 25 ms.\n\n"
     "`pb::frame(float dt)` executa um passo de física."),
])

# o 87% do paper da CMU era uma promessa que nunca voltava
troca("02_pesquisa.md", [
    ("O agente deles faz 2,35 vezes o aleatório, e 87% do humano. Guarde esse 87%,\nporque ele volta.",
     "O agente deles faz 2,35 vezes o aleatório e 87% do humano. Esse segundo número\n"
     "é o que eu não consigo calcular para o meu, porque nunca cheguei a coletar uma\n"
     "linha de base humana."),
])

# "p-valor com quinze zeros" e o overclaim da celula unica
troca("07_reacao.md", [
    ("p-valor com quinze zeros.", "com $p$ da ordem de $10^{-15}$."),
])

troca("09_gifs.md", [
    ("**Ele aprendeu uma situação e spamma no resto.** As 4,3 vezes sobre o acaso vêm\ndaquela célula sozinha.",
     "**Ele aprendeu uma situação e spamma no resto.** Aquela é a única célula com\n"
     "sinal claro de mira; no restante, a política se parece muito mais com spam.\n"
     "Não cheguei a fazer a ablação que provaria quanto do ganho vem só dali."),
    ("\\caption{Onde ele aperta (cinza) contra onde realmente conecta (verde), sobre o tabuleiro real.}",
     "\\caption{Onde ele aperta (cinza) contra onde realmente conecta (vermelho), sobre o tabuleiro real.}"),
])

# "estrategia otima" e' forte demais para o que foi medido
troca("10_descoberta.md", [
    ("Então a estratégia ótima não é \"bater bem\". É **durar**.",
     "Então, para estes agentes, **durar valeu mais que mirar**. O recorde humano de\n"
     "126 milhões sugere que em outro regime de jogo a pontaria e a progressão\n"
     "voltam a pesar."),
])

# na conclusao ainda estavam o 941x isolado e o "tempo de reacao humano"
troca("12_aprendi.md", [
    ("**Instrumentar vale muito mais que fotografar a tela.** 941 vezes a velocidade\nreal é a diferença entre rodar dez experimentos e rodar um.",
     "**Instrumentar vale muito mais que fotografar a tela.** A instrumentação leva a\n"
     "física a até 941 vezes o tempo real, e o treino completo a cerca de 17 vezes.\n"
     "É a diferença entre rodar dez experimentos e rodar um."),
    ("O agente do Space Cadet não vai bater recorde nenhum. Com tempo de reação humano\nele perde para uma moeda.",
     "O agente do Space Cadet não vai bater recorde nenhum. Com 250 ms de latência de\n"
     "ação, na faixa usada como referência humana, ele perde para uma moeda."),
    ("**Medição pareada, sempre.** A variância entre execuções é de 40%. Comparar duas\navaliações rodadas em momentos diferentes não significa nada. Todos os números\ndeste documento vêm de comparações em série, no mesmo processo, com teste\nestatístico.",
     "**Avaliação lado a lado, no mesmo processo.** A variância entre execuções é de\n"
     "40%, e comparar duas avaliações rodadas em momentos diferentes não significa\n"
     "nada. Todos os números deste documento vêm de agentes avaliados em série, no\n"
     "mesmo processo, com Mann-Whitney entre as amostras. Os episódios não\n"
     "compartilham semente, então não é um teste pareado no sentido estatístico."),
])

print("correcoes da revisao 2 aplicadas")
