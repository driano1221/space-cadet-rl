# Estado Atual - 2026-08-26

## Funciona

- Build reproduzivel: VS2022 Enterprise + SDL2 2.32.10 + SDL2_mixer 2.8.2.
- Modo headless sem janela (`SDL_VIDEODRIVER=dummy`), ~1.000x tempo real.
- **Coleta de trajetoria** (`-rl-trace N`): 20 colunas por linha, incluindo
  posicao/velocidade da bola, luzes acesas, multiplicador, acoes aplicadas e
  a posicao projetada em pixels.
- **Varredura de agressividade** (`-rl-prob P`): probabilidade de manter o
  flipper pressionado, de 0 a 100.
- Determinismo verificado: mesma semente produz arquivo identico.
- Analise em R (tidyverse + data.table) e validacao visual em Python.

## Validacao visual - feita

Tres evidencias independentes de que os dados sao reais:

1. **A densidade de posicoes desenha a mesa.** Os obstaculos aparecem como
   regioes frias; o canal do plunger, como faixa quente.
2. **A trajetoria de uma partida e' fisicamente coerente.** A bola sobe pelo
   canal do plunger a direita, quica nos defletores e desce ao funil.
3. **Politicas degeneradas produzem distribuicoes distintas** - se o input nao
   chegasse ao jogo, seriam iguais.

## Numeros

Baseline aleatorio (n=1000): mediana 392.500, media 501.988, max 2.970.750,
assimetria 2,26, duracao media 168,6 s, correlacao duracao x score = 0,79.

Normalidade: Shapiro-Wilk p < 2,2e-16 no score bruto; p = 0,0015 em log(score).
O log melhora ~12 ordens de magnitude mas **ainda rejeita** - nao e' log-normal
exata, provavelmente por causa dos saltos discretos das missoes.

Varredura de agressividade (150 partidas por nivel):

| Prob. apertar | Score mediano | Duracao (s) | Satura o teto |
|---|---|---|---|
| 0% | 145.125 | 90 | 0% |
| 20% | 324.625 | 143 | 0% |
| **30%** | **413.625** | 162 | 0% |
| 50% | 401.875 | 168 | 0% |
| 80% | 255.875 | 157 | 0% |
| 95% | 247.375 | 314 | 7% |
| 100% | 16.000 | **597** | 99% |

## Ambiente Gymnasium - FEITO

`python/spacecadet_gym.py` expoe `SpaceCadetEnv`, validado em 13 verificacoes de
interface. O modulo C++ `spacecadet_env` (pybind11) roda o jogo em uma thread e
atende comandos por handshake, a ~21.000 chamadas/s.

Equivalencia com o executavel verificada em 150 partidas por via, mesma politica:
Kolmogorov-Smirnov p = 0,079; Mann-Whitney p = 0,224. Indistinguiveis.

Build: `-DBUILD_PYTHON_MODULE=ON -Dpybind11_DIR=<dir>` e alvo `spacecadet_env`.

## Limitacoes conhecidas

1. **O reset e' estocastico.** `seed` nao torna o estado inicial reproduzivel:
   `pb::replay_level` parte do estado em que a partida anterior terminou e a
   bola sai do canal do plunger em momentos diferentes. A fisica e'
   deterministica; o estado inicial e' que varia. Por isso o `check_env` do
   Gymnasium reprova na checagem de determinismo - a validacao de interface e'
   feita por `python/teste_env.py`.
2. **Uma instancia de jogo por processo.** O estado do jogo e' global no codigo
   original. Para paralelizar, usar `SubprocVecEnv`, nunca VecEnv em threads.
2. **`render::update()` continua rodando** dentro de `pb::frame()`. Desenha em
   buffer mesmo sem janela. Custo nao medido.
3. **Dados em 100% saturam o teto** de 72.000 passos: censurados a direita.
4. **Sem paralelismo.** Um processo por vez.
5. **Trace pesa.** 200 episodios com intervalo 6 geram ~50 MB por politica;
   `analise/dados` esta com 284 MB e nao e' versionado.
6. **A semente controla so' a politica.** O jogo se mostrou deterministico,
   mas nao foi investigado se ha' RNG interno semeavel.

## Armadilhas ja encontradas (nao repetir)

- `TBall::ActiveFlag` **nao** significa "bola em jogo". E' passado por ponteiro
  ao `TEdgeSegment` e oscila a cada passo. Filtrar por ele descartava 2/3 das
  amostras e cortava metade da mesa.
- A projecao **nao e' linear**: e' perspectiva 3D. Para sobrepor posicoes ao
  bitmap da mesa, usar `proj::xform_to_2d` (colunas `tela_x`/`tela_y`).
- Um teste de reprodutibilidade ja sobrescreveu um CSV e fez uma comparacao
  rodar com n=20 contra n=300. Conferir sempre o `n` de cada grupo.
