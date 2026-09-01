# Scripts

Todos rodam de dentro desta pasta (`python <script>.py`), porque resolvem
imports e caminhos a partir do proprio arquivo.

## Nucleo — o ambiente

| Arquivo | O que e |
|---|---|
| `spacecadet_gym.py` | o `gym.Env` principal. Concentra todas as variantes: `visao`, `prever`, `mascara_zona`, `custo_flip`, `peso_*`, `bolas`, `atraso_ms` |
| `visao.py` | grade 9x36x28 da mesa (bola, velocidade, bumpers, alvos, luzes, flippers) |
| `cnn.py` | extrator convolucional da grade |
| `vecenv.py` | fabrica para `SubprocVecEnv` (o estado do jogo e global: uma instancia por processo) |
| `env_opcoes.py` / `env_opcoes2.py` | semi-MDP onde o agente escolhe quanto esperar. **Linha encerrada** - pede predicao de um agente que so sabe reagir |

## Treino

| Arquivo | Uso |
|---|---|
| `treinar_visao_par.py` | o treinador principal. 14 argumentos posicionais - ver cabecalho do arquivo |
| `treinar_opcoes.py`, `treinar_duplo.py` | treinadores do env de opcoes |
| `fila_ideias.sh` | roda as cinco ideias em sequencia |
| `apos_fila.sh` | dispara a coleta lado a lado quando a fila termina |

`PINBALL_DEVICE=cpu` forca CPU. Checkpoints saem em `ckpt/` a cada 250k passos.

## Self-checks — rodar antes de treinar

Todos usam `assert`: falham alto em vez de imprimir sucesso falso.

| Arquivo | Verifica |
|---|---|
| `teste_lados.py`, `teste_duplo.py` | cada acao aciona o flipper que promete, e so ele |
| `teste_contagem.py` | a recompensa cobre o intervalo inteiro, sem buraco nem dupla contagem |
| `teste_custo.py` | o custo cobra na borda e nao no hold |
| `teste_acerto.py`, `valida_acerto.py` | `ev_flip_acerto` conta tacada de verdade (zero com pa parada) |
| `teste_prever.py` | os campos de previsao correspondem a trajetoria real |
| `teste_ideias.py` | bonus de novidade decresce, shaping e telescopico, bolas mudam mesmo |

## Medicoes — o metodo do projeto

Medir a frequencia do evento **antes** de gastar uma hora de GPU. Ja evitou
quatro treinos inuteis.

| Arquivo | O que mede |
|---|---|
| `spam.py`, `mira.py` | taxa de acionamento e onde ele mira |
| `varre_esperas.py` | qual espera rende mais (o plato vai ate 200 ms) |
| `testa_lado_importa.py`, `testa_ambos.py` | o lado do flipper carrega sinal? acionar os dois ajuda? |
| `zona_mascara.py` | constroi a zona e mede se a bola fica tempo suficiente nela |
| `por_que_parede.py` | decompoe score em duracao x pontos/s |
| `heuristica_prev.py` | quanto uma heuristica crua faz com as mesmas features |
| `testa_predicao.py` | erro da extrapolacao por horizonte |
| `checa_aprendizado.py` | inicializacao, horizonte do gamma, forma do sinal |
| `testa_replay.py` | o replay reproduz o estado? (nao reproduz - matou o Go-Explore) |

## Avaliacao

| Arquivo | Uso |
|---|---|
| `coletar_eda.py` | **o que vale**: N episodios completos por agente, em serie, gerando os CSVs. Detecta a dimensao da observacao pelo proprio modelo |
| `sem_teto.py` | partidas sem limite de tempo |
| `comparar_flip.py`, `duelo.py` | comparacoes lado a lado com Mann-Whitney |
| `clipes.py`, `clipes_opcoes.py` | GIFs com a tela real do jogo |
| `goexplore.py` | arquivo de celulas e mapa da fronteira alcancada |
| `jogar.py` | gravador de partidas humanas (pronto, nunca usado) |

> A avaliacao **interna do treinador** (n=6) nao serve para comparar
> agentes - ja induziu leitura errada tres vezes. Use `coletar_eda.py`.

> **Nota sobre "pareado".** Versoes antigas destes textos chamavam as
> comparacoes de pareadas. Nao sao: os episodios nao compartilham semente e
> o teste usado e' Mann-Whitney entre amostras. O que se controla e' a
> variancia entre execucoes, rodando os agentes em serie no mesmo processo.
