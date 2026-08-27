# Ambiente Gymnasium

```python
from spacecadet_gym import SpaceCadetEnv

env = SpaceCadetEnv(recompensa="score")   # ou "sobrevivencia"
obs, info = env.reset()
obs, rec, terminado, truncado, info = env.step(2)   # 0=nada 1=esq 2=dir 3=ambos
```

## Observacao (9 valores, normalizados)

posicao x/y da bola, velocidade x/y, modulo da velocidade, bolas restantes,
bolas em jogo, luzes acesas, multiplicador.

## Parametros

| Nome | Efeito |
|---|---|
| `recompensa` | `"score"` (ganho de pontos) ou `"sobrevivencia"` (fixo por passo) |
| `comprimir` | raiz quadrada no ganho, para domar a cauda pesada |
| `bonus_vivo` | bonus por passo vivo — **veja o aviso abaixo** |
| `quadros_por_passo` | quantos frames o C++ avanca por `step` (padrao 6) |

## Dois limites que voce precisa saber

1. **Uma instancia por processo.** O estado do jogo e' global no codigo
   original. Para paralelizar use `SubprocVecEnv`, nunca VecEnv em threads.
2. **O reset e' estocastico.** `seed` nao reproduz o estado inicial: o
   `replay_level` parte de onde a partida anterior terminou. A fisica e'
   deterministica; o ponto de partida varia.

## Aviso sobre `bonus_vivo`

Um bonus de apenas **0,02 por passo** foi suficiente para o PPO abandonar o jogo
e travar o flipper direito em 96,8% dos passos. Nessa configuracao, **93% da
recompensa acumulada vinha do bonus** e apenas 7% do score, que caiu 4,75x.

O parametro existe justamente para poder demonstrar esse efeito. Deixe em zero
se o objetivo for aprender a jogar.

## Visao da mesa

`SpaceCadetEnv(visao=True)` troca a observacao por um dicionario:

| chave | forma | conteudo |
|---|---|---|
| `grade` | 8 x 36 x 28 | mesa em canais semanticos |
| `vetor` | 15 | os mesmos numeros de antes, com precisao total |

Canais da grade: 0 bola (gaussiana 3x3), 1 velocidade x, 2 velocidade y,
3 bumpers, 4 alvos, 5 rollovers, 6 luzes acesas, 7 flippers.

Os canais 3 a 5 sao estaticos e pre-computados; bola, luzes e flippers mudam a
cada passo. Custo medido: 31 us por observacao.

Use `cnn.VisaoMesaExtractor` com `MultiInputPolicy` - a NatureCNN padrao do SB3
usa convolucao 8x8 com passo 4, feita para telas 84x84, e destroi uma grade
36x28 na primeira camada.

**O canal dos flippers nunca vale zero**: 0,3 em repouso e 1,0 erguido. Com o
valor puro do angulo, o canal zerava com os flippers soltos e o agente perdia a
referencia de onde eles ficam.

## Paralelismo

Uma instancia de jogo por processo, entao **SubprocVecEnv e' obrigatorio**;
DummyVecEnv com varios envs no mesmo processo nao funciona. `vecenv.fabrica()`
cria os ambientes ja configurados. Throughput medido (so' coleta, sem rede):

| Ambientes | Passos/s |
|---|---|
| 1 | 1.626 |
| 2 | 2.869 |
| 4 | 4.513 |
| 6 | 6.080 |

## Scripts

- `teste_env.py` — 13 verificacoes de interface
- `treinar2.py` — treino PPO com raiz + normalizacao (sem visao)
- `treinar_visao_par.py` — treino com visao, ambientes paralelos e CNN na GPU
- `benchmark_quadros.py` — varredura de resolucao temporal
- `diag_ppo2.py` — distribuicao de acoes e origem da recompensa
- `coletar_eda.py` — trajetoria completa para analise
