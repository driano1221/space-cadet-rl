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

## Proximo passo

Implementar o binding Python (pybind11) e o wrapper `gym.Env`, fechando o
loop para treinar um agente de verdade. A coleta de trajetoria ja esta pronta.
