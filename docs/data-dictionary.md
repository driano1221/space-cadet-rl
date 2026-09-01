# Dicionario de dados

O que cada campo significa, em que unidade, e como foi medido. Toda conversao de
tempo usa **8,33 ms por quadro** (o jogo roda a 120 quadros/s, `kPassoMs` em
`rlenv.cpp`); assumir 40 quadros/s ja custou um dia de numeros errados.

## Estado exposto pelo jogo (`info` do env)

Vem da instrumentacao em C++, nao de leitura de tela.

| Campo | Unidade | Significado |
|---|---|---|
| `score` | pontos | placar do jogo, sem transformacao |
| `tempo_s` | segundos | tempo de jogo do episodio, calculado no C++ |
| `tela_x`, `tela_y` | pixels | posicao da bola na tela (600x416) |
| `bola_x/y`, `bola_vx/vy` | unidades do jogo | posicao e velocidade na fisica |
| `bola_speed` | unidades/quadro | modulo da velocidade |
| `bolas_restantes` | contagem | bolas ainda disponiveis (padrao 3) |
| `rank` / `rank_total` | 0-9 | progressao de patente; onde os milhoes viram dezenas |
| `progresso` / `progresso_total` | 0-18 | avanco dentro do rank atual |
| `multiplicador` | 1,2,3,5,10 | multiplicador de pontos ativo |
| `flip_esq_ang`, `flip_dir_ang` | 0-1 | angulo da pa (0 = repouso, 1 = erguida) |
| `bola_rel_esq_x/y`, `bola_rel_dir_x/y` | normalizado | posicao da bola relativa a cada pa. **Os eixos usam constantes de normalizacao diferentes** - nao calcular hipotenusa com eles |
| `tilt`, `nudge_count` | flag / contagem | estado de tilt e empurroes |

### Contadores de evento (`ev_*`)

Sao **acumuladores monotonicos**: o valor de interesse e a diferenca entre dois
instantes, nunca o valor absoluto.

| Campo | Incrementa quando |
|---|---|
| `ev_flip_acerto` | a pa **em movimento** toca a bola. Pa parada erguida nao conta |
| `ev_bumper` | a bola atinge um bumper |
| `ev_hyperspace` | entrada no hyperspace |
| `ev_medal` | um medal target e' derrubado |
| `ev_mission_target` | alvo de missao atingido |
| `ev_launch_ramp` | passagem pela rampa de lancamento |
| `ev_missao_completa` | missao concluida |
| `ev_extra_ganha` | bola extra **concedida** |

> `bolas_extras` e' **saldo**, nao contador: desce ao usar. Para contar
> concessoes, usar `ev_extra_ganha`.

## `analise/eda_episodios.csv`

Uma linha por episodio completo.

| Coluna | Unidade | Nota |
|---|---|---|
| `modelo` | texto | tag do agente |
| `score` | pontos | placar final |
| `duracao_s` | segundos | **metrica de primeira classe**: e' o que converte em pontos |
| `passos` | decisoes | passos do agente no episodio |
| `flipper_ligado` | fracao 0-1 | tempo com alguma pa erguida |
| `acionamentos_s` | por segundo | bordas solto->apertado |
| `tacadas_s` | por segundo | de `ev_flip_acerto` |
| `acerto_por_acionamento` | fracao | **pontaria**: fracao dos apertos que conectam. 2,3% no agente base |
| `ambos` | fracao 0-1 | passos com as duas pa's |

## `analise/eda_acionamentos.csv`

Uma linha por acionamento individual (413.978 na coleta dos sete agentes).

| Coluna | Nota |
|---|---|
| `lado` | `esq` ou `dir` |
| `rel_x`, `rel_y` | posicao da bola **no inicio do movimento**, nao no contato - inclui a antecipacao da pa |
| `bola_y` | altura na mesa (0 = topo) |
| `vel` | velocidade no momento |
| `acertou` | 1 se `ev_flip_acerto` subiu nos 3 passos seguintes |

## `analise/zona_flipper.json`

Zona onde a pa alcanca a bola, em celulas de 10 px, derivada das tacadas reais.

```
{"celula": 10, "zonas": {"esq": [[cx, cy], ...], "dir": [...]}}
```

Uma celula `(cx, cy)` cobre os pixels `[cx*10, cx*10+10) x [cy*10, cy*10+10)`.
As duas zonas **se sobrepoem ~60%** (a bola desce pelo mesmo funil), entao a
zona nao determina qual pa usar.

## Recompensa (treino) x metrica (avaliacao)

Distincao que importa ao ler qualquer resultado:

- **Avaliacao** usa `score` bruto. Comparacoes entre agentes sao sempre nisso.
- **Treino** usa `sqrt(ganho / 1000)` por passo, para conter a cauda pesada
  (jackpot de 75 mil ao lado de bumper de 500). Somar raizes nao e' a raiz da
  soma: 5 eventos de mil rendem 5,00 e um de 5 mil rende 2,24 - a funcao
  favorece pontuacao picada. A distorcao e' igual em todos os agentes.
