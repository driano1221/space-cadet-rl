# Quanto a resolucao temporal importa?
suppressMessages({library(data.table); library(ggplot2); library(tidyr); library(dplyr)})
d <- fread("C:/Users/drian/Games/pinball_rl/analise/dados/benchmark_quadros.csv")
print(as.data.frame(d), digits = 6)

longo <- d |>
  select(ms_por_decisao, `Aleatoria` = aleat_mediana, `Heuristica` = heur_mediana) |>
  pivot_longer(-ms_por_decisao, names_to = "politica", values_to = "score")

g <- ggplot(longo, aes(ms_por_decisao, score, colour = politica)) +
  geom_line(linewidth = .9) + geom_point(size = 2.6) +
  scale_x_continuous(breaks = d$ms_por_decisao,
                     labels = paste0(round(d$ms_por_decisao), "ms")) +
  scale_y_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_colour_manual(values = c("#2c7fb8", "#d95f0e"), name = NULL) +
  labs(title = "Resolucao temporal muda o jogo",
       subtitle = "Score mediano por intervalo entre decisoes, 30 partidas por ponto",
       x = "Intervalo entre decisoes", y = "Score mediano") +
  theme_minimal(base_size = 11) + theme(legend.position = "top")
ggsave("C:/Users/drian/Games/pinball_rl/analise/benchmark_quadros.png", g,
       width = 7.5, height = 4.4, dpi = 150)

g2 <- ggplot(d, aes(heur_duracao, heur_mediana)) +
  geom_path(colour = "#d95f0e", alpha = .6) +
  geom_point(aes(size = ms_por_decisao), colour = "#d95f0e") +
  geom_point(aes(x = aleat_duracao, y = aleat_mediana, size = ms_por_decisao),
             colour = "#2c7fb8") +
  scale_y_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_size_continuous(name = "ms/decisao") +
  labs(title = "A heuristica 'defensiva' cai na mesma armadilha",
       subtitle = "Laranja = heuristica que so' rebate a bola; azul = aleatoria",
       x = "Duracao media (s)", y = "Score mediano") +
  theme_minimal(base_size = 11)
ggsave("C:/Users/drian/Games/pinball_rl/analise/heuristica_armadilha.png", g2,
       width = 7, height = 4.4, dpi = 150)
cat("graficos salvos\n")
