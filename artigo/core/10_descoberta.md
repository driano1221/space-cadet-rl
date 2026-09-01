# A descoberta que reorganizou tudo

Com a máscara ligada, a pontaria multiplicou por vinte e o score caiu para um
nono. Isso não fazia sentido nenhum para mim.

Se o agente acerta a bola vinte vezes mais, como é que ele pontua menos?

A pergunta veio nesses termos:

> por que usar flippers como parede pontua mais que usar uma lógica para bater?
> não faz muito sentido para mim

Não fazia para mim também. Fui medir em vez de teorizar.

| | Score | Duração | Pontos/s | Pá erguida |
|---|---|---|---|---|
| Agente livre | 3.039.250 | 393 s | 5.942 | **73%** |
| Com máscara | 346.250 | 125 s | 2.673 | **1%** |

São os dois fatores agindo juntos. Ele sobrevive **3,1 vezes menos** e pontua
**2,2 vezes mais devagar**. O produto dá 6,8 e o score difere 8,8 vezes: a
sobra é esperada, porque mediana de produto não é produto de medianas. O que
importa é a ordem de grandeza, e ela vem dos dois fatores.

E o número que explica tudo é o último: **73% contra 1% de pá erguida.**

Com as pás levantadas, elas ocupam fisicamente o buraco do dreno. A bola que ia
cair bate nelas e volta. **Não precisa de timing nenhum.** É bloqueio
permanente.

O agente mascarado tem a pá em repouso 99% do tempo, então o dreno fica aberto.

Testei o caso extremo: uma política que aperta **os dois flippers o tempo todo**,
sem exceção.

```
duração: 7.207 segundos
```

Duas horas de partida. Bateu o teto que eu tinha configurado. A bola
simplesmente **não drena**.

Aqui está a coisa que eu levei quinze passos de experimento para entender:

**Os flippers não pontuam.** Quem pontua no Space Cadet é a mesa, os bumpers,
as rampas, os alvos, as luzes. Os flippers só existem para manter a bola viva o
suficiente para a mesa fazer o trabalho.

Então, para estes agentes, **durar valeu mais que mirar**. O recorde humano de
126 milhões sugere que em outro regime de jogo a pontaria e a progressão
voltam a pesar.

E uma parede fixa dura mais que um taco preciso.

O agente base, que acerta a bola em apenas 2,3% dos apertos, descobriu isso
sozinho. Ele não é um jogador ruim que precisa de aula de mira. Ele é um
sobrevivente eficiente que eu estava tentando transformar em atleta.

Eu passei o projeto inteiro tratando pontaria como sinônimo de competência.
Nesses agentes, o placar recompensava muito mais permanência do que pontaria.

Depois disso, **duração virou métrica de primeira classe** em toda avaliação. Sem
ela, os testes anteriores estavam medindo a coisa errada: a queda de score do
experimento de custo de flipper se explica muito melhor pela perda de 41% de
duração do que por qualquer coisa sobre mira.

Antes de aceitar isso, tentei uma última coisa do lado da percepção. O agente não
consegue prever onde a bola vai estar; e se eu simplesmente **contar** para ele?

Acrescentei três campos à observação: quantos quadros até a bola cruzar a linha
dos flippers, onde ela vai cruzar, e se está descendo. É o que agentes de Pong e
Breakout fazem.

Verifiquei antes se a previsão era viável: extrapolação linear erra 4,5 pixels em
67 ms, e o raio da bola é 7 pixels. Cabe.

| | Pontaria | p |
|---|---|---|
| Punir acionamento | sem efeito | 0,97 |
| Premiar tacada | sem efeito | 0,21 |
| **Prever trajetória** | **+16,6%** | **0,0008** |

**Primeiro efeito significativo na pontaria em todo o projeto.** E ele conseguiu
isso **apertando menos** (11,7% menos acionamentos), o que é seleção, não volume.

Foi também o único tratamento que **não custou duração**.

```{=latex}
\begin{figure*}[tb]\centering
\includegraphics[width=13cm]{img/eda_efeitos.png}
\caption{Tamanho de efeito e significância de cada tratamento.}
\end{figure*}
```

O score? Empatou. Porque a essa altura já sabíamos por quê: melhorar a mira não
melhora o placar num jogo onde o placar depende de ficar vivo, e ele já estava no
teto de sobrevivência que a estratégia de parede permite.
