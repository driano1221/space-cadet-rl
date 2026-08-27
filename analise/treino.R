# Compara o agente antes e depois do treino, na escala certa (log).
suppressMessages({library(data.table); library(ggplot2); library(dplyr)})
dir <- "C:/Users/drian/Games/pinball_rl/python"
arq <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(arq)) arq <- "resultado2_score.csv"

d <- fread(file.path(dir, arq))
d[, fase := factor(fase, levels = c("antes", "depois"),
                   labels = c("Aleatorio", "PPO treinado"))]

d |> summarise(n = n(), mediana = median(score), media = mean(score),
               p25 = quantile(score, .25), p75 = quantile(score, .75),
               duracao = mean(duracao), .by = fase) |>
  as.data.frame() |> print(digits = 6)

a <- d[fase == "Aleatorio", score]; b <- d[fase == "PPO treinado", score]
w <- wilcox.test(a, b)
cat("\nMann-Whitney p =", format.pval(w$p.value, digits = 3), "\n")
cat("razao das medianas:", round(median(b) / median(a), 2), "x\n")

g <- ggplot(d, aes(fase, score, fill = fase)) +
  geom_violin(alpha = .5, colour = NA) +
  geom_boxplot(width = .15, fill = "white", outlier.size = .6) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = c("#8c96c6", "#2c7fb8"), guide = "none") +
  labs(title = "Agente antes e depois do treino",
       subtitle = paste0(nrow(d) / 2, " partidas por fase, escala log"),
       x = NULL, y = "Score final") +
  theme_minimal(base_size = 11)
ggsave("C:/Users/drian/Games/pinball_rl/analise/treino_resultado.png", g,
       width = 6.5, height = 4.2, dpi = 150)
cat("grafico salvo\n")
