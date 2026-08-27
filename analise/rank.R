# O agente pontua 11x mais que o acaso e progride igual: nao usa missoes.
suppressMessages({library(data.table); library(ggplot2); library(patchwork)})
d <- fread("C:/Users/drian/Games/pinball_rl/analise/dados/rank_medido.csv")
d[, agente := factor(fifelse(agente == "ppo", "PPO com visao", "Aleatorio"),
                     levels = c("Aleatorio", "PPO com visao"))]

print(as.data.frame(d[, .(n = .N, score_mediano = median(score),
    rank_medio = mean(rank_max), rank_max = max(rank_max),
    prog_medio = mean(prog_max)), by = agente]), digits = 5)

cores <- c("Aleatorio" = "#2c7fb8", "PPO com visao" = "#238b45")

g1 <- ggplot(d, aes(agente, score, fill = agente)) +
  geom_boxplot(width = .45, outlier.size = .8) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = cores, guide = "none") +
  labs(title = "Score: 11x de diferenca", x = NULL, y = "Score (log)") +
  theme_minimal(base_size = 10)

g2 <- ggplot(d, aes(agente, rank_max, fill = agente)) +
  geom_boxplot(width = .45) +
  scale_y_continuous(breaks = 1:9, limits = c(1, 9)) +
  scale_fill_manual(values = cores, guide = "none") +
  labs(title = "Rank: praticamente igual",
       subtitle = "9 patentes possiveis; ambos param no 4",
       x = NULL, y = "Rank alcancado") +
  theme_minimal(base_size = 10)

g3 <- ggplot(d, aes(rank_max, score, colour = agente)) +
  geom_jitter(width = .12, size = 2.4, alpha = .8) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_x_continuous(breaks = 1:9) +
  scale_colour_manual(values = cores, name = NULL) +
  labs(title = "Pontua muito mais sem progredir mais",
       subtitle = "Cada ponto e' uma partida. O eixo do rank quase nao se move.",
       x = "Rank alcancado", y = "Score (log)") +
  theme_minimal(base_size = 10) + theme(legend.position = "top")

ggsave("C:/Users/drian/Games/pinball_rl/analise/rank.png",
       (g1 | g2) / g3 + plot_layout(heights = c(1, 1.15)),
       width = 9, height = 8, dpi = 145)
cat("rank.png salvo\n")
