# O berço, ou como o agente me enganou

Em algum momento eu tive uma ideia que parecia esperta: e se em vez de
recompensar pontos, eu recompensasse **sobreviver**? Pinball é um jogo de manter
a bola viva. Dá 0,01 por passo em que a bola não drenou e deixa ele descobrir o
resto.

Rodei. Olhei o resultado: **758 segundos de partida**. Doze minutos e meio sem
perder a bola, contra os 292 segundos do agente normal.

Fiquei orgulhoso por uns bons trinta segundos, até olhar o placar: **19 mil
pontos**.

Fui entender o que tinha acontecido.

Com os dois flippers erguidos ao mesmo tempo, a bola fica **apoiada e imóvel**
entre eles. Não desce. Não drena. A partida simplesmente não acaba.

Ele encontrou um estado absorvente do jogo e se instalou lá.

Chamei isso de **berço**, e as métricas dele são inconfundíveis:

| | Velocidade da bola | Tempo quase parada | Tempo no topo |
|---|---|---|---|
| **Berço** | **0,13** | **94,1%** | **2,2%** |
| Aleatório | 9,49 | 10,9% | 20,7% |
| Agente que joga | 10,48 | 6,9% | 22,9% |

A bola passa 94% do tempo praticamente parada. Ela nem está em jogo.

O detalhe que mais me impressionou: eu tinha escrito **à mão** uma heurística
defensiva para testar o berço, e o agente ficou **melhor que ela**, velocidade
0,13 contra 0,17, 94,1% parado contra 82,7%. Ele não copiou um truque
conhecido. Redescobriu e **otimizou** o atalho partindo de pesos aleatórios,
recebendo só "0,01 por passo vivo".

Depois disso montei o experimento mais limpo do projeto. Dois agentes, tudo
idêntico, mesma visão, mesma CNN, mesmos 2,5 milhões de passos. **Só a
recompensa muda.**

| | Score puro | Sobrevivência pura |
|---|---|---|
| Score mediano | 1.740.875 | **76.000** |
| Duração | 292 s | **307 s** |
| Velocidade da bola | 10,48 | **0,13** |
| Tempo quase parada | 6,9% | **94,1%** |
| Tempo no topo | 22,9% | **2,2%** |

O que faz esse par funcionar é a linha da duração. Eu esperava que o agente de
sobrevivência durasse *muito* mais, o que abriria a objeção óbvia: "claro que ele
pontua menos, jogou diferente".

Mas eles duram **praticamente o mesmo**. 307 contra 292 segundos.

A diferença de **23 vezes** no score vem do que cada um faz com o mesmo tempo
de jogo. A duração praticamente igual elimina a explicação mais óbvia para a
diferença. Duas inteligências idênticas, objetivos opostos, e uma delas passa
a partida abraçada na bola.

```{=latex}
\begin{figure*}[tb]\centering
\includegraphics[width=13cm]{img/conflito_sobreviver_pontuar.png}
\caption{Varredura da probabilidade de manter o flipper pressionado. Score e sobrevivência apontam para lados opostos, e de 95\% para 100\% o score cai 15 vezes.}
\end{figure*}
```

Fui medir onde exatamente está a armadilha. Varri a probabilidade de apertar o
flipper, 150 partidas por nível:

| Probabilidade | Score mediano | Duração |
|---|---|---|
| 0% | 145.125 | 90 s |
| **30%** | **413.625** | 162 s |
| 50% | 401.875 | 168 s |
| 95% | 247.375 | 314 s |
| 100% | **16.000** | 597 s |

De 95% para 100% o score cai **15 vezes**.

Isso me surpreendeu. Eu imaginava uma ladeira suave rumo ao berço, um agente
ficando progressivamente mais defensivo. Não é. É **falésia**: um ponto isolado
no extremo, e o caminho até o ótimo (por volta de 30%) é gradiente monotônico
bem-comportado.

```{=latex}
\begin{figure*}[tb]\centering
\includegraphics[width=16.9cm]{img/mapa_mesa.png}
\caption{Onde a bola passa o tempo, por política. As duas manchas escuras sobre os flippers, no painel da direita, são o berço: a bola parada entre as pás.}
\end{figure*}
```

Quatro caminhos diferentes caem nesse buraco: bônus por passo vivo, política
de flipper travado, heurística escrita à mão, e agente de RL treinado só com
sobrevivência. Não é bug do meu código. É propriedade do jogo.

E o paper da CMU, em outra mesa, com outro engine, descreve a mesma coisa.
