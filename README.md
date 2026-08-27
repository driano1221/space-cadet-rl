# Space Cadet Pinball como ambiente instrumentado

Experimento de engenharia reversa aplicada: transformar o *3D Pinball for
Windows - Space Cadet* num ambiente que gera dados em massa, para depois
treinar e **analisar estatisticamente** um agente.

> **Status: experimento validado, ainda nao e' projeto.**
> A coleta de dados funciona. Nao existe agente treinado.

## O resultado que justifica o experimento

| Metrica | Valor |
|---|---|
| Velocidade de simulacao | **941x tempo real** |
| Episodios por segundo | 5,6 |
| 1000 partidas completas | 3 minutos (46 h de tempo de jogo) |
| Determinismo | mesma semente produz CSV identico byte a byte |

Para comparacao, o projeto publico mais proximo
([space-cadet-nn](https://github.com/angelowilliams/space-cadet-nn)) leva
**20 minutos para 20 partidas** usando captura de tela.

## Estrutura

```text
SpaceCadetPinball/   decompilacao (k4zmu2a) + instrumentacao propria
  SpaceCadetPinball/rlmode.cpp    modo headless de coleta (~140 linhas)
analise/             scripts R e dados gerados
  dados/             CSVs das rodadas
  scripts/           utilitarios de conferencia em Python
docs-ai/             contexto para retomar o trabalho
```

## Como reproduzir

Compilar (precisa de Visual Studio 2022 e das libs SDL2 em `Libs/`):

```powershell
cd SpaceCadetPinball
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

Coletar dados (o `PINBALL.DAT` precisa estar junto do executavel):

```bash
cd SpaceCadetPinball/bin/Release
SDL_VIDEODRIVER=dummy ./SpaceCadetPinball.exe -rl-episodes 1000 -rl-seed 42 -rl-policy 1
```

Politicas: `0` nunca aperta, `1` aleatoria, `2` sempre apertado.
Adicione `-rl-trace 6` para gravar tambem a trajetoria (uma linha a cada 6
passos), ou `-rl-prob 30` para fixar a probabilidade de apertar em 30%.
As duas degeneradas existem como **controle**: se o input parar de chegar ao
jogo, as tres distribuicoes de score ficam iguais.

Analisar:

```bash
cd analise
Rscript baseline.R        # distribuicao do baseline aleatorio
Rscript validacao.R       # as tres politicas de controle
Rscript conflito.R        # varredura de agressividade
python validacao_visual.py  # densidade e trajetoria sobre a mesa
```

## Validacao

A trajetoria de uma partida sobre a mesa real. A bola sobe pelo canal do plunger
a direita (linha ciano, o inicio), curva no topo e entra na mesa - a fisica e' a
do jogo original, nao uma aproximacao.

![trajetoria](analise/validacao_trajetoria.png)

Densidade de posicoes por politica: os obstaculos aparecem como regioes frias.

![densidade](analise/validacao_densidade.png)

## O conflito entre sobreviver e pontuar

Varrendo a probabilidade de apertar o flipper de 0 a 100%:

| Prob. apertar | Score mediano | Duracao (s) |
|---|---|---|
| 0% | 145.125 | 90 |
| **30%** | **413.625** | 162 |
| 50% | 401.875 | 168 |
| 95% | 247.375 | 314 |
| 100% | **16.000** | **597** |

![conflito](analise/conflito_sobreviver_pontuar.png)

De 95% para 100% o score cai 15x e a duracao dobra. Travar os flippers e' um
ponto isolado, nao um atrator suave: o caminho ate' o otimo (~30%) e' um
gradiente monotono.

## Creditos

Construido sobre a decompilacao
[k4zmu2a/SpaceCadetPinball](https://github.com/k4zmu2a/SpaceCadetPinball).
A instrumentacao esta na branch `rl-instrumentation`, em um unico commit.
