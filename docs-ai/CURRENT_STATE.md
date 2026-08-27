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

## Ciclo de RL - resultados (2026-08-26/27)

Quatro treinos PPO. Nenhum bateu o baseline aleatorio, mas a distancia caiu
pela metade e cada rodada rendeu um achado.

| Agente | Mediana | dp | CV | Max | Duracao |
|---|---|---|---|---|---|
| **Aleatorio a 25 ms** | **404.375** | 353.219 | 0,67 | 1.425.000 | 173 s |
| PPO 25 ms + flippers | 212.500 | 90.899 | 0,38 | 461.750 | 104 s |
| PPO sem bonus, 50 ms | 154.500 | - | - | 400.750 | 120 s |
| PPO score cru, 50 ms | 144.750 | - | - | 351.500 | 98 s |
| PPO + bonus de sobrevivencia | 72.000 | - | - | 525.000 | 264 s |

### Tres achados

**1. O berco.** Com dois flippers erguidos a bola fica apoiada, imovel, e a
partida nunca termina. A EDA mostrou: velocidade mediana 0,17 contra 9,49 do
aleatorio, 82,7% do tempo quase parada, 97,6% do tempo na base, 1,5% no topo
(onde ficam os alvos). Rende 11.568 pontos/min contra 161.280 do aleatorio.
Tres caminhos independentes caem nele: bonus de recompensa, politica de flipper
travado e heuristica defensiva escrita a mao.

**2. Resolucao temporal.** O flipper leva ~50 ms para erguer. Decidir a cada
50 ms e' decidir na escala do proprio movimento da pa'. Score mediano do
aleatorio por intervalo: 100 ms = 247.375; 50 ms = 355.375; **25 ms = 467.750**;
8 ms = 452.125. Existe um patamar em torno de 25 ms.

**3. Captura do objetivo.** Um bonus de sobrevivencia de 0,02 por passo levou o
PPO a travar o flipper direito em 96,8% dos passos, com **93% da recompensa
vindo do bonus** e 7% do score. Controle limpo: o treino seguinte, identico
exceto pelo bonus zerado, usou 27% de "direito" e 100% da recompensa vinda do
score.

### Por que o agente nao aprende a jogar bem

Em ordem de peso:

1. **Ele nao enxerga a mesa.** A observacao tem 15 numeros sobre bola e
   flippers e nada sobre alvos, rampas ou bumpers. Nao ha' como aprender a
   mandar a bola num alvo que nao existe na percepcao. O teto de 461.750 contra
   1.425.000 do aleatorio e' compativel com isso: ele nunca acessa as jogadas
   grandes.
2. **O aleatorio e' baseline forte.** Faz 404.375 - a fisica trabalha sozinha.
   Nao e' Atari, onde random faz zero.
3. **Credito diluido.** Os pontos chegam segundos apos a tacada; com 40
   decisoes/s e gamma 0,995, 3 s descontam para 55%. E 97% dos passos valem
   zero, com picos de 25x o desvio.
4. **Escala.** 600k passos sao ~1,8M frames; Atari usa 50M.

### Proximos passos sugeridos

- [ ] **Visao da mesa**: observacao em grade 2D (bola + luzes em canais) e CNN,
      como o projeto do Antiyoy fez. Ataca a causa raiz.
- [ ] **Bloquear o berco**: penalizar bola parada perto dos flippers ou encerrar
      o episodio por velocidade baixa prolongada. Barato.
- [ ] **Escala**: 5M+ passos.
- [ ] **Acoes que faltam**: nudge (`nudge_left/right/up`) e plunger modulado -
      hoje `launch_ball()` usa sempre `Boost = MaxPullback`, forca maxima.
