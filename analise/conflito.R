# O conflito central: sobreviver x pontuar.
# Varremos a probabilidade de apertar o flipper de 0 a 100% e medimos, para
# cada nivel, quanto o agente sobrevive e quanto pontua.
suppressMessages({library(data.table); library(ggplot2); library(dplyr); library(tidyr)})

dir <- "C:/Users/drian/Games/pinball_rl/analise/dados"
arqs <- list.files(dir, "^rl_prob_[0-9]+[.]csv$", full.names = TRUE)

d <- rbindlist(lapply(arqs, \(a) {
  p <- as.integer(gsub("[^0-9]", "", basename(a)))
  fread(a)[, prob := p]
}))

res <- d |>
  summarise(n = n(),
            duracao = mean(segundos_jogo),
            score_mediano = median(score),
            score_medio = mean(score),
            pontos_por_seg = median(score / segundos_jogo),
            saturou = mean(passos >= 72000),
            .by = prob) |>
  arrange(prob)
print(as.data.frame(res), digits = 5)

cat("\nPico de score  em prob =", res$prob[which.max(res$score_mediano)], "%\n")
cat("Pico de tempo  em prob =", res$prob[which.max(res$duracao)], "%\n")

longo <- res |>
  select(prob, `Sobrevivencia (s)` = duracao, `Score mediano` = score_mediano) |>
  pivot_longer(-prob)

g <- ggplot(longo, aes(prob, value)) +
  geom_line(linewidth = .9, colour = "#2c7fb8") +
  geom_point(size = 1.8, colour = "#2c7fb8") +
  facet_wrap(~name, scales = "free_y") +
  scale_x_continuous(labels = scales::label_percent(scale = 1)) +
  scale_y_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  labs(title = "Sobreviver e pontuar pedem estrategias opostas",
       subtitle = "150 partidas por nivel; prob. de manter cada flipper pressionado",
       x = "Probabilidade de apertar", y = NULL) +
  theme_minimal(base_size = 11)
ggsave("C:/Users/drian/Games/pinball_rl/analise/conflito_sobreviver_pontuar.png",
       g, width = 9, height = 4, dpi = 150)

g2 <- ggplot(res, aes(duracao, score_mediano, colour = prob)) +
  geom_path(linewidth = .7, alpha = .6) +
  geom_point(size = 3) +
  ggrepel::geom_text_repel(aes(label = paste0(prob, "%")), size = 3, show.legend = FALSE) +
  scale_colour_viridis_c(option = "plasma", name = "Prob.\napertar",
                         labels = scales::label_percent(scale = 1)) +
  scale_y_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  labs(title = "A fronteira entre sobreviver e pontuar",
       subtitle = "Cada ponto e' um nivel de agressividade; o canto superior direito seria o ideal",
       x = "Duracao media da partida (s)", y = "Score mediano") +
  theme_minimal(base_size = 11)
ggsave("C:/Users/drian/Games/pinball_rl/analise/fronteira_pareto.png",
       g2, width = 7.5, height = 5, dpi = 150)
cat("graficos salvos\n")
