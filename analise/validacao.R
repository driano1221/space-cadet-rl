# Validacao da instrumentacao: se o input nao chegasse ao jogo, as tres
# politicas dariam resultados iguais. Elas nao dao.
suppressMessages(library(tidyverse))
base <- "C:/Users/drian/Games/pinball_rl/analise/dados"
rotulos <- c("0" = "Nula\n(nunca aperta)", "1" = "Aleatoria", "2" = "Sempre apertado")

d <- map_dfr(0:2, \(p) read_csv(file.path(base, paste0("rl_dados_p", p, ".csv")),
                                show_col_types = FALSE) |> mutate(politica = as.character(p))) |>
  mutate(politica = factor(rotulos[politica], levels = rotulos))

d |> summarise(n = n(), mediana = median(score), duracao = mean(segundos_jogo),
               .by = politica) |> as.data.frame() |> print(digits = 6)

# Normalidade: o log melhora muito, mas ainda rejeita a 5%.
alea <- d |> filter(politica == "Aleatoria") |> pull(score)
cat("\nShapiro bruto:", format.pval(shapiro.test(alea)$p.value),
    "| log:", format.pval(shapiro.test(log(alea))$p.value), "\n")

g <- ggplot(d, aes(politica, score, fill = politica)) +
  geom_violin(alpha = .55, colour = NA) +
  geom_boxplot(width = .16, outlier.size = .5, fill = "white") +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = c("#8c96c6", "#2c7fb8", "#d95f0e"), guide = "none") +
  labs(title = "Tres politicas, mesma semente, 300 partidas cada",
       subtitle = "Se os flippers nao respondessem, as distribuicoes seriam iguais",
       x = NULL, y = "Score final (escala log)") +
  theme_minimal(base_size = 11)
ggsave("C:/Users/drian/Games/pinball_rl/analise/validacao_politicas.png", g,
       width = 7, height = 4.4, dpi = 150)
cat("grafico salvo\n")
