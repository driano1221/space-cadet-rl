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

## Scripts

- `teste_env.py` — 13 verificacoes de interface
- `treinar2.py` — treino PPO com raiz + normalizacao
- `diag_ppo2.py` — distribuicao de acoes e origem da recompensa
