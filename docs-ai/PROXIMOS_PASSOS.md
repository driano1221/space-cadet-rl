# Proximos passos

Situacao em 2026-08-27.

| # | Passo | Status | Resultado |
|---|---|---|---|
| 1 | Medir o rank atual | **feito** | 11,6x mais pontos que o acaso, mesmo rank |
| 2 | Expor `render::vscreen` | **feito** | captura real; GIF com flippers e luzes |
| 3 | Recompensar progresso de rank | **feito, falhou** | sinal 180x mais esparso que o score |
| 4 | Fluxo de missao | **feito, funcionou** | alvos +31% (p=0,030), score inalterado |
| 5 | Multiplicadores (2x a 10x) | pendente | maior potencial de escala restante |
| 6 | Loop do launch pad | pendente | verificar se o agente descobre sozinho |
| 7 | Nudge, com penalidade de falta | pendente | acao que existe e nao esta exposta |
| 8 | Tempo de reacao variavel | pendente | ideia do Adriano; handicap e regularizacao |
| 9 | Escala de treino | pendente | 2,5M passos e' ~5% do orcamento tipico de Atari |

---

## 1. Medir o rank que o agente atinge hoje — CONCLUIDO

Quantifica a distancia real ate' o recorde humano (126 milhoes). O rank e' legivel
sem instrumentacao nova pesada: os grupos de luzes `middle_circle` (rank, 0-9) e
`outer_circle` (progresso dentro do rank) sao acessiveis por
`TPinballTable::find_component("middle_circle")` e respondem a
`MessageCode::TLightGroupGetOnCount`.

## 2. Expor `render::vscreen` e refazer o GIF — CONCLUIDO

O GIF atual desenha um circulo sobre o bitmap estatico da mesa: nao mostra
flippers, luzes nem sprites. `render::vscreen` e' o framebuffer que o jogo
compoe de fato (`render.h:40`, `gdrv_bitmap8*`). Expondo esses pixels, a
animacao vira captura real.

## 3. Recompensar progresso de rank — CONCLUIDO, NAO FUNCIONOU

E' o passo com chance de mudar a ordem de grandeza do score.

## 4. Ensinar o fluxo de missao — CONCLUIDO, FUNCIONOU

Nao e' habilidade que falta ao agente, e' **protocolo**. As missoes do primeiro
rank sao coisas que ele ja faz por acidente (acertar o bumper 8 vezes); o que
ele desconhece e' o ritual de **acertar o mission target (16) e depois passar
pelo launch pad (11)** para que os acertos passem a contar.

Caminho sugerido:

1. expor no estado: rank, progresso no rank, missao ativa e combustivel;
2. recompensa em camadas - pontos, mais um bonus por luz de progresso acesa,
   mais um bonus grande por missao completada;
3. avaliar com `bmax` (bolas infinitas) para separar "aprender a pontuar" de
   "aprender a nao morrer" - sao dois problemas e hoje estao misturados.

## 5. Multiplicadores (barato e escala muito)

- **Field Multiplier**: derrubar 3 alvos multiplica os pontos de ataque em
  2x, 3x, 5x e **10x**;
- **Weapon upgrade**: 3 luzes da reentry lane dobram o bumper, ate' 3 vezes.

Sao alvos fisicos que o agente ja consegue acertar. Basta que a recompensa
sinalize que valem mais do que parecem no curto prazo.

## 6. Verificar se o agente descobre o loop do launch pad

As regras mencionam pontuacao quase indefinida mandando a bola repetidamente a
area do launch pad. Se ele achar isso sozinho, e' mais um caso de exploracao
para documentar - na mesma familia do berco.

## 7. Nudge, com cuidado

`nudge::nudge_left/right/up` existe e nao esta exposto. Mas uso em sequencia
gera falta: trava os controles e derruba a bola. So' expor junto com a
penalidade modelada, senao o agente se sabota.

## 9. Escala de treino

2,5M passos sao ~1,8M frames com `quadros_por_passo=3`. Projetos de Atari usam
50M. Estamos com cerca de 5% do orcamento tipico, e nunca testamos se o
desempenho satura ou continua subindo. E' o experimento mais simples que resta:
mesma configuracao vencedora, 10M passos, e comparar.

## 8. Tempo de reacao variavel (ideia do Adriano)

Hoje o agente decide a cada 25 ms, sempre, com precisao perfeita. Um humano tem
latencia de 200-300 ms e ela **varia**. Duas leituras, e as duas valem
experimento:

**Como handicap** - injetar atraso entre a decisao e a acao chegar ao jogo,
para medir quanto do desempenho vem de reflexo sobre-humano e quanto vem de
estrategia. Se o agente cair para o nivel humano com 250 ms de atraso, boa parte
da vantagem dele e' velocidade, nao entendimento do jogo.

**Como regularizacao** - variar o intervalo durante o treino (por exemplo,
sortear entre 17 e 42 ms a cada episodio) forca o agente a nao depender de
timing exato. E' analogo a domain randomization em robotica, e costuma produzir
politicas mais robustas.

Vale medir tambem a **curva de degradacao**: score em funcao do atraso imposto.
Ela diz onde esta o limite entre "joga bem" e "so' reage rapido" - e e' um
grafico bom de portfolio, porque situa o agente contra a capacidade humana.

Depende do benchmark de resolucao ja feito (25 ms e' o otimo sem atraso).

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
