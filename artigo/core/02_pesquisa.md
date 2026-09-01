# Antes de escrever código, uma boa pesquisa

Com o viking no lugar, a pergunta mudou: dá para fazer mais do que trocar um
sprite nesse jogo?

Minha primeira reação foi abrir o editor e começar. Segurei. Se a ideia fosse
boa, provavelmente alguém já tinha feito, e eu ia querer saber o que essa pessoa
aprendeu antes de repetir os erros dela.

Vale a pena listar o que encontrei, porque quase
tudo aqui é útil para quem quiser mexer com o mesmo jogo.

**[k4zmu2a/SpaceCadetPinball](https://github.com/k4zmu2a/SpaceCadetPinball)** é a
peça central de tudo. É a decompilação em C++ do binário original do Windows XP,
feita por engenharia reversa, e ela **compila e roda** [@spacecadet_decomp]. Todo este projeto existe
por causa desse repositório. Sem ele eu estaria no mesmo barco do Simon,
recriando pinball em Pygame.

**[AdrienTD/PinballTools](https://github.com/AdrienTD/PinballTools)** traz
ferramentas de modding e, mais importante, documentação do formato dos arquivos.
Foi o que me ajudou no viking [@pinballtools].

**[3D Pinball Mod Tool](https://cryoganix.itch.io/3d-pinball-mod-tool)** é uma
interface gráfica de modding no itch.io, para quem não quer escrever parser
[@modtool].

Agora a parte que me interessava de verdade: alguém já tinha treinado IA nesse
jogo?

**[ElliotWood/3DPinballAI](https://github.com/ElliotWood/3DPinballAI)** usa Unity
ML-Agents. Dez estrelas, arquivado em abril de 2020. Mas tem um detalhe: é uma
**recriação do jogo em Unity**, não o jogo original. As físicas são do Unity, não
do Space Cadet [@pinball_unity].

**[angelowilliams/space-cadet-nn](https://github.com/angelowilliams/space-cadet-nn)**
usa algoritmo genético com captura de tela (OpenCV e MSS, a 30 quadros por
segundo). Nove estrelas [@spacecadet_nn]. O README dele tem uma frase que me pegou:

> não roda em emulador nem é open source

Era verdade quando ele escreveu, em 2019. Deixou de ser verdade com a
decompilação. E ninguém voltou para refazer o trabalho.

**[Modeling my pinball scores](https://www.sumsar.net/blog/modeling-my-pinball-scores/)**,
do Rasmus Bååth, é modelagem bayesiana de pontuação de pinball em R. Não é RL,
mas é o precedente do lado estatístico, e me deu ideias de como tratar a
distribuição de score, que tem uma cauda pesada horrorosa [@baath_pinball].

Achei também os ports do jogo para Emscripten, Vita, Switch, Wii U, libretro e
PowerPC. Não usei nenhum, mas mostram o tamanho da comunidade que ainda mexe
nisso [@ports].

Já com o projeto adiantado, encontrei **Pinbot: Applying Reinforcement Learning
to Pinball Machines**, de Chaudhary, Mohta, Xiao, Cuenca e Holand, do curso
16-831 da CMU, outono de 2024 [@pinbot]. PPO sobre Visual Pinball X, mirando transferir o
aprendizado para uma máquina física de verdade.

Duas frases do paper deles descrevem, com outras palavras, coisas que eu já
tinha visto acontecer no meu:

> o agente eventualmente aprendeu a simplesmente ficar parado sem lançar a bola,
> com medo da penalidade futura quando a bola drenasse

Isso é o meu primeiro treino, que colapsou em "nunca apertar nada".

> uma recompensa simples baseada em tempo alcançaria um mínimo local onde o
> agente simplesmente prende a bola no flipper

Isso é o que eu vim a chamar de **berço**, e vou falar bastante dele mais para
frente.

Descobrir isso foi ótimo por dois motivos. Primeiro, tira meus achados da
categoria "peculiaridade do Space Cadet" e coloca como propriedade do pinball
enquanto problema de RL. Segundo, me deu a régua deles:

| | Score | Tempo |
|---|---|---|
| Humano | 38.952 | 69 s |
| Agente treinado | 33.952 | 57 s |
| Aleatório | 14.420 | 38 s |
| Sem agente | 8.358 | 36 s |

O agente deles faz 2,35 vezes o aleatório e 87% do humano. Esse segundo número é o que eu não consigo
calcular para o meu: volto a isso no capítulo sobre latência.

Vale dimensionar o tamanho da coisa.

Sendo honesto sobre o tamanho da coisa: **instrumentar jogo de código aberto para
RL é técnica estabelecida desde o ViZDoom, em 2016** [@vizdoom]. Eu não inventei método
nenhum.

O que eu faço aqui é preencher uma lacuna num nicho pequeno. Os dois projetos de
IA que existem para este jogo não usam o jogo real: um recria em Unity, o outro
fotografa a tela a 30 quadros por segundo. Nenhum dos dois consegue ler o estado
interno, e nenhum dos dois roda mais rápido que tempo real.

O meu roda a **941 vezes a velocidade real** e lê a posição da bola direto da
física. Procurei bastante e não achei nada parecido: ninguém tinha voltado ao
jogo depois que a decompilação tornou isso possível.

É lacuna preenchida, não fronteira movida. Prefiro apresentar assim.
