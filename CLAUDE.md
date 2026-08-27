# Space Cadet como ambiente de RL

Experimento de engenharia reversa + RL sobre o *3D Pinball for Windows - Space
Cadet*. O jogo foi instrumentado para gerar dados e treinar agentes.

**Antes de editar qualquer coisa, leia `docs-ai/HANDOFF.md` e
`docs-ai/PROXIMOS_PASSOS.md`.** Eles trazem o estado atual, a ordem acordada dos
proximos passos e as regras de pontuacao do jogo.

## Estrutura

```
SpaceCadetPinball/   fork instrumentado (repo proprio, branch rl-instrumentation)
python/              ambiente Gymnasium, visao, CNN, treinos
analise/             scripts R e Python de validacao
docs-ai/             contexto: BRIEF, DECISIONS, CURRENT_STATE, HANDOFF, PROXIMOS_PASSOS
```

Sao **dois repositorios git**: o fork mantem a linhagem com o upstream do
k4zmu2a; a raiz versiona o resto. `analise/dados/` e artefatos de treino ficam
fora do git.

## Regras que evitam retrabalho

### Nunca confie em duracao alta como sinal de bom desempenho

Existe um estado absorvente - o **berco**: com os dois flippers erguidos a bola
fica imovel e a partida nunca termina. Duracao alta com score baixo e' a
assinatura dele. Ao avaliar qualquer agente, olhe **velocidade mediana da bola**
e **% do tempo no topo da mesa**, nao so' score e duracao.

Referencias medidas: berco = velocidade 0,17 e 1,5% no topo; aleatorio = 9,49 e
20,7%; agente bom = 10,48 e 22,9%.

### Sempre rode as politicas de controle

`-rl-policy 0` (nunca aperta) e `-rl-policy 2` (sempre apertado) sao o teste que
prova que o input chega ao jogo. Se as tres distribuicoes ficarem parecidas, algo
quebrou. Confira tambem o `n` de cada grupo antes de comparar - ja aconteceu de
um teste sobrescrever CSV e a comparacao rodar com n=20 contra n=300.

### Baselines nao sao comparaveis entre resolucoes

Mudar `quadros_por_passo` muda tambem o score do aleatorio (342k a 50 ms, 404k a
25 ms). Remedir o baseline junto, sempre. Use **25 ms** (`quadros_por_passo=3`).

### SubprocVecEnv e' obrigatorio

O estado do jogo e' global no codigo original: **uma instancia por processo**.
DummyVecEnv com varios envs no mesmo processo nao funciona. Para acelerar,
aumente o numero de ambientes, nao a GPU - ela fica em ~20% de uso.

### Cuidado com bonus de recompensa

Um bonus de sobrevivencia de **0,02 por passo** foi suficiente para o agente
abandonar o jogo e travar o flipper: 93% da recompensa vinha do bonus. Qualquer
incentivo secundario precisa ser medido, nao presumido inofensivo.

## Armadilhas do codigo do jogo

- `TBall::ActiveFlag` **nao** significa "bola em jogo": e' passado por ponteiro
  ao `TEdgeSegment` e oscila a cada passo de colisao.
- `get_coordinates()` devolve `VisualPosNorm`, que fica em (-1,-1) para tudo sem
  sprite. A posicao boa vem de `RenderSprite->BmpRect`, em pixels.
- A projecao e' perspectiva 3D, nao linear. Para mapear posicao em pixels, use
  `proj::xform_to_2d` (colunas `tela_x`/`tela_y`), nunca regra de tres.
- O reset tem tres tempos encadeados: a bola nao existe no `replay_level`, leva
  ~1 s ate' o canal do plunger e mais ~1 s deslizando ate' o plunger conseguir
  lanca-la.

## Comandos

Compilar (o cmake fica em `C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin`):

```powershell
cd SpaceCadetPinball
cmake -S . -B build -G "Visual Studio 17 2022" -A x64 -DBUILD_PYTHON_MODULE=ON -Dpybind11_DIR=<dir>
cmake --build build --config Release
```

Coletar dados pelo executavel:

```bash
cd SpaceCadetPinball/bin/Release
SDL_VIDEODRIVER=dummy ./SpaceCadetPinball.exe -rl-episodes 200 -rl-seed 42 -rl-policy 1 -rl-trace 6
```

Treinar:

```bash
cd python && python treinar_visao_par.py 2500000 tag 6 score
```

## Idioma

Codigo, comentarios e documentacao em portugues, como no resto dos projetos do
Adriano. Nomes de API do jogo permanecem em ingles.
