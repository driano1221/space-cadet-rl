# A pergunta que eu não queria fazer

O agente estava fazendo 2,6 milhões de pontos. Bonito, 4,3 vezes o acaso,
com $p$ da ordem de $10^{-15}$. Eu já estava pensando em como postar isso.

(Um aviso sobre dois números que vão aparecer juntos: o 4,3x é da avaliação
que mediu o efeito da visão da mesa, e o 3,8x da tabela abaixo é da coleta de
latência. Mesma política, avaliações diferentes.)

Aí me veio uma dúvida que estragou a festa: **ele é bom, ou ele é só rápido?**

O agente toma 40 decisões por segundo. Uma pessoa tem tempo de reação de 200 a
300 milissegundos, o que dá três a cinco decisões por segundo. Ele não está
jogando o mesmo jogo que eu.

Dá para testar isso, e o teste é constrangedoramente simples: **atrasar as ações
dele**. A decisão continua sendo tomada olhando o estado atual, mas só é aplicada
$N$ passos depois. É uma aproximação simples de latência em escala humana. Não é simular uma
pessoa: ele continua emitindo comandos a 40 Hz, só que deslocados no tempo.

Implementei com uma fila. Cinco linhas de código.

| Atraso | Score mediano | Queda | Contra o acaso |
|---|---|---|---|
| 0 ms | **1.552.750** |, | 3,8x |
| 50 ms | 320.625 | −79% | 0,79x |
| 100 ms | 319.000 | −79% | 0,79x |
| 150 ms | 247.875 | −84% | 0,61x |
| **250 ms (humano)** | **251.000** | **−84%** | **0,62x** |
| 400 ms | 171.250 | −89% | 0,42x |

```{=latex}
\begin{figure}[tb]\centering
\includegraphics[width=8.5cm]{img/reacao.png}
\caption{Score por atraso de ação. A queda de 79\% acontece já com 50 ms, cinco vezes mais rápido que a reação humana.}
\end{figure}
```

Com latência na faixa humana, **ele deixa de superar até a política aleatória**.

Sessenta e dois por cento do aleatório. Ele perde para a moeda.

O formato da queda importa mais que o tamanho dela.

O que mais me pegou não foi a queda. Foi o formato dela.

Já com **50 milissegundos**, ainda cinco vezes mais rápido que qualquer pessoa
, ele perde 79%. Depois disso o desempenho fica num platô de 250 a 320 mil,
quase indiferente a mais atraso.

Ou seja: **toda a vantagem dele vive numa janela abaixo de 50 milissegundos**,
que nenhum ser humano alcança. Não é uma habilidade que degrada com latência. É
uma habilidade que **só existe** em altíssima frequência.

Esse resultado explica várias coisas soltas.

Esse resultado explica, de uma vez, um monte de coisa que eu tinha observado
solta:

Ele não faz *cradle* (a técnica de segurar a bola para mirar) numa taxa acima do
acaso. Não completa missões nem trincas. Reward shaping muda o que ele *tenta*,
mas não o que ele *consegue*. Adicionar memória temporal não acrescenta nada.

Tudo isso apontava para a mesma conclusão sem prová-la: **a competência dele é
motora, não tática.** Faltava a medida direta, e ela é essa.

Na mesma coleta eu medi que ele passa pela rampa de lançamento 3,7 vezes por
partida, uma a cada 72 segundos. Ele **não descobriu** o loop de pontuação que as
regras da mesa descrevem. Não há estratégia deliberada ali.

Porque quase nenhum projeto de bot faz essa pergunta.

O padrão do gênero é: treina, mostra o número grande, compara com humano ou com
random, posta o vídeo. Ninguém pergunta se o agente é bom **por mérito ou por
velocidade de reflexo**, porque a resposta pode estragar a demonstração.

Estragou a minha. E virou a coisa mais interessante que eu tinha para contar.

Também responde, em parte, uma pergunta que ficou em aberto: eu cheguei a montar
um gravador para registrar partidas minhas e usar como régua humana, e depois
desisti de gravar. Como eu não cheguei a coletar uma linha de base
humana, o que dá para afirmar é o que está medido: sob latência nessa faixa,
o agente cai abaixo do acaso.

Ele é um controlador reativo de altíssima frequência, não um jogador de pinball.
