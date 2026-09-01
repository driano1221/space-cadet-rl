"""Corrige erros factuais apontados na revisao.

Cada troca abaixo tem o numero verificado no lugar do que estava no texto.
"""
import io
import os

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")


def troca(arq, pares):
    p = os.path.join(CORE, arq)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pares:
        assert s.count(a) == 1, f"{arq}: ancora ausente ou repetida -> {a[:60]}"
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"  {arq}: {len(pares)} correcoes")


# 1. as tres velocidades nao fechavam entre si
troca("03_instrumentar.md", [
    ("""O 941x é o que torna o projeto viável num notebook. Um treino de 2,5 milhões de
passos representa **52 horas de jogo**, e roda em cinquenta e três minutos.

Sem isso, o mesmo treino levaria dois dias inteiros de máquina ligada. E eu
rodei mais de dez treinos.""",
     """Vale separar dois números que são fáceis de confundir. O **941x** é a física
sozinha, rodando sem a rede neural no laço: é o teto do ambiente. No treino de
verdade a rede entra, e a conta muda.

Um treino de 2,5 milhões de decisões, a 25 ms cada, representa **17,4 horas de
jogo**. Ele roda em **uma hora**, o que dá aceleração efetiva de **17x**.

Ainda é a diferença entre rodar dez experimentos e rodar um. Sem o ambiente
instrumentado, esses mesmos treinos levariam quase um dia cada."""),
])

# 2. o desconto a 60 s: manter a conta feita no capitulo de RL
troca("08_teto.md", [
    ("com $\\gamma = 0{,}995$ e 40 decisões por segundo, um evento a 60\nsegundos de distância vale 0,00003% da recompensa.",
     "com $\\gamma = 0{,}995$ e 40 decisões por segundo, um evento a 60\nsegundos de distância vale 0,0006% da recompensa."),
    ("A de memória temporal merece nota.",
     "O teste de memória temporal merece nota."),
])

# 3. o espaco de acoes mudou ao longo do projeto e o texto nao contava quando
troca("04_rl.md", [
    ("""A cada 25 milissegundos o agente olha o **estado** $s_t$ (onde a bola está, para
onde vai, ângulo das pás, placar) e escolhe uma **ação** $a_t$ entre quatro:
não apertar nada, apertar o flipper esquerdo, o direito, ou os dois.""",
     """A cada 25 milissegundos o agente olha o **estado** $s_t$ (onde a bola está, para
onde vai, ângulo das pás, placar) e escolhe uma **ação** $a_t$. Na versão
principal são quatro: não apertar nada, apertar o flipper esquerdo, o direito,
ou os dois. Esse espaço mudou nos experimentos, e vou avisando quando: no
ambiente de opções ele vira sete (não apertar, ou seis tempos de espera) e
depois treze (os mesmos seis tempos, para cada um dos dois flippers)."""),
    ("E no começo tudo é igual. Testei isso numa rede recém-criada e as sete opções\nsaem exatamente com $1/7 = 0{,}143$ de probabilidade cada, desvio zero. O\naprendizado é literalmente entortar essa distribuição uniforme.",
     "E no começo tudo é igual. Testei numa rede recém-criada do ambiente de opções,\nque tem sete: elas saem exatamente com $1/7 = 0{,}143$ de probabilidade cada,\ncom desvio zero. O aprendizado é literalmente entortar essa distribuição\nuniforme."),
])

# 4. "fecha" nao fechava: 6,8 contra 8,8 e' 30% de diferenca
troca("10_descoberta.md", [
    ("São os dois fatores multiplicados. Ele sobrevive **3,1 vezes menos** e pontua\n**2,2 vezes mais devagar**. Multiplicando dá 6,8, e o score difere 8,8 vezes.\nFecha.",
     "São os dois fatores agindo juntos. Ele sobrevive **3,1 vezes menos** e pontua\n**2,2 vezes mais devagar**. O produto dá 6,8 e o score difere 8,8 vezes: a\nsobra é esperada, porque mediana de produto não é produto de medianas. O que\nimporta é a ordem de grandeza, e ela vem dos dois fatores."),
])

# 5. p = 0,052 nao e' significativo a 5%
troca("11_ultima_rodada.md", [
    ("**Nenhuma superou o controle.** Duas empataram, três pioraram com significância.",
     "**Nenhuma superou o controle.** Todas ficaram com score menor: duas com\n$p < 0{,}05$, uma no limite ($p = 0{,}052$) e duas sem diferença detectável."),
    ("**As três que pioraram, pioraram pelo mesmo motivo.**",
     "**As três de baixo caíram pelo mesmo motivo.**"),
])

print("erros factuais corrigidos")
