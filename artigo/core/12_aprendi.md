# O que eu aprendi (e os erros que quase publiquei)

Terminei o projeto sem bater o recorde do jogo. O agente faz 2,6 milhões, o
recorde é 126 milhões, e eu documentei em detalhe por que a distância não fecha.

Mas saí com um punhado de coisas que valem mais do que o número teria valido.

**Medir a frequência do evento antes de treinar.** Um script de cinco minutos
substitui uma hora de GPU. Evitou quatro treinos inúteis.

O caso mais didático: eu tinha medido "11,5 das 18 luzes acendem por partida" e
li como sinal denso. Era **valor acumulado**, não frequência. O progresso de rank
muda uma ou duas vezes por partida, sinal 200 vezes mais esparso que o score. Eu
estava tentando curar esparsidade com algo ainda mais esparso.

A faixa que funciona neste ambiente fica entre 30 e 1.000 passos entre eventos.
Acima de 3.000, o desconto come o crédito antes de chegar na ação que causou.

**Avaliação lado a lado, no mesmo processo.** A variância entre execuções é de
40%, e comparar duas avaliações rodadas em momentos diferentes não significa
nada. Todos os números deste documento vêm de agentes avaliados em série, no
mesmo processo, com Mann-Whitney entre as amostras. Os episódios não
compartilham semente, então não é um teste pareado no sentido estatístico.

**Controle contra o acaso em toda métrica derivada.** Meu detector de tacada por
"salto de velocidade" parecia funcionar e era ruído (1,15 vezes o acaso). Se eu
não tivesse comparado contra instantes aleatórios, teria construído a máscara
inteira sobre uma medição vazia.

Sendo honesto, porque a lista é mais útil que a dos acertos.

**Confundi valor acumulado com frequência.** Já contei. Custou um treino e uma
conclusão errada.

**Li um saldo como contador.** O campo `ExtraBalls` desce quando você usa a bola.
Reportei "zero bolas extras" pelo motivo errado; o zero se confirmou por sorte.

**Calculei uma distância com eixos de escalas diferentes.** Fiz hipotenusa de dois
valores normalizados por constantes distintas. O resultado dizia que o agente
aciona *menos* com a bola perto, o que contradizia um fato já medido. A métrica
estava errada, não o agente. Trocando por uma grade em quantis, o sinal apareceu
na hora.

**Assumi que o jogo rodava a 40 quadros por segundo.** Roda a 120. Durante horas
reportei taxas com fator 3 de erro, todas internamente consistentes e todas na
unidade errada. Só descobri porque alguém estranhou que os GIFs pareciam lentos.

**Deixei uma brecha na penalidade e ele fugiu por ela.** Cobrei o acionamento e
não o hold, "para proteger o trapping". Ele segurou a pá 45% mais tempo.

**Quebrei um teorema achando que estava corrigindo.** Tirei o $\gamma$ do shaping
por potencial e com isso removi exatamente a garantia que eu queria invocar.
Descobri numa auditoria, depois de já ter afirmado que "a teoria valeu".

**Comparei réguas diferentes três vezes.** A avaliação interna do treinador (n=6)
contra a avaliação em série (n=10). Números diferentes por construção, e eu li
como diferença de desempenho.

Todos esses estão registrados com a correção, o que é a única coisa que os torna
úteis.

**Instrumentar vale muito mais que fotografar a tela.** A instrumentação leva a
física a até 941 vezes o tempo real, e o treino completo a cerca de 17 vezes.
É a diferença entre rodar dez experimentos e rodar um.

**Cheque a percepção antes do algoritmo.** Quatro treinos abaixo do acaso viraram
4,3 vezes acima só por colocar a mesa na observação. Nenhum hiperparâmetro faria
isso.

**Desconfie do resultado bom.** Toda vez que um número me surpreendeu para cima,
tinha erro atrás. Toda vez.

**Assista ao agente jogar.** Os dois bugs mais caros do projeto foram encontrados
olhando vídeo, não tabela: o spam de flipper e a pá errada sendo acionada. Métrica
agregada não mostra isso.

**Pergunte se o seu agente é bom ou só rápido.** Esse teste custou cinco linhas de
código e produziu o resultado mais interessante que eu tinha.

O agente do Space Cadet não vai bater recorde nenhum. Com 250 ms de latência de
ação, na faixa usada como referência humana, ele perde para uma moeda.

Mas ele me ensinou que quem pontua no pinball é a mesa, que uma pá parada vale
mais que um taco preciso, e que a coisa mais difícil de um projeto de RL não é
fazer o agente aprender, é descobrir o que você estava medindo errado o tempo
todo.

E o viking continua lá, pilotando a nave.

Se você for instrumentar um jogo para treinar um agente, quatro coisas que eu
faria diferente desde o começo:

1. **Leia a taxa de quadros do código, não do seu chute.** Assumi 40 por segundo
   num jogo que roda a 120, e reportei taxas com fator 3 de erro por horas.
2. **Escreva o script de medição antes do de treino.** Se o evento que você quer
   recompensar acontece três vezes por partida, nenhum peso vai ensiná-lo.
3. **Compare lado a lado, no mesmo processo.** A variância entre execuções aqui é
   de 40%: duas avaliações rodadas em momentos diferentes não dizem nada.
4. **Assista ao agente jogar.** Os dois bugs mais caros deste projeto foram
   encontrados olhando vídeo, não tabela.

## Nota sobre método e ferramentas

Cada tratamento foi treinado uma vez, com semente fixa, e avaliado em 10
episódios completos. Isso caracteriza bem *aquela política treinada*, mas não
substitui várias execuções independentes de treino: onde o texto diz que um
tratamento causou um efeito, leia "nesta execução, mantendo os demais
componentes fixos".

Os p-valores da última rodada são exploratórios e não foram corrigidos para
múltiplas comparações: com cinco testes contra o mesmo controle, valores como
0,043 e 0,015 não devem ser lidos como evidência confirmatória forte.

O código do projeto reúne o ambiente instrumentado, os treinadores, os scripts
de medição e os dados brutos das avaliações, com um `README` trazendo os
comandos mínimos para compilar e treinar. O endereço do repositório entra aqui
na publicação.

Claude (Anthropic) foi usado como apoio em programação, revisão e discussão
durante o desenvolvimento e a escrita.
