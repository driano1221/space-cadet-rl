# O ambiente Python reproduz o comportamento do executavel C++?
# Comparamos as distribuicoes de score da mesma politica (30% de apertar).
suppressMessages({library(data.table); library(ggplot2); library(dplyr)})
dir <- "C:/Users/drian/Games/pinball_rl/analise/dados"

cpp <- fread(file.path(dir, "rl_prob_030.csv"))[, .(score, segundos_jogo, via = "C++ (.exe)")]
py  <- fread(file.path(dir, "py_prob_030.csv"))[, .(score, segundos_jogo, via = "Python (.pyd)")]
d <- rbind(cpp, py)

d |> summarise(n = n(), mediana = median(score), media = mean(score),
               p25 = quantile(score, .25), p75 = quantile(score, .75),
               duracao = mean(segundos_jogo), .by = via) |>
  as.data.frame() |> print(digits = 6)

ks <- ks.test(cpp$score, py$score)
w  <- wilcox.test(cpp$score, py$score)
cat("\nKolmogorov-Smirnov: D =", round(ks$statistic, 4), " p =", round(ks$p.value, 4), "\n")
cat("Mann-Whitney:        p =", round(w$p.value, 4), "\n")
cat(if (ks$p.value > .05 && w$p.value > .05)
      "-> as duas vias sao estatisticamente indistinguiveis\n"
    else "-> ATENCAO: as distribuicoes diferem\n")

g <- ggplot(d, aes(score, colour = via)) +
  stat_ecdf(linewidth = .9) +
  scale_x_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_colour_manual(values = c("#2c7fb8", "#d95f0e"), name = NULL) +
  labs(title = "O ambiente Python reproduz o executavel C++",
       subtitle = "Distribuicao acumulada do score, mesma politica (30% de apertar), 150 partidas cada",
       x = "Score final (escala log)", y = "Proporcao acumulada") +
  theme_minimal(base_size = 11) + theme(legend.position = "top")
ggsave("C:/Users/drian/Games/pinball_rl/analise/equivalencia.png", g,
       width = 7.5, height = 4.5, dpi = 150)
cat("grafico salvo\n")
