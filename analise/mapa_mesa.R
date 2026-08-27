# Validacao visual: se os dados de trajetoria forem reais, a densidade das
# posicoes da bola tem de desenhar o formato da mesa. Serve tambem para
# comparar ONDE cada politica mantem a bola.
suppressMessages({library(data.table); library(ggplot2); library(dplyr)})

dir <- "C:/Users/drian/Games/pinball_rl/analise/dados"
rot <- c("0" = "Nula (nunca aperta)", "1" = "Aleatoria", "2" = "Sempre apertado")

d <- rbindlist(lapply(0:2, \(p) {
  x <- fread(file.path(dir, sprintf("rl_trace_p%d.csv", p)),
             select = c("bola_x", "bola_y", "score", "tempo_s", "episodio"))
  x[, politica := rot[as.character(p)]]
}))
d <- d[bola_x > -90]
d[, politica := factor(politica, levels = rot)]
cat("linhas totais:", format(nrow(d), big.mark = "."), "\n")

g <- ggplot(d, aes(bola_x, bola_y)) +
  geom_bin2d(bins = 90) +
  scale_fill_viridis_c(option = "inferno", trans = "log10",
                       labels = scales::label_number(scale_cut = scales::cut_short_scale()),
                       name = "Passos") +
  coord_fixed() +
  facet_wrap(~politica) +
  labs(title = "Onde a bola passa o tempo, por politica",
       subtitle = "Densidade de posicoes da bola; escala de cor logaritmica",
       x = "x (unidades da mesa)", y = "y (unidades da mesa)") +
  theme_minimal(base_size = 11) +
  theme(panel.grid = element_blank())
ggsave("C:/Users/drian/Games/pinball_rl/analise/mapa_mesa.png", g,
       width = 10, height = 5.2, dpi = 150)
cat("mapa_mesa.png salvo\n")
