# Onde as tacadas acontecem, SOBRE o tabuleiro real.
#
# O grafico anterior usava coordenada relativa (bola - flipper), que nao tem
# como ser sobreposta a mesa, e deixava o eixo Y na convencao de tela (cresce
# para baixo) sem inverter - por isso a mesa aparecia de cabeca para baixo.
# Aqui: pixels de tela, imagem de fundo, e Y invertido para bater com o que se
# ve jogando.
library(tidyverse)
library(png)
library(grid)

mesa <- readPNG("mesa_fundo.png")
H <- dim(mesa)[1]; W <- dim(mesa)[2]
fundo <- rasterGrob(mesa, width = unit(1, "npc"), height = unit(1, "npc"))

# A imagem de fundo e' desenhada na orientacao do dispositivo (primeira linha
# no topo), enquanto os pontos seguem o eixo (y cresce para cima). Inverter o
# eixo desalinha os dois - a mesa sai certa e os pontos saem espelhados. A
# correcao e' converter a coordenada dos pontos, nao o eixo: tela_y conta do
# topo, entao H - tela_y poe o ponto na mesma convencao da imagem.
tac <- read_csv("tacadas_tela.csv", show_col_types = FALSE) |>
  mutate(lado = factor(lado, c("esq", "dir"), c("flipper esquerdo", "flipper direito")),
         desfecho = factor(acertou, c(0, 1), c("nao conectou", "TACADA")),
         y_plot = H - tela_y)

cat("acionamentos:", nrow(tac), "| tacadas:", sum(tac$acertou), "\n")
tac |> summarise(n = n(), tacadas = sum(acertou),
                 taxa = scales::percent(mean(acertou), .01), .by = lado) |> print()

# so' a area da mesa (a direita e' o placar, nao interessa)
X_MESA <- 320

base_mesa <- function(dados, titulo, sub) {
  ggplot(dados, aes(tela_x, y_plot)) +
    annotation_custom(fundo, xmin = 0, xmax = W, ymin = 0, ymax = H) +
    coord_fixed(xlim = c(0, X_MESA), ylim = c(0, H), expand = FALSE) +
    labs(title = titulo, subtitle = sub, x = NULL, y = NULL) +
    theme_minimal(base_size = 11) +
    theme(axis.text = element_blank(), panel.grid = element_blank(),
          legend.position = "bottom")
}

# 1. onde ele APERTA (cinza) x onde CONECTA (verde)
p1 <- base_mesa(tac, "Onde o flipper e' acionado x onde a tacada conecta",
                "cada ponto e' a posicao da bola no instante do acionamento") +
  geom_point(data = \(d) filter(d, acertou == 0),
             color = "grey70", size = .5, alpha = .35) +
  geom_point(data = \(d) filter(d, acertou == 1),
             color = "#2ca02c", size = 1.4, alpha = .85) +
  facet_wrap(~ lado)
ggsave("mesa_tacadas.png", p1, width = 10, height = 7.5, dpi = 150, bg = "white")

# 2. a zona da mascara desenhada sobre a mesa
z <- tac |>
  filter(acertou == 1) |>
  summarise(x0 = quantile(tela_x, .005), x1 = quantile(tela_x, .995),
            y0 = quantile(y_plot, .005), y1 = quantile(y_plot, .995), .by = lado)
print(z)

dentro <- tac |>
  left_join(z, by = "lado") |>
  mutate(na_zona = tela_x >= x0 & tela_x <= x1 & y_plot >= y0 & y_plot <= y1)
cat("\ntacadas preservadas:",
    scales::percent(mean(dentro$na_zona[dentro$acertou == 1]), .1),
    "| acionamentos liberados:", scales::percent(mean(dentro$na_zona), .1),
    "| spam cortado:", scales::percent(mean(!dentro$na_zona[dentro$acertou == 0]), .1), "\n")

p2 <- base_mesa(tac, "A mascara proposta, sobre a mesa",
                "verde = tacadas reais | retangulo = onde o flipper ficaria liberado") +
  geom_point(data = \(d) filter(d, acertou == 1),
             color = "#2ca02c", size = 1.2, alpha = .7) +
  geom_rect(data = z, aes(xmin = x0, xmax = x1, ymin = y0, ymax = y1),
            inherit.aes = FALSE, fill = "#d62728", alpha = .18,
            color = "#d62728", linewidth = .8, linetype = "22") +
  facet_wrap(~ lado)
ggsave("mesa_mascara.png", p2, width = 10, height = 7.5, dpi = 150, bg = "white")
write_csv(z, "mascara_tela.csv")
