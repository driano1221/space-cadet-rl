# Analise

Scripts R (tidyverse + patchwork), dados e graficos. Rodar de dentro desta
pasta: `Rscript eda_flip.R`.

## Dados

| Arquivo | Conteudo |
|---|---|
| `eda_episodios.csv` | uma linha por episodio completo (70 na ultima coleta: 7 agentes x 10) |
| `eda_acionamentos.csv` | uma linha por acionamento (413.978), com posicao da bola e se conectou |
| `tacadas_tela.csv` | acionamentos em coordenadas de tela, para os mapas sobre o tabuleiro |
| `zona_flipper.json` | zona de tacada em celulas de 10 px, por flipper |

Campos e unidades em [../docs-ai/DICIONARIO.md](../docs-ai/DICIONARIO.md).

## Scripts

| Arquivo | Gera |
|---|---|
| `eda_flip.R` | painel dos agentes: score, tacadas, volume x pontaria, tempo de pa erguida |
| `_cmp.R` | tabela de comparacao contra o controle, com Mann-Whitney |
| `mascara_mesa.R` | tacadas plotadas sobre o tabuleiro real do jogo |
| `zona_reativa_img.R` | zona antiga x nova, sobre a mesa |
| `reacao.R` | a curva de reacao (o achado principal do projeto) |
| `linha_do_tempo.R`, `agentes.R`, `rank.R`, `eda_escala.R` | graficos dos passos anteriores |

## Graficos principais

| Arquivo | Mostra |
|---|---|
| `reacao.png` | score por atraso de acao — **o resultado principal** |
| `eda_flip_painel.png` | os sete agentes lado a lado |
| `eda_duracao_score.png` | duracao x score: a ordem por um e a ordem pelo outro |
| `eda_efeitos.png` | tamanho de efeito e p-valor por tratamento |
| `mesa_tacadas.png`, `mesa_mascara.png` | onde ele aperta x onde conecta |
| `zona_antiga_vs_nova.png` | as duas versoes da zona sobre o tabuleiro |

## midia/

Cinco GIFs representativos, com a tela real do jogo. As pastas `clipes*/` ficam
fora do git (24 MB, reproduziveis com `python/clipes.py`).

## Cuidado ao ler

`mesa_fundo.png` e a mesa capturada do emulador, usada como fundo dos mapas. O
eixo Y da tela cresce para baixo; os scripts invertem (`H - tela_y`) ao plotar.
