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
