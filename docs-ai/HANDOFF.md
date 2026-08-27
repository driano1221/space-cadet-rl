# Handoff

## Objetivo atual

Sair de "coleta de resultado final" para "coleta de trajetoria", que e' o que
destrava treinar um agente.

## Onde mexer

Tudo relevante esta em `SpaceCadetPinball/SpaceCadetPinball/rlmode.cpp`.

Pontos de entrada da decompilacao ja mapeados:

| O que | Onde |
|---|---|
| Passo de fisica | `pb::frame(float dtMilliSec)` |
| Aplicar acao | `MainTable->Message(MessageCode::LeftFlipperInputPressed, pb::time_now)` |
| Codigos de acao | `TPinballComponent.h`, 1000 a 1005 |
| Fim de episodio | `pb::game_mode == GameModes::GameOver` |
| Iniciar partida | `pb::replay_level(false)` |
| Soltar plunger | `pb::launch_ball()` |
| Bola | `TBall`: `Position`, `Direction`, `Speed` (publicos) |
| Placar e bolas | `TPinballTable`: `CurScore`, `BallCount`, `ScoreMultiplier` |
| Luzes | `TPinballTable::LightGroup` |
| Bolas em jogo | `TPinballTable::BallList` |

## Comandos

```powershell
cd SpaceCadetPinball
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

```bash
cd SpaceCadetPinball/bin/Release
SDL_VIDEODRIVER=dummy ./SpaceCadetPinball.exe -rl-episodes 300 -rl-seed 42 -rl-policy 1
```

O cmake fica em
`C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin`.

## Riscos

- **Nao confiar em numero novo sem rodar as politicas 0 e 2 como controle.**
  Se as distribuicoes ficarem parecidas, o input parou de chegar ao jogo.
- Conferir o `n` de cada grupo antes de comparar: ja aconteceu de um teste
  sobrescrever CSV e a comparacao rodar com n=20 contra n=300.
- Trajetoria completa a 120 passos/s gera arquivo grande. Amostrar.
- **Duracao alta com score baixo e' o berco, nao bom desempenho.** Sempre
  conferir velocidade mediana da bola e % do tempo no topo da mesa.
- Baselines de resolucoes diferentes nao sao comparaveis: mudar
  `quadros_por_passo` muda tambem o score do aleatorio.

## Proximo passo

**Dar visao da mesa ao agente.** Hoje a observacao tem 15 numeros sobre bola e
flippers e nada sobre alvos, rampas ou bumpers - o agente nao pode aprender a
mirar no que nao percebe. O caminho e' uma observacao em grade 2D (canais para
posicao da bola e luzes acesas) com CNN, como o projeto do Antiyoy fez.

Ja existe `tela_x`/`tela_y` no estado, projetados pelo proprio jogo, o que
facilita montar a grade.

Antes disso, dois itens baratos:

- **bloquear o berco**: penalizar bola parada perto dos flippers, ou encerrar o
  episodio quando a velocidade ficar abaixo de um limiar por N segundos;
- **usar 25 ms** (`quadros_por_passo=3`) em tudo - a 50 ms o baseline cai 40%.

Duas acoes do jogo continuam sem exposicao: **nudge**
(`nudge::nudge_left/right/up`) e **plunger modulado** - `pb::launch_ball()`
sempre usa `Boost = MaxPullback`, forca maxima, mas o jogo permite modular pelo
tempo entre `PlungerInputPressed` e `PlungerInputReleased`.
