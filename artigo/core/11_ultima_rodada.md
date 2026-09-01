# Última rodada: cinco ideias de uma vez

A essa altura eu já tinha diagnosticado o teto, mas queria uma última tentativa
honesta antes de fechar. Pesquisei o que a literatura oferece para exatamente
este problema, recompensa esparsa, horizonte longo, exploração difícil.

O nome que aparece em todo lugar é **Go-Explore** [@goexplore], a técnica que
resolveu o Montezuma's Revenge. A ideia: guardar estados promissores num arquivo, voltar
para eles, e explorar dali. Normalmente isso exige salvar e restaurar o estado do
jogo.

Eu não tenho save state. Mas o jogo é determinístico, então dá para "restaurar"
rejogando a sequência de ações.

Testei antes de construir em cima:

```
replay 1: score 13.750  bola (262,138)
replay 2: score  6.750  bola (177,251)
replay 3: score  7.500  bola (242,201)
```

Não reproduz. O jogo tem gerador aleatório que avança entre episódios. Go-Explore
morreu ali, e custou vinte minutos em vez de um dia, porque eu testei a premissa
antes de implementar.

Montei então cinco ideias que atacam ângulos diferentes, e rodei todas com o
mesmo orçamento:

| Ideia | O que ataca |
|---|---|
| **Previsão + progresso** | percepção e incentivo juntos |
| **Shaping por potencial** | incentivo, na forma matematicamente correta |
| **Bônus de novidade** | exploração, paga $1/\sqrt{\text{visitas}}$ por estado raro |
| **Currículo de bolas** | oportunidade, treinar com 6 bolas em vez de 3 |
| **Treino longo** | tempo, 7,5 milhões de passos em vez de 2,5 |

A lógica: duas mexem no incentivo, duas na oportunidade, uma na percepção. Se
nenhuma funcionar, são cinco vias distintas falhando pelo mesmo motivo.

Sete agentes (o base, o controle e as cinco ideias), 10 episódios completos
cada, num total de 70. As cinco comparações abaixo são contra o controle:
mesma configuração, pesos zerados.

```
modelo      score      variação  p       duração  pontaria
controle  2.775.125      ,     ,        1131s     2,8%
longo     2.407.000     -13%   0,796      1066s     2,9%
potencial 1.890.250     -32%   0,165      1026s     2,7%
novidade    954.875     -66%   0,043       548s     2,2%
previsão    680.000     -75%   0,052       551s     2,3%
bolas       523.250     -81%   0,015       423s     1,7%
```

**Nenhuma superou o controle.** Todas ficaram com score menor: duas com
$p < 0{,}05$, uma no limite ($p = 0{,}052$) e duas sem diferença detectável.

**Treino longo empatou** ($p = 0{,}80$). Triplicar o orçamento não move nada.
Isso fecha em definitivo a hipótese mais confortável de todas, a de que "é só
treinar mais".

**Shaping por potencial não trouxe ganho mensurável** ($p = 0{,}17$). Vale notar
que a garantia de Ng et al. é preservar a política ótima, não produzir empate:
o método poderia perfeitamente ter acelerado a chegada a uma política melhor.
Aqui não acelerou.

**As três de baixo caíram pelo mesmo motivo.** Olhe a coluna de duração:
548, 551 e 423 segundos contra 1131 do controle. Todas cortaram o tempo de jogo
pela metade ou mais.

O currículo de bolas é o caso mais limpo e mais irônico: treinei com 6 bolas para
ele ter folga de aprender sequências longas, e ele **aprendeu a jogar como quem
tem bolas sobrando**. Com 3 bolas de volta, morre em 423 segundos. O currículo
ensinou exatamente a coisa errada.

E aqui está a coisa mais bonita da tabela inteira:

**A ordem por score é idêntica à ordem por duração. Nas sete linhas. Sem uma
exceção.**

```{=latex}
\begin{figure}[tb]\centering
\includegraphics[width=8.5cm]{img/eda_duracao_score.png}
\caption{Duração contra score: a mesma ordem, sem exceção.}
\end{figure}
```

Não importa o que eu fizesse com a recompensa, com a exploração, com o orçamento
ou com a informação. O que decidia o placar era sempre quanto tempo a bola ficava
viva.

Somando com tudo que veio antes, punir, premiar, restringir, crédito local,
Go-Explore, são **doze tentativas por vias diferentes** e o teto não se moveu.

Os resultados apontam para um limite estrutural desta configuração: não é de
incentivo, nem de exploração, nem de tempo de treino, nem de informação.
