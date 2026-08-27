# Proximos passos (ordem acordada em 2026-08-27)

## 1. Medir o rank que o agente atinge hoje

Quantifica a distancia real ate' o recorde humano (126 milhoes). O rank e' legivel
sem instrumentacao nova pesada: os grupos de luzes `middle_circle` (rank, 0-9) e
`outer_circle` (progresso dentro do rank) sao acessiveis por
`TPinballTable::find_component("middle_circle")` e respondem a
`MessageCode::TLightGroupGetOnCount`.

## 2. Expor `render::vscreen` e refazer o GIF

O GIF atual desenha um circulo sobre o bitmap estatico da mesa: nao mostra
flippers, luzes nem sprites. `render::vscreen` e' o framebuffer que o jogo
compoe de fato (`render.h:40`, `gdrv_bitmap8*`). Expondo esses pixels, a
animacao vira captura real.

## 3. Recompensar progresso de rank e retreinar

E' o passo com chance de mudar a ordem de grandeza do score.

---

# Como o jogo realmente pontua

Levantado das regras da tabela. Explica por que o agente para em ~1,9 milhao
enquanto o recorde humano e' 126 milhoes: **ele joga o jogo basico**.

## Pontos por evento

| Evento | Pontos |
|---|---|
| Attack bumper | 500 |
| Hyperspace nivel 1 | 10.000 |
| Hyperspace nivel 2 (jackpot) | 20.000 |
| Black hole kickout | 20.000 |
| Hit streak bonus | 25.000 |
| Skill shot (no lancamento) | 7.500 a 75.000 |
| Gravity well | 100.000 |
| **Completar missao** | **500.000 a 1.000.000+** |
| **Jackpot Maelstrom** | **500.000** |

## Multiplicadores (o que escala de verdade)

- **Field Multiplier Target**: derrubar os 3 alvos multiplica os pontos de
  ataque em **2x, 3x, 5x e 10x**.
- **Weapon upgrade**: acender as 3 luzes da reentry lane **dobra** o valor do
  bumper. Ate' 3 upgrades (azul -> verde -> amarelo -> vermelho). Expira em 60 s.

## As missoes do primeiro rank sao simples

Isto e' o mais acionavel de tudo. No rank inicial (Candidate) as missoes sao:

| Missao | Objetivo |
|---|---|
| Launch training | acertar o launch pad **3 vezes** |
| Reentry training | acertar a reentry lane **3 vezes** |
| Target practice | acertar o attack bumper **8 vezes** |
| Science | derrubar o falling target **9 vezes** |

Sao coisas que o agente ja faz por acidente. O que falta e' o **fluxo**: acertar
o mission target (16) para escolher a missao e depois passar pelo launch pad
(11) para aceita-la. Sem isso os acertos nao contam para nada.

## Combustivel

Missoes consomem combustivel; se acabar, a missao aborta. Recarrega passando
pelo launch pad ou acertando o fuel target.

## Cheat keys uteis para experimentacao

Digitadas durante a espera do lancamento:

- `bmax` - bolas infinitas. Util para treinar sem o episodio terminar.
- `RMAX` - sobe um rank na hora. Util para testar comportamento em ranks altos
  sem precisar jogar ate' la'.
- `1max` - adiciona uma vida.
- `gmax` - ativa o centro de gravidade.

## Nudge tem custo

As teclas de empurrar (`x` e `.`) nao podem ser usadas em sequencia: gera falta,
acende a luz de foul, **trava os controles e a bola cai**. Se o nudge for
exposto como acao, o agente precisa da penalidade no modelo, senao vai abusar.

## Loop conhecido

As regras mencionam que, com timing dominado, da' para pontuar quase
indefinidamente mandando a bola para a area do launch pad repetidamente. Vale
verificar se o agente descobre isso sozinho - seria outro caso de exploracao.
