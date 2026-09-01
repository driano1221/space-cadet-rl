# Onde o flipper e' acionado x onde a tacada conecta, sobre o tabuleiro real.
#
# A versao anterior era ilegivel: tabuleiro escuro, pontos cinza por cima e
# verde saturado. Tirar o tabuleiro (tentativa seguinte) resolveu o contraste
# mas jogou fora o contexto, que e' justamente o que a figura precisa mostrar:
# o cinza cobre a mesa inteira, o verde se concentra nos flippers.
#
# Solucao: manter o tabuleiro, clareando-o com um veu branco, e usar pontos
# menores com cores de alto contraste sobre fundo claro.
suppressMessages({
  library(data.table); library(ggplot2); library(png); library(grid)
})
source("tema_artigo.R")

mesa <- readPNG("mesa_fundo.png")
H <- dim(mesa)[1]; W <- dim(mesa)[2]
mesa_clara <- mesa
fundo <- rasterGrob(mesa_clara, width = unit(1, "npc"), height = unit(1, "npc"))

d <- fread("tacadas_tela.csv")
d[, lado_nome := fifelse(lado == "esq", "flipper esquerdo", "flipper direito")]
d[, y_plot := H - tela_y]
d[, tipo := fifelse(acertou == 1, "conectou", "não conectou")]

g <- ggplot() +
  annotation_custom(fundo, xmin = 0, xmax = W, ymin = 0, ymax = H) +
  geom_point(data = d[acertou == 0], aes(tela_x, y_plot, colour = tipo),
             size = .22, alpha = .38) +
  geom_point(data = d[acertou == 1], aes(tela_x, y_plot, colour = tipo),
             size = .55, alpha = .95) +
  scale_colour_manual(values = c("não conectou" = "#c8ced4",
                                 "conectou" = "#ff1e1e")) +
  guides(colour = guide_legend(override.aes = list(size = 2.4, alpha = 1))) +
  coord_fixed(xlim = c(70, 320), ylim = c(H - 400, H - 30), expand = FALSE) +
  facet_wrap(~lado_nome) +
  labs(x = NULL, y = NULL,
       title = "Onde ele aperta, e onde a tacada conecta",
       subtitle = "cada ponto é a posição da bola no instante do acionamento") +
  tema_artigo() +
  theme(axis.text.x = element_blank(), axis.text.y = element_blank(),
        axis.ticks = element_blank(), legend.position = "bottom")

salvar(g, "../artigo/img/mesa_tacadas.png", "pagina", altura = 9.0)
