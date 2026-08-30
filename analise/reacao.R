# O agente e' bom por estrategia ou por reflexo? A curva responde.
suppressMessages({library(data.table); library(ggplot2); library(patchwork)})
d <- fread("C:/Users/drian/Games/pinball_rl/analise/dados/reacao.csv")
ACASO <- 404375

res <- d[, .(mediana = median(score), q25 = quantile(score,.25),
             q75 = quantile(score,.75), duracao = mean(duracao),
             rampas = mean(rampas)), by = atraso]
print(as.data.frame(res), digits = 6)

g1 <- ggplot(res, aes(atraso, mediana)) +
  annotate("rect", xmin = 200, xmax = 300, ymin = -Inf, ymax = Inf,
           fill = "#fdae6b", alpha = .30) +
  annotate("text", x = 250, y = 1.35e6, label = "faixa humana\n200-300 ms",
           size = 3.1, colour = "#8c4a10") +
  geom_hline(yintercept = ACASO, linetype = "22", colour = "#08519c") +
  annotate("text", x = 355, y = ACASO * 1.22, label = "politica aleatoria",
           size = 3.1, colour = "#08519c") +
  geom_ribbon(aes(ymin = q25, ymax = q75), fill = "#238b45", alpha = .18) +
  geom_line(colour = "#238b45", linewidth = 1) +
  geom_point(colour = "#238b45", size = 3) +
  scale_y_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  labs(title = "O agente joga por reflexo, nao por estrategia",
       subtitle = paste("50 ms de atraso ja' custam 79% do score. Com latencia humana,",
                        "ele fica\nabaixo da politica aleatoria."),
       x = "Atraso de reacao imposto (ms)", y = "Score mediano") +
  theme_minimal(base_size = 11)

g2 <- ggplot(res, aes(atraso, duracao)) +
  geom_line(colour = "#d95f0e", linewidth = 1) + geom_point(colour = "#d95f0e", size = 2.6) +
  labs(title = "Duracao da partida", x = "Atraso (ms)", y = "segundos") +
  theme_minimal(base_size = 10)

g3 <- ggplot(res, aes(atraso, rampas)) +
  geom_line(colour = "#6a51a3", linewidth = 1) + geom_point(colour = "#6a51a3", size = 2.6) +
  labs(title = "Passagens pela rampa de lancamento",
       subtitle = "3,7 por partida: nao ha' loop de exploracao",
       x = "Atraso (ms)", y = "por partida") +
  theme_minimal(base_size = 10)

ggsave("C:/Users/drian/Games/pinball_rl/analise/reacao.png",
       g1 / (g2 | g3) + plot_layout(heights = c(1.5, 1)), width = 9, height = 8.5, dpi = 145)
cat("reacao.png salvo\n")
