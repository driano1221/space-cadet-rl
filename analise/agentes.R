# Como a funcao de recompensa muda o comportamento aprendido.
suppressMessages({library(data.table); library(ggplot2); library(dplyr)})
dir <- "C:/Users/drian/Games/pinball_rl/python"

le <- function(arq, rotulo, fase = "depois") {
  a <- file.path(dir, arq)
  if (!file.exists(a)) return(NULL)
  fread(a)[fase_ := fase][fase == get("fase_")][, .(score, duracao, agente = rotulo)]
}

d <- rbindlist(list(
  fread(file.path(dir, "resultado_score.csv"))[fase == "antes"][
    , .(score, duracao, agente = "Aleatorio")],
  fread(file.path(dir, "resultado_score.csv"))[fase == "depois"][
    , .(score, duracao, agente = "PPO: score cru")],
  fread(file.path(dir, "resultado2_score.csv"))[fase == "depois"][
    , .(score, duracao, agente = "PPO: score + bonus de sobrevivencia")],
  fread(file.path(dir, "resultado3_score.csv"))[fase == "depois"][
    , .(score, duracao, agente = "PPO: sem bonus, 50ms")],
  fread(file.path(dir, "resultado4_score.csv"))[fase == "depois"][
    , .(score, duracao, agente = "PPO: 25ms + estado dos flippers")],
  fread(file.path(dir, "resultado4_score.csv"))[fase == "antes"][
    , .(score, duracao, agente = "Aleatorio a 25ms")]
), use.names = TRUE)

ordem <- c("Aleatorio a 25ms", "Aleatorio", "PPO: 25ms + estado dos flippers",
           "PPO: sem bonus, 50ms", "PPO: score cru",
           "PPO: score + bonus de sobrevivencia")
d[, agente := factor(agente, levels = ordem)]

# Metricas completas: a mediana sozinha esconde a cauda, que e' onde mora o
# score alto no pinball.
d |> summarise(n = n(), media = mean(score), dp = sd(score),
               cv = sd(score) / mean(score), min = min(score),
               mediana = median(score), q75 = quantile(score, .75),
               max = max(score), duracao = mean(duracao),
               .by = agente) |> as.data.frame() |> print(digits = 5)

g <- ggplot(d, aes(duracao, score, colour = agente)) +
  geom_point(size = 2, alpha = .65) +
  stat_summary(fun = median, geom = "point", size = 6, shape = 18) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_colour_manual(values = c("#08519c", "#8c96c6", "#31a354", "#74c476",
                                 "#d95f0e", "#c51b8a"), name = NULL) +
  labs(title = "A recompensa decide o que o agente aprende",
       subtitle = "Losangos = mediana. 40 partidas por agente. Nenhum PPO bateu o aleatorio, mas a distancia caiu.",
       x = "Duracao da partida (s)", y = "Score final (log)") +
  theme_minimal(base_size = 11) +
  theme(legend.position = "top", legend.direction = "vertical")
ggsave("C:/Users/drian/Games/pinball_rl/analise/agentes.png", g,
       width = 7.5, height = 5.4, dpi = 150)
cat("grafico salvo\n")
