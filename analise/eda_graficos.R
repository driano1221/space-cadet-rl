suppressMessages({library(data.table); library(ggplot2); library(dplyr); library(patchwork)})
dir <- "C:/Users/drian/Games/pinball_rl/analise/dados"
d <- rbindlist(list(
  fread(file.path(dir, "eda_aleatoria.csv"))[, pol := "Aleatoria"],
  fread(file.path(dir, "eda_heuristica.csv"))[, pol := "Heuristica"]))
cores <- c("Aleatoria" = "#2c7fb8", "Heuristica" = "#d95f0e")

g1 <- ggplot(d, aes(speed, fill = pol)) +
  geom_histogram(bins = 60, alpha = .75, position = "identity") +
  scale_fill_manual(values = cores, name = NULL) +
  labs(title = "A bola esta parada",
       subtitle = "Distribuicao da velocidade da bola. 83% do tempo a heuristica a mantem quase imovel.",
       x = "Velocidade", y = "Amostras") +
  theme_minimal(base_size = 10) + theme(legend.position = "top")

g2 <- ggplot(d, aes(tela_x, tela_y, fill = after_stat(count))) +
  geom_bin2d(bins = 70) +
  scale_fill_viridis_c(option = "inferno", trans = "log10", guide = "none") +
  scale_y_reverse() + coord_fixed() + facet_wrap(~pol) +
  labs(title = "Onde a bola passa o tempo",
       subtitle = "A heuristica prende a bola na base, entre os flippers",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 10) +
  theme(panel.grid = element_blank(), axis.text = element_blank())

ep <- d[, .(score = max(score)), by = .(pol, episodio)]
g3 <- ggplot(ep, aes(pol, score, fill = pol)) +
  geom_violin(alpha = .5, colour = NA) +
  geom_boxplot(width = .16, fill = "white", outlier.size = .7) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = cores, guide = "none") +
  labs(title = "Score final", subtitle = "25 partidas por politica, escala log",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 10)

g4 <- ggplot(d[, .(score = max(score)), by = .(pol, episodio, minuto = floor(tempo_s/30)*0.5)],
             aes(minuto, score, group = interaction(pol, episodio), colour = pol)) +
  geom_line(alpha = .35) +
  scale_colour_manual(values = cores, guide = "none") +
  scale_y_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  facet_wrap(~pol, scales = "free_x") +
  labs(title = "Score ao longo da partida",
       subtitle = "Cada linha e' um episodio; a heuristica pontua devagar e por muito mais tempo",
       x = "Minutos de jogo", y = NULL) +
  theme_minimal(base_size = 10)

ggsave("C:/Users/drian/Games/pinball_rl/analise/eda_completa.png",
       (g1 | g3) / g2 / g4 + plot_layout(heights = c(1, 1.25, 1)),
       width = 11, height = 12, dpi = 140)
cat("eda_completa.png salvo\n")
