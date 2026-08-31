# RL no 3D Pinball Space Cadet

Um agente de RL que joga o pinball do Windows XP, treinado sobre uma
**decompilacao instrumentada** do jogo — o estado vem da fisica em C++, nao de
leitura de tela.

A pergunta que o projeto acabou respondendo nao foi "da para bater o recorde?",
e sim **"o agente e bom por competencia ou por velocidade de reflexo?"**.

## O resultado principal

O agente faz **2,6 milhoes** de pontos (mediana, partidas sem teto de tempo),
contra 404 mil de uma politica aleatoria. Parece competencia. Mas basta atrasar
as acoes dele para ver de onde vem a vantagem:

| Atraso | Score mediano | vs. acaso |
|---|---|---|
| 0 ms | 1.552.750 | 3,8x |
| 50 ms | 320.625 | 0,79x |
| **250 ms** (reacao humana) | **251.000** | **0,62x** |

**Com latencia humana, ele joga pior que apertar botao ao acaso.** Nao e um
declinio gradual: ja com 50 ms — cinco vezes mais rapido que uma pessoa — ele
perde 79%. A vantagem inteira vive numa janela que nenhum humano alcanca.

## O que sustenta essa conclusao

Cinco tratamentos independentes tentaram melhorar a **pontaria** (fracao de
apertos que conectam com a bola, 2,3% no agente base):

| Tratamento | Pontaria | Duracao | Score |
|---|---|---|---|
| Punir acionamento | sem efeito (p=0,97) | **-41%** | -56% |
| Premiar tacada | sem efeito (p=0,21) | -23% | -19% |
| Action masking | **+20x a +35x** | -66% | -83% |
| Credito local (gamma) | sem efeito | — | empate |
| **Prever trajetoria** | **+17% (p=0,0008)** | preservada | empate |

Nenhum sinal de recompensa move a pontaria; restringir a acao move muito. E
melhorar a pontaria **nao melhora o placar** — porque quem pontua nesta mesa e a
mesa (bumpers, rampas, alvos), e os flippers so mantem a bola viva. A politica
"segurar as duas pa's erguidas" sobreviveu **2 horas** sem perder a bola.

## Como rodar

```bash
# treinar (2,5M passos, ~1h em GPU)
python python/treinar_visao_par.py 2500000 minha_tag 6 score 0 0 0 0 0 0 True

# avaliar sem teto de tempo
python python/sem_teto.py ppo_minha_tag 10

# gerar clipes do agente jogando
python python/clipes.py ppo_minha_tag 6 12

# EDA comparando agentes
Rscript analise/eda_flip.R
```

`PINBALL_DEVICE=cpu` força CPU (a GPU de 4 GiB e compartilhada com o navegador e
ja matou um treino com OOM).

## Estrutura

```
python/        ambientes, treinadores, self-checks e medicoes
  spacecadet_gym.py    o gym.Env principal (visao, previsao, mascara, shaping)
  env_opcoes*.py       semi-MDP: o agente escolhe quanto esperar (linha encerrada)
  treinar_*.py         treinadores
  teste_*.py           self-checks com assert
  varre_*.py, spam.py  medicoes que antecedem treino
analise/       scripts R, graficos, CSVs e a zona do flipper
  midia/               clipes representativos
docs-ai/       estado, decisoes e dicionario de dados
SpaceCadetPinball/     fork instrumentado (repositorio proprio, branch rl-instrumentation)
```

## Metodo

Duas regras que emergiram do projeto e evitaram varios erros:

**Medir a frequencia do evento antes de treinar.** Ja evitou quatro treinos
inuteis — se o agente so ve o evento 3 vezes por partida, nenhum peso de
recompensa vai ensina-lo.

**Todo numero derivado precisa de controle contra o acaso.** O detector de
tacada por "salto de velocidade da bola" parecia funcionar e dava lift de apenas
1,15x sobre instantes aleatorios: media ruido, porque qualquer bumper acelera a
bola. Foi substituido por um contador lido da propria fisica do jogo.

Ver [docs-ai/DICIONARIO.md](docs-ai/DICIONARIO.md) para os campos e unidades, e
[docs-ai/DECISIONS.md](docs-ai/DECISIONS.md) para o historico de decisoes.
