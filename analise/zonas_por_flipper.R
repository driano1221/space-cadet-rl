# A area de ativacao de CADA flipper, sobre a mesa, e a regiao onde as duas se
# sobrepoem (a bola desce pelo mesmo funil).
library(tidyverse); library(jsonlite); library(png); library(grid)

mesa <- readPNG("mesa_fundo.png"); H <- dim(mesa)[1]; W <- dim(mesa)[2]
fundo <- rasterGrob(mesa, width = unit(1, "npc"), height = unit(1, "npc"))
z <- fromJSON("zona_flipper.json", simplifyVector = FALSE)
CEL <- z$celula

cel_df <- function(lista, nome) {
  map_dfr(lista, \(c) tibble(cx = c[[1]], cy = c[[2]])) |> mutate(lado = nome)
}
todas <- bind_rows(cel_df(z$zonas$esq, "esquerdo"), cel_df(z$zonas$dir, "direito"))
sobrep <- todas |> count(cx, cy) |> filter(n == 2) |> mutate(lado = "ambos")

cat("celulas esquerdo:", sum(todas$lado == "esquerdo"),
    "| direito:", sum(todas$lado == "direito"),
    "| sobrepostas:", nrow(sobrep), "\n")

# em pixels, com y ja' convertido para a convencao da imagem (H - y)
retangulos <- function(d) d |>
  mutate(x0 = cx * CEL, x1 = x0 + CEL,
         y1 = H - cy * CEL, y0 = y1 - CEL)

r_todas <- retangulos(todas); r_sobrep <- retangulos(sobrep)
cores <- c(esquerdo = "#1f77b4", direito = "#d62728", ambos = "#9467bd")

base <- function() list(
  annotation_custom(fundo, xmin = 0, xmax = W, ymin = 0, ymax = H),
  coord_fixed(xlim = c(90, 290), ylim = c(0, 130), expand = FALSE),
  theme_minimal(base_size = 11),
  theme(axis.text = element_blank(), panel.grid = element_blank(),
        legend.position = "bottom")
)

p1 <- ggplot() + base() +
  geom_rect(data = r_todas, aes(xmin = x0, xmax = x1, ymin = y0, ymax = y1, fill = lado),
            alpha = .45, color = NA) +
  scale_fill_manual(values = cores, name = NULL) +
  facet_wrap(~ lado) +
  labs(title = "Area de ativacao de cada flipper",
       subtitle = "a pa' so' responde com a bola dentro da area dela",
       x = NULL, y = NULL)
ggsave("zonas_por_flipper.png", p1, width = 11, height = 5.5, dpi = 140, bg = "white")

p2 <- ggplot() + base() +
  geom_rect(data = r_todas, aes(xmin = x0, xmax = x1, ymin = y0, ymax = y1, fill = lado),
            alpha = .3, color = NA) +
  geom_rect(data = r_sobrep, aes(xmin = x0, xmax = x1, ymin = y0, ymax = y1),
            fill = cores["ambos"], alpha = .75, color = NA) +
  scale_fill_manual(values = cores, name = NULL) +
  labs(title = "As duas areas sobrepostas",
       subtitle = paste0("roxo = ", nrow(sobrep), " celulas onde AMBAS as pa's podem ser acionadas ",
                         "(a bola desce pelo mesmo funil)"),
       x = NULL, y = NULL)
ggsave("zonas_sobreposicao.png", p2, width = 8, height = 6, dpi = 140, bg = "white")
