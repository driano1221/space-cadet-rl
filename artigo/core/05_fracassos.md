# Quatro treinos abaixo do acaso

Ambiente pronto, PPO configurado, GPU quente. Rodei o primeiro treino com
enorme expectativa.

O agente aprendeu a **não apertar nada**.

Cem por cento das ações em "não fazer nada". Ele lançava a bola, assistia ela
cair, e recomeçava. Descobri depois, lendo o paper da CMU, que o time deles
passou exatamente por isso e descreveu como o agente ter "medo da penalidade
futura". Meu agente era covarde por conta própria.

Ajustei a recompensa, rodei de novo. E de novo. E de novo.

| Treino | Score mediano |
|---|---|
| 1 | 144.000 |
| 2 | 72.000 |
| 3 | 154.000 |
| 4 | 212.500 |
| **Aleatório** | **404.375** |

Quatro treinos seguidos, todos **abaixo de apertar botão ao acaso**.

Isso é humilhante de um jeito muito específico. Não é o agente estar ruim, é ele
estar *pior que nada*. Eu gastei horas de GPU para produzir algo que perde para
uma moeda.

Demorei a entender isso, e é um ponto importante sobre pinball.

Em jogos de Atari, uma política aleatória faz basicamente zero. No pinball, não.
A física trabalha por você: a bola desce, bate em coisas, acende luzes, e
**pontua sozinha**. Apertar os flippers de vez em quando devolve ela para cima,
onde ela pontua mais.

O aleatório não é um adversário fraco. Ele é uma linha de base forte, e todo
mundo que compara agente de pinball com "random" precisa dizer isso.

Levantei quatro hipóteses para o fracasso:

1. o agente não enxerga a mesa
2. o aleatório é forte demais
3. o crédito está diluído (os pontos chegam segundos depois da tacada)
4. faltou escala de treino

A hipótese 4 era a mais confortável, do tipo "é só treinar mais". Testei
triplicando o treino: 2,5 milhões, 5 milhões, 7,5 milhões de passos.

Nenhuma diferença estatística ($p = 0{,}55$ e $p = 0{,}48$). **"Faltou treino"
morreu ali**, e eu fiquei sem a desculpa mais fácil.

Sobrava a hipótese mais chata.

A hipótese 1 era a mais chata de aceitar, porque implicava refazer o ambiente.

Meu agente recebia um vetor de números: posição da bola, velocidade, ângulo dos
flippers, placar. Parece razoável, até você perceber que **os alvos não estavam
ali**. Nem os bumpers, nem as rampas, nem as luzes.

Ele sabia onde a bola estava, mas não tinha ideia do que existia na mesa. Era
como jogar sinuca no escuro sabendo só onde está a bola branca.

Construí uma grade de $9 \times 36 \times 28$, tipo uma imagem de nove canais:

```
canal 0  bola          canal 5  rollovers
canal 1  velocidade x  canal 6  luzes acesas
canal 2  velocidade y  canal 7  flippers
canal 3  bumpers       canal 8  alvos do multiplicador
canal 4  alvos
```

E coloquei uma CNN pequena para processar isso.

| | Score mediano |
|---|---|
| Aleatório | 404.375 |
| Antes da visão | 212.500 |
| **Com visão da mesa** | **1.740.875** |

**4,3 vezes o aleatório**, Mann-Whitney com $p = 5{,}7 \times 10^{-15}$. O pior
episódio dele (548.000) supera a mediana do aleatório.

E a evidência é limpa de um jeito raro: só a percepção mudou. Mesma arquitetura,
mesma recompensa, mesmo algoritmo, mesmo número de passos. De 1,9 vezes abaixo
do acaso para 4,3 vezes acima.

```{=latex}
\begin{figure}[tb]\centering
\includegraphics[width=8.5cm]{img/baseline_score.png}
\caption{O salto da visão da mesa contra a linha de base aleatória.}
\end{figure}
```

Fui olhar quais canais a rede usava. Os de velocidade somam 35,6% da saliência
(importa para onde a bola *vai*, não onde ela está), os da mesa somam 39,4%, e
as **luzes pesam mais que qualquer objeto fixo**, 13,3% sozinhas, por serem o
único canal que muda, indicando quais missões estão ativas.

Ele aprendeu a ler o estado do jogo pelas luzes. Isso me deixou genuinamente
feliz.

```{=latex}
\begin{figure*}[tb]\centering
\includegraphics[width=17cm]{img/saliencia_grade.png}
\caption{Saliência por canal: velocidade e luzes dominam. Ele olha para onde a bola vai, não para onde está.}
\end{figure*}
```

Lição que ficou: **antes de mexer em hiperparâmetro, garanta que a observação
contém o que o agente precisa perceber.** Não foi ajuste fino que resolveu, foi
dar olhos para ele.
