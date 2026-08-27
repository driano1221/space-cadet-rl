# Baseline aleatorio do Space Cadet: 1000 partidas geradas headless.
# Objetivo: caracterizar a distribuicao de score antes de treinar qualquer agente.
library(tidyverse)

dados <- read_csv("dados/baseline_1000_aleatoria.csv", show_col_types = FALSE)

resumo <- dados |>
  summarise(
    n          = n(),
    media      = mean(score),
    mediana    = median(score),
    dp         = sd(score),
    p10        = quantile(score, .10),
    p90        = quantile(score, .90),
    maximo     = max(score),
    assimetria = mean((score - mean(score))^3) / sd(score)^3,
    razao_p90_p10 = quantile(score, .90) / quantile(score, .10)
  )
print(as.data.frame(resumo), digits = 4)

# Cauda pesada? Se log(score) for aproximadamente normal, a escala certa e' log.
cat("\nShapiro-Wilk (amostra de 500):\n")
cat("  score bruto:", shapiro.test(sample(dados$score, 500))$p.value, "\n")
cat("  log(score) :", shapiro.test(log(sample(dados$score, 500)))$p.value, "\n")

cat("\nDuracao media da partida:", round(mean(dados$segundos_jogo), 1), "s\n")
cat("Correlacao duracao x score:", round(cor(dados$segundos_jogo, dados$score), 3), "\n")

g <- ggplot(dados, aes(score)) +
  geom_histogram(bins = 40, fill = "#2c7fb8", colour = "white", linewidth = .2) +
  scale_x_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  labs(title = "Score do agente aleatorio no Space Cadet",
       subtitle = paste0(nrow(dados), " partidas, escala logaritmica"),
       x = "Score final", y = "Partidas") +
  theme_minimal()
ggsave("baseline_score.png", g, width = 7, height = 4.2, dpi = 150)
cat("\ngrafico: baseline_score.png\n")
