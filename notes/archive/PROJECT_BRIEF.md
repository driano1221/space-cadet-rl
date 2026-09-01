# Project Brief - Space Cadet instrumentado

## Objetivo

Transformar o *3D Pinball Space Cadet* num ambiente de geracao de dados, treinar
um agente e - o diferencial - **analisar o agente com rigor estatistico**, coisa
que nenhum projeto publico do genero fez.

## Origem da ideia

Adriano assistiu ao video *"Mastering the Hex: A Case Study in Reinforcement
Learning for Strategy Games"*, do Simon, sobre um bot para o jogo Antiyoy. O
projeto do video fracassou no objetivo declarado, mas virou bom conteudo pela
honestidade. A ideia foi fazer algo parecido com um jogo nostalgico.

## Por que pinball e' mais tratavel que Antiyoy

| | Antiyoy | Space Cadet |
|---|---|---|
| Espaco de acao | ~4.000 acoes, precisa de mascara | **2 botoes binarios** |
| Horizonte de credito | turno 5 decide a partida no turno 80 | pontos em segundos |
| Estrutura | estrategia por turnos, multiagente | controle reativo |

Alem disso, o Simon precisou **recriar o jogo do zero em Pygame** porque o
original era Java. Aqui a decompilacao ja existe e e' fiel ao binario original.

## O diferencial pretendido

Score de pinball tem cauda pesada. Comparar agentes por media aritmetica e' erro
- as caudas dominam. Separar habilidade de sorte, quantificar incerteza e modelar
a distribuicao e' terreno de estatistico. Projetos amadores de RL reportam
"recompensa media subiu" e param ai.

## Escopo em camadas

Cada camada e' entregavel sozinha, para o projeto nao depender do sucesso do RL
(que foi o erro do Simon):

1. **Ambiente instrumentado** - FEITO. ~1.000x tempo real, deterministico,
   exposto como `gym.Env` via pybind11.
2. **Baseline estatistico do jogo** - FEITO. Distribuicao de score (cauda
   pesada), curva de resolucao temporal, fronteira sobreviver x pontuar e a
   caracterizacao do berco.
3. **Agente RL** - FEITO. Supera o aleatorio em **4,3x** (1.740.875 contra
   404.375, p = 5,7e-15) depois que passou a enxergar a mesa.

O que segue agora nao e' mais "fazer funcionar", e' **escalar**: o agente joga
o jogo basico e ignora missoes e multiplicadores, que e' onde estao as ordens de
grandeza. Ver `PROXIMOS_PASSOS.md`.

## Resultado alcancado (2026-08-30)

O objetivo declarado - **analisar o agente com rigor estatistico** - foi
cumprido, e produziu um achado que os projetos publicos do genero nao reportam.

**O agente faz 4,3x o acaso, mas por reflexo, nao por estrategia.** Impondo
250 ms de atraso (a latencia de uma pessoa) ele cai para 62% da politica
aleatoria. A vantagem esta toda na janela abaixo de 50 ms.

Isso e' coerente com o resto: nao completa missoes, nao fecha trincas do
multiplicador, nao faz *cradle* mais que o acaso, e nao descobriu o loop de
pontuacao das regras. A competencia e' motora, nao cognitiva.

Quatro hipoteses foram testadas para o teto de ~1,7 milhao; tres descartadas com
dados (escala, incentivo, memoria) e uma bloqueada por hardware (off-policy).

Ao longo do caminho, dois resultados de valor proprio: **reward hacking
demonstrado com controle limpo** (duas IAs identicas, objetivos opostos, mesma
duracao, 23x de diferenca no score) e um **ambiente de RL inedito** sobre a
decompilacao do jogo.
