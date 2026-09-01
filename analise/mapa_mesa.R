# Onde a bola passa o tempo, por politica.
#
# Cuidado com os eixos: medido em 31/08, cor(y_fisica, tela_y) = +0,992 e
# cor(x_fisica, tela_x) = -0,994. Ou seja, o y da fisica cresce PARA BAIXO
# (como coordenada de tela) e o x cresce PARA A ESQUERDA. Plotar direto
# devolve a mesa espelhada nos dois eixos, que foi como esta figura saiu na
# primeira versao do artigo.
suppressMessages({library(data.table); library(ggplot2); library(scales)})
source("tema_artigo.R")

ler <- function(arq, rotulo) {
  d <- fread(file.path("dados", arq), select = c("x", "y"))
  d[, politica := rotulo][]
}

d <- rbindlist(list(
  ler("eda_aleatoria.csv",  "Aleatória"),
  ler("eda_heuristica.csv", "Heurística defensiva (berço)")
), fill = TRUE)

g <- ggplot(d, aes(x, y)) +
  stat_bin2d(bins = 90) +
  scale_fill_gradientn(
    colours = c("#f2f5f8", "#b9c6d4", "#5b7fa6", DESTAQUE, "#16243a"),
    trans = "log10", labels = label_number(scale_cut = cut_short_scale()),
    name = "passos") +
  scale_x_reverse() +   # x da fisica cresce para a esquerda
  scale_y_reverse() +   # y da fisica cresce para baixo
  coord_fixed() +
  facet_wrap(~politica) +
  labs(x = NULL, y = NULL,
       title = "Onde a bola passa o tempo",
       subtitle = "densidade de posições, escala logarítmica") +
  tema_artigo() +
  theme(axis.text.x = element_blank(), axis.text.y = element_blank(),
        axis.ticks = element_blank(),
        legend.position = "right", legend.title = element_text(size = 7),
        legend.key.width = unit(7, "pt"), legend.key.height = unit(22, "pt"))

salvar(g, "../artigo/img/mapa_mesa.png", "pagina", altura = 8.4)
