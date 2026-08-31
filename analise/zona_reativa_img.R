# Compara a zona antiga (gatilho, para o env de opcoes) com a nova (janela de
# controle, para decisao continua) sobre a mesa.
library(tidyverse); library(jsonlite); library(png); library(grid)

mesa <- readPNG("mesa_fundo.png"); H <- dim(mesa)[1]; W <- dim(mesa)[2]
fundo <- rasterGrob(mesa, width = unit(1, "npc"), height = unit(1, "npc"))

ler <- function(arq, nome) {
  z <- fromJSON(arq, simplifyVector = FALSE)
  map_dfr(c("esq", "dir"), \(l)
    map_dfr(z$zonas[[l]], \(c) tibble(cx = c[[1]], cy = c[[2]])) |>
      mutate(lado = if_else(l == "esq", "esquerdo", "direito"))) |>
    mutate(versao = nome, cel = z$celula)
}
tudo <- bind_rows(ler("zona_flipper.json", "anterior (dilatada): subia demais"),
                  ler("zona_reativa.json", "nova (trajetoria 100ms): 4,1% do tempo")) |>
  mutate(x0 = cx * cel, x1 = x0 + cel, y1 = H - cy * cel, y0 = y1 - cel,
         versao = fct_relevel(versao, "anterior (dilatada): subia demais"))

tac <- read_csv("tacadas_tela.csv", show_col_types = FALSE) |>
  filter(acertou == 1) |> mutate(y_plot = H - tela_y)

p <- ggplot() +
  annotation_custom(fundo, xmin = 0, xmax = W, ymin = 0, ymax = H) +
  geom_rect(data = tudo, aes(xmin = x0, xmax = x1, ymin = y0, ymax = y1, fill = lado),
            alpha = .38, color = NA) +
  geom_point(data = tac, aes(tela_x, y_plot), color = "#ffe94d", size = .35, alpha = .55) +
  coord_fixed(xlim = c(80, 300), ylim = c(0, 150), expand = FALSE) +
  scale_fill_manual(values = c(esquerdo = "#1f77b4", direito = "#d62728"), name = NULL) +
  facet_wrap(~ versao) +
  labs(title = "Zona antiga x zona nova",
       subtitle = "amarelo = tacadas que conectaram | area colorida = onde a pa' responde",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 11) +
  theme(axis.text = element_blank(), panel.grid = element_blank(),
        legend.position = "bottom")
ggsave("zona_antiga_vs_nova.png", p, width = 12, height = 6, dpi = 140, bg = "white")
tudo |> count(versao, lado) |> print()
