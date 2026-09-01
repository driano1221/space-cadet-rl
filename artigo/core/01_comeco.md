# Tudo começou com um viking

Eu queria mudar a cara de um personagem.

É sério, foi só isso. Instalei o 3D Pinball Space Cadet, aquele do Windows XP,
por pura saudade. Abri, joguei duas partidas, perdi as duas, e reparei que o
piloto da nave no canto da tela era um bonequinho genérico de capacete.

E aí veio a associação boba que dá origem a projetos inteiros. Eu tinha visto
*Freaks and Geeks* [@freaksgeeks], aquele episódio em que o Sam tenta
impressionar a Cindy, e a série tem um viking que ficou na minha cabeça. Olhei o
piloto do pinball e pensei que ele ficaria melhor de elmo e barba.

Não existe motivo racional para isso. Eu estava com tempo livre e queria ver um
viking pilotando uma nave espacial num jogo de 1995.

```{=latex}
\begin{figure}[tb]\centering
\includegraphics[width=4.6cm]{img/freaks_geeks.jpg}
\caption{A referência que começou tudo: o viking de \emph{Freaks and Geeks}.}
\end{figure}
```

O arquivo do jogo é um `PINBALL.DAT` de formato proprietário, sem documentação
oficial, cheio de bitmaps colados uns nos outros. Escrevi um parser e descobri
que os 318 bitmaps compartilham uma paleta global de 256 cores: mexer numa
entrada estraga a mesa inteira. Sobravam 19 índices livres, e trabalhei dentro
deles.

Depois de umas cinco tentativas de desenhar o viking por código, o resultado
estava tão ruim que eu ri sozinho. Barba grande demais, elmo flutuando acima da
cabeça, resquícios do capacete antigo aparecendo por trás. Parecia um acidente
industrial. Desisti da abordagem, gerei a imagem que eu queria num modelo de
imagem, e escrevi um conversor: alinhamento por busca de escala e deslocamento,
requantização com distância perceptual, preenchimento por vizinhança para não
deixar buraco no fundo com dither.

```{=latex}
\begin{figure*}[tb]\centering
\includegraphics[width=13cm]{img/viking_no_jogo.png}
\caption{O jogo rodando com o arquivo original e com o modificado. São 70 por
57 pixels de sprite, trocados dentro da paleta global de 256 cores.}
\end{figure*}
```

Funcionou. O viking ficou lá, pilotando a nave. E foi aí que a coisa saiu do
controle.

Foi um vídeo que ligou uma coisa na outra.

Por essa época eu estava vendo um vídeo do Simon, *Mastering the Hex: A Case
Study in Reinforcement Learning for Strategy Games* [@antiyoy_rl], sobre treinar
uma inteligência artificial para jogar Antiyoy, um jogo de estratégia
hexagonal. O vídeo é ótimo e tem um detalhe que ficou na minha cabeça: para
treinar o agente, ele precisou **recriar o jogo inteiro em Pygame**, porque o
original era Java e não dava para instrumentar.

Ele reconstruiu mecânica por mecânica, com o risco extra de a recriação não
bater com o jogo real.

Eu tinha acabado de passar um bom tempo dentro do formato binário do Space
Cadet. E pensei: *"espera aí. O Space Cadet tem decompilação em C++. O
código-fonte reconstruído está no GitHub. Eu não preciso recriar nada."*

Foi essa a ideia. Pegar um jogo que praticamente todo brasileiro da minha idade
abriu pelo menos uma vez enquanto esperava alguma coisa carregar, e transformar
ele num laboratório de aprendizado por reforço de verdade. Decidi embarcar
nisso, e fui registrando o caminho enquanto acontecia, que é o que você está
lendo.

Aviso desde já: **o agente não bateu o recorde do jogo.** Ele chegou a 2,6
milhões de pontos, e o recorde humano é 126 milhões. Está 48 vezes longe.

Mas a pergunta que este projeto acabou respondendo é bem mais interessante do
que "dá para bater o recorde?", e eu só cheguei nela porque quase tudo que
tentei deu errado primeiro.
