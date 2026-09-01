# O dia em que assistir ao agente valeu mais que os gráficos

Depois de semanas olhando tabelas, resolvi gravar o agente jogando. Dez GIFs com
a tela real do jogo, não uma visualização, flippers animados, placar, mensagens
de missão, tudo.

E aí veio o comentário que reorientou o projeto inteiro:

> fica muito feio os flippers disparando sozinhos, não parece algo real jogando

Ele estava certo, e eu nunca tinha olhado para isso.

```
flipper ligado em 71,3% dos passos
~11 acionamentos por segundo em cada lado
```

Fui além e montei um mapa: para cada célula da posição relativa entre bola e
flipper, qual a chance dele apertar? Se ele mirasse, o mapa mostraria
concentração perto da bola.

Existe **uma única célula de mira**, com 89%. Nas outras 24, tudo entre 24% e
59%, colado na taxa global.

**Ele aprendeu uma situação e spamma no resto.** Aquela é a única célula com
sinal claro de mira; no restante, a política se parece muito mais com spam.
Não cheguei a fazer a ablação que provaria quanto do ganho vem só dali.

Porque apertar flipper **é grátis**. O jogo não cobra nada: não tira ponto, não
gasta recurso, não penaliza. Como apertar não custa nada e às vezes ajuda, o
ambiente favorece políticas que apertam com muita frequência.

Não é preguiça do agente. É o ambiente que não cobrava.

Coloquei um custo de 0,005 por acionamento, cobrado só na borda de solto para
apertado. Deixei o *hold* de graça de propósito, raciocinando que segurar a pá é
técnica legítima de pinball e eu não queria proibir isso.

O resultado:

| | antes | depois |
|---|---|---|
| Acionamentos/s | 7,47 | 6,26 |
| **Duração de cada um** | **37 ms** | **53 ms** |
| Tempo com pá erguida | 73,2% | **79,5%** |
| Score | 2.637.750 | 1.165.625 |

Ele reduziu os acionamentos **segurando o flipper 45% mais tempo**.

Eu escrevi a regra achando que estava protegendo uma habilidade, e na prática
abri a rota de fuga mais barata. Ele achou em 2,5 milhões de passos. O vídeo
ficou pior que antes: em vez de espernear, agora passa 80% do tempo com as pás
levantadas.

Isso é *reward hacking* na brecha que **eu** deixei, e é o exemplo mais didático
que o projeto produziu.

Foi então que veio a sugestão que virou o melhor experimento da rodada:

> e se colocássemos uma regra de só usar o flipper caso a bola passar de tal
> área?

Isso tem nome em RL: *action masking*. Em vez de **desincentivar** por
recompensa, que ele contorna, você **remove** a ação do espaço. Não tem brecha,
porque a ação não existe.

Para desenhar a área eu precisava saber onde o flipper de fato alcança a bola. E
aí entrou aquele contador `ev_flip_acerto` que eu tinha instrumentado: dá para
pegar todas as tacadas que **realmente conectaram** e olhar onde a bola estava
quando o movimento começou.

Antes disso eu tinha tentado descobrir isso por fora, detectando "salto de
velocidade da bola" depois do aperto. Parecia funcionar. Fui conferir contra
instantes aleatórios e o sinal era **1,15 vezes o acaso**. Ruído puro, qualquer
bumper acelera a bola, e com 71% de acionamento tudo coincide com um aperto
recente.

Perguntar ao jogo resolveu o que adivinhar de fora não resolvia.

```{=latex}
\begin{figure}[tb]\centering
\includegraphics[width=8.5cm]{img/mesa_mascara.png}
\caption{A zona de tacada desenhada a partir dos acertos reais, sobre o tabuleiro.}
\end{figure}
```

```{=latex}
\begin{figure*}[tb]\centering
\includegraphics[width=13cm]{img/mesa_tacadas.png}
\caption{Onde ele aperta (cinza) contra onde realmente conecta (vermelho), sobre o tabuleiro real.}
\end{figure*}
```

O efeito foi imediato.

```
pontaria (tacadas por acionamento)
  agente livre                0,023
  com máscara, política fixa  0,54 a 0,61
  com máscara, lado sorteado  0,808
```

**Vinte a trinta e cinco vezes mais pontaria**, vinda de restrição geométrica
pura, sem treino nenhum. Punir e premiar não tinham movido esse número em três
tentativas. Restringir moveu de imediato.

E o score despencou.

Antes de eu entender o porquê, veio outro comentário olhando os GIFs:

> vejo a bola indo para um flip e o outro sendo ativado

Fui verificar. As duas zonas, construídas a partir das tacadas de cada flipper,
**se sobrepõem em 67%**, a bola desce pelo mesmo funil para os dois lados. E o
meu código escolhia assim:

```python
for lado in ("esq", "dir"):
    if celula in self.zona[lado]:
        return lado          # sempre para no "esq" primeiro
```

**Ele acionava a pá esquerda por ordem alfabética.** Na maior parte das
entradas, a bola ia para a direita e a esquerda subia.

Pior: quando fui procurar um critério para corrigir automaticamente, descobri
que **não existe**. O melhor limiar de posição separa os lados com 56,3% de
acerto, contra 50% de chute. Qual pá vai alcançar a bola depende da trajetória
futura, não de onde ela está ao entrar na zona.

Era uma decisão que **eu** tinha tomado no lugar do agente, e tomado errado.
Devolvi para ele: o espaço de ação passou de 7 para 13 opções. Só a correção
quase dobrou a pontaria, de 0,30 para 0,54–0,61.

Dois treinos foram para o lixo por causa desse bug, e ele foi encontrado
assistindo ao vídeo, não olhando tabela.
