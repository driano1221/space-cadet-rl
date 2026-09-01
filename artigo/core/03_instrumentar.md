# O que significa instrumentar um jogo

Vale explicar isso direito, porque é a decisão técnica que define o projeto
inteiro.

Existem duas formas de fazer uma IA jogar um jogo.

**A forma de fora.** Você tira uma foto da tela, manda para uma rede neural
descobrir o que está acontecendo, e simula apertos de tecla. É o que o
space-cadet-nn faz. Funciona em qualquer jogo, inclusive nos que você não tem o
código. O preço é alto: você fica preso à velocidade real, gasta processamento
enorme convertendo pixels em significado, e o agente precisa aprender a
enxergar antes de aprender a jogar.

**A forma de dentro.** Você pega o código do jogo, acha a linha onde ele calcula
a posição da bola, e simplesmente **pergunta**. É o que o ViZDoom fez com o Doom
em 2016 [@vizdoom], e o que virou padrão desde então.

A segunda é incomparavelmente melhor quando você tem o código. E eu tinha.

Isso foi o que mais deu trabalho, porque não é óbvio. Depois de ler bastante
código, os pontos que importam são três:

A física roda a **120 Hz**, e eu agrupo três quadros por decisão: o agente
age a **40 Hz**, uma ação a cada 25 ms.

`pb::frame(float dt)` executa um passo de física. Chamar isso num laço, sem
desenhar nada na tela, é o que dá as 941 vezes a velocidade real.

Esta chamada aplica o aperto do flipper, e é por aqui que o agente age:

```
MainTable->Message(
    MessageCode::LeftFlipperInputPressed,
    pb::time_now)
```

`TPinballTable::CurScore` e a lista `BallList` dão o placar e a bola. Estavam
públicos, sem nenhum encapsulamento no caminho.

O código já separava física de renderização e já tinha modo de passo único, o
que sugere que quem fez a decompilação também precisou depurar quadro a quadro.

Compilou de primeira. Escrevi um `rlenv.cpp` que roda o jogo numa thread
separada, com um handshake simples: o Python pede um passo, o C++ executa e
devolve o estado. Um binding em pybind11 expõe isso para o Python como um módulo
normal.

Não é screenshot. É isto, direto da física, a cada 25 milissegundos:

```
bola_x, bola_y, bola_vx, bola_vy, bola_speed
score, bolas_restantes, bolas_em_jogo
rank, progresso, multiplicador
flip_esq_ang, flip_dir_ang
bola_rel_esq_x/y, bola_rel_dir_x/y
tilt, nudge_count
ev_bumper, ev_hyperspace, ev_medal,
ev_flip_acerto, ev_extra_ganha
```

Os campos que começam com `ev_` são contadores que eu **adicionei ao C++**,
incrementados dentro dos controladores do jogo. Quando a bola bate num bumper, o
contador sobe. Quando o flipper em movimento toca a bola, outro contador sobe.

Esse último, o `ev_flip_acerto`, custou uma tarde e vai ser importante mais para
frente, então guarde o nome.

Uma armadilha que descobri no caminho: `TBall::ActiveFlag` **não** significa
"bola em jogo". Ele oscila a cada passo de colisão. Filtrar por ele descartava
dois terços das minhas amostras, e eu levei um tempo até perceber que os dados
estavam sumindo.

Outra: a projeção da mesa na tela é perspectiva 3D, não linear. Se você tentar
converter coordenada do mundo para pixel com regra de três, erra. Existe uma
função `proj::xform_to_2d` no código que faz isso certo.

Comparando com fotografar a tela:

| | Foto da tela | Instrumentado |
|---|---|---|
| Velocidade | 1x | **941x** |
| Posição da bola | inferida da imagem | exata |
| Eventos do jogo | invisíveis | contados na física |
| Custo por passo | conversão de pixels | leitura de struct |

Vale separar dois números que são fáceis de confundir. O **941x** é a física
sozinha, rodando sem a rede neural no laço: é o teto do ambiente. No treino de
verdade a rede entra, e a conta muda.

Um treino de 2,5 milhões de decisões, a 25 ms cada, representa **17,4 horas de
jogo**. Ele roda em **uma hora**, o que dá aceleração efetiva de **17x**.

Ainda é a diferença entre rodar dez experimentos e rodar um. Sem o ambiente
instrumentado, esses mesmos treinos levariam quase um dia cada.

