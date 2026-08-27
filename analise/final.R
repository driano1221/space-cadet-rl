# O resultado do projeto: a visao da mesa foi o que destravou o aprendizado.
suppressMessages({library(data.table); library(ggplot2); library(dplyr); library(patchwork)})
dir <- "C:/Users/drian/Games/pinball_rl/python"

le <- function(arq, rot, qual = "depois") {
  a <- file.path(dir, arq)
  if (!file.exists(a)) return(NULL)
  x <- fread(a)
  x <- x[x$fase == qual, ]
  data.table(score = x$score, duracao = x$duracao, agente = rot)
}
d <- rbindlist(list(
  le("resultado_visao_v1.csv", "Aleatorio", "antes"),
  le("resultado_score.csv", "PPO sem visao (score cru)"),
  le("resultado2_score.csv", "PPO sem visao (+ bonus)"),
  le("resultado4_score.csv", "PPO sem visao (25ms + flippers)"),
  le("resultado_visao_v1.csv", "PPO COM VISAO DA MESA")
), use.names = TRUE)

ordem <- c("PPO COM VISAO DA MESA", "Aleatorio", "PPO sem visao (25ms + flippers)",
           "PPO sem visao (score cru)", "PPO sem visao (+ bonus)")
d[, agente := factor(agente, levels = rev(ordem))]

cat("=== RESULTADO FINAL ===\n")
print(as.data.frame(d |> summarise(n = n(), mediana = median(score), media = mean(score),
      dp = sd(score), cv = sd(score)/mean(score), min = min(score), max = max(score),
      duracao = mean(duracao), .by = agente) |> arrange(desc(mediana))), digits = 5)

a <- d[agente == "Aleatorio", score]; b <- d[agente == "PPO COM VISAO DA MESA", score]
w <- wilcox.test(a, b)
cat("\nPPO com visao x aleatorio: razao das medianas =",
    round(median(b)/median(a), 2), "x | Mann-Whitney p =", format.pval(w$p.value, digits=3), "\n")

cores <- c("PPO COM VISAO DA MESA" = "#238b45", "Aleatorio" = "#08519c",
           "PPO sem visao (25ms + flippers)" = "#74c476",
           "PPO sem visao (score cru)" = "#d95f0e", "PPO sem visao (+ bonus)" = "#c51b8a")

g1 <- ggplot(d, aes(agente, score, fill = agente)) +
  geom_violin(alpha = .55, colour = NA) +
  geom_boxplot(width = .15, fill = "white", outlier.size = .6) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = cores, guide = "none") +
  coord_flip() +
  labs(title = "A visao da mesa foi o que destravou o aprendizado",
       subtitle = "40 partidas por agente, escala logaritmica",
       x = NULL, y = "Score final") +
  theme_minimal(base_size = 11)

g2 <- ggplot(d, aes(duracao, score, colour = agente)) +
  geom_point(size = 2, alpha = .6) +
  stat_summary(fun = median, geom = "point", size = 6, shape = 18) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_colour_manual(values = cores, name = NULL) +
  labs(subtitle = "Losangos = mediana. Canto superior direito = joga bem e sobrevive.",
       x = "Duracao da partida (s)", y = "Score (log)") +
  theme_minimal(base_size = 10) +
  theme(legend.position = "bottom", legend.direction = "vertical")

ggsave("C:/Users/drian/Games/pinball_rl/analise/resultado_final.png",
       g1 / g2 + plot_layout(heights = c(1, 1.3)), width = 9, height = 10, dpi = 145)
cat("resultado_final.png salvo\n")
