# A caçada ao teto

O agente parava em torno de 1,7 milhão de pontos e não passava dali, treinasse o
que treinasse. Virou obsessão descobrir por quê.

Listei as hipóteses e fui testando uma por uma.

**Percepção.** Era isso, em parte: a visão da mesa deu 4,3 vezes o acaso.

**Escala de treino.** Descartada. 2,5, 5 e 7,5 milhões de passos sem diferença.

**Incentivo.** Descartada, com três shapings diferentes testados.

**Memória temporal.** Descartada: a AUC vai de 0,847 para 0,859 e satura.

**Algoritmo off-policy.** Bloqueado por hardware: o buffer estimado ficaria em
cerca de 68 GB de RAM, acima da memória disponível na máquina.

O teste de memória temporal merece nota. A intuição diz que o agente precisa lembrar
do passado para jogar bem. Testei empilhar quadros e medir quanto isso melhora
uma tarefa auxiliar: prever o estado seguinte. A métrica é a AUC dessa
previsão, e ela vai de 0,847 para 0,859 antes de saturar.

Nesse teste, acrescentar histórico rendeu quase nada, o que sugere que posição
e velocidade já carregam boa parte da informação relevante. Não é prova formal
de que o estado é markoviano, mas indica que memória longa não é onde está o
gargalo.

Fui atrás das mecânicas que valem os pontos grandes.

Fui investigar as mecânicas avançadas do jogo, aquelas que valem os pontos
grandes, e medi quantas vezes ele consegue cada uma:

**Alvos de missão: 9,8 por partida.** Exigem um tiro só, e ele acerta.

**Medal targets: 7,3 por partida**, o que dá 2,4 conjuntos. A bola extra exige
três conjuntos completos.

**Hyperspace: 3,2 entradas.** O Center Post ativa na quarta, o Gravity Well na
quinta. Ele para logo antes das duas.

**Missões completas: 0,6 por partida.** Cada uma é uma sequência longa.

**Bolas extras: zero.** Dependem dos três conjuntos de medal.

O padrão salta aos olhos: **ele executa sequências de três passos e trava nas de
nove.**

Chega a 2,4 conjuntos de medal targets por partida. A bola extra exige três.
Para a um conjunto de distância, partida após partida.

E tem uma explicação quantitativa direta, aquela conta do desconto do capítulo
sobre RL: com $\gamma = 0{,}995$ e 40 decisões por segundo, um evento a 60
segundos de distância vale 0,0006% da recompensa. Nove eventos encadeados não
deixam nenhum crédito chegar de volta às ações que iniciaram a sequência.

Não é falta de habilidade. É que o sinal chega muito fraco.

```{=latex}
\begin{figure}[tb]\centering
\includegraphics[width=8.5cm]{img/rank.png}
\caption{Progressão de rank: onde estão as ordens de grandeza que faltam.}
\end{figure}
```

Nessa investigação eu reportei "zero bolas extras" com bastante confiança.
Estava certo, mas pelo motivo errado.

Eu estava lendo o campo `ExtraBalls` no fim do episódio. Só que esse campo é um
**saldo**, não um contador: ele sobe quando você ganha e **desce quando você
usa**. Um agente que ganhasse duas bolas extras e usasse as duas terminaria com
zero, exatamente igual a um que nunca ganhou nada.

Adicionei um contador de concessões dentro do C++, na função que concede a bola.
O zero se confirmou. Mas se não tivesse confirmado, eu teria publicado um número
errado com toda a certeza do mundo.

Com o teto diagnosticado, medi a distância até o recorde do jogo. Dez partidas
**sem limite de tempo**:

```
mediana  2.637.750       máximo  6.712.000
duração  375 s           acima de 5M: 1 em 10
ritmo    6.024 pontos por segundo
```

O recorde humano é **126 milhões** [@recorde]. Estamos 48 vezes longe pela mediana, 19 pelo
melhor caso.

Nenhuma das dez partidas bateu o teto de duas horas que eu tinha configurado.
Todas terminam por **bolas esgotadas**. O limite não é tempo, é a regra das três
bolas.

No ritmo dele, 126 milhões sairiam em 5,8 horas de jogo ininterrupto. Sem bolas
extras confiáveis, não existe partida de horas. E sem partida de horas, não
existe recorde.

Um detalhe que contraria o resto: a partida de 1.772.500 chegou ao **rank 6**, o
mais alto que vi. A de 6.712.000 ficou no rank 3.

**Pontuar alto e progredir de rank são caminhos diferentes**, e ele nunca faz os
dois na mesma partida. Quem sobe de rank gasta tempo em missões; quem pontua
fica batendo em bumpers.
