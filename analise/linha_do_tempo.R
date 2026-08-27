# Linha do tempo do projeto: todos os agentes, do primeiro ao ultimo.
#
# Os agentes 1-3 vem das avaliacoes originais (obs de 9 valores, incompativel
# com o ambiente atual). Os demais foram medidos juntos, na mesma sessao.
suppressMessages({library(data.table); library(ggplot2); library(dplyr); library(patchwork)})

novo <- fread("C:/Users/drian/Games/pinball_rl/analise/dados/comparacao_geral.csv")

# historico dos que nao rodam mais no ambiente atual
hist <- data.table(
  agente = c("1. score cru (50ms)", "2. + bonus sobrevivencia", "3. sem bonus"),
  score = c(144750, 72000, 154500),
  duracao = c(98, 264, 120),
  medicao = "historico")

res <- novo[, .(score = median(score), duracao = mean(duracao),
                rank = mean(rank), progresso = mean(progresso),
                alvos = mean(alvos), missoes = mean(missoes),
                vel = mean(vel_mediana), parada = mean(pct_parada),
                topo = mean(pct_topo), ambos = mean(pct_ambos)),
            by = agente][, medicao := "uniforme"]

todos <- rbindlist(list(hist, res), fill = TRUE)
ordem <- c("Aleatorio", "1. score cru (50ms)", "2. + bonus sobrevivencia",
           "3. sem bonus", "4. 25ms + flippers", "5. VISAO DA MESA",
           "6. sobrevivencia pura", "7. + progresso de rank", "8. + fluxo de missao")
todos[, agente := factor(agente, levels = rev(ordem))]
setorder(todos, -agente)
print(as.data.frame(todos), digits = 5)
fwrite(todos, "C:/Users/drian/Games/pinball_rl/analise/dados/resumo_agentes.csv")

cores <- c(uniforme = "#238b45", historico = "#969696")

g1 <- ggplot(todos, aes(agente, score, fill = medicao)) +
  geom_col(width = .68) +
  geom_hline(yintercept = todos[agente == "Aleatorio", score],
             linetype = "22", colour = "#08519c", linewidth = .7) +
  annotate("text", x = 1.4, y = todos[agente == "Aleatorio", score] * 1.35,
           label = "acaso", colour = "#08519c", size = 3.2) +
  scale_y_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = cores, name = NULL,
                    labels = c(historico = "medicao antiga", uniforme = "medicao uniforme")) +
  coord_flip() +
  labs(title = "Todos os agentes, do primeiro ao ultimo",
       subtitle = "Score mediano. Cinza = avaliacao original, nao comparavel diretamente.",
       x = NULL, y = "Score mediano") +
  theme_minimal(base_size = 10) + theme(legend.position = "top")

d2 <- todos[medicao == "uniforme"]
g2 <- ggplot(d2, aes(vel, topo, colour = agente, size = score)) +
  geom_point(alpha = .85) +
  scale_size_continuous(range = c(3, 11), guide = "none") +
  labs(title = "Como cada um joga",
       subtitle = "Direita e acima = bola rapida e no topo, onde ficam os alvos. Tamanho = score.",
       x = "Velocidade mediana da bola", y = "% do tempo no topo da mesa") +
  theme_minimal(base_size = 10) + theme(legend.position = "right",
                                        legend.title = element_blank())

ggsave("C:/Users/drian/Games/pinball_rl/analise/linha_do_tempo.png",
       g1 / g2 + plot_layout(heights = c(1.15, 1)), width = 9.5, height = 9.5, dpi = 145)
cat("linha_do_tempo.png salvo\n")
