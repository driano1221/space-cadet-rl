# EDA da curva de escala: 2,5M vs 5M vs 7,5M passos.
# Procura anomalia, nao so' media - a licao que o berco ensinou.
suppressMessages({library(data.table); library(ggplot2); library(dplyr); library(patchwork)})
d <- fread("C:/Users/drian/Games/pinball_rl/python/curva_escala.csv")
d[, rot := fifelse(modelo == "aleatorio", "aleatorio",
            fifelse(modelo == "ppo_visao_v1", "ref 2,5M",
             paste0(round(passos/1e6, 1), "M")))]
ordem <- c("aleatorio", "ref 2,5M", "2.5M", "5M", "7.5M")
d <- d[rot %in% ordem][, rot := factor(rot, levels = ordem)]

cat("=== RESUMO ===\n")
print(as.data.frame(d[, .(n = .N, mediana = median(score), media = mean(score),
    dp = sd(score), cv = sd(score)/mean(score), min = min(score), max = max(score),
    duracao = mean(duracao), alvos = mean(alvos), missoes = mean(missoes),
    vel = mean(vel), parada = mean(parada), topo = mean(topo)), by = rot]), digits = 4)

cat("\n=== TESTE: algum checkpoint difere do de 2,5M? ===\n")
base <- d[rot == "2.5M", score]
for (r in c("5M", "7.5M")) {
  x <- d[rot == r, score]
  if (length(x)) cat(sprintf("  2,5M vs %-5s: p = %.3f  (razao das medianas %.2f)\n",
                             r, wilcox.test(base, x)$p.value, median(x)/median(base)))
}

cores <- c("aleatorio"="#08519c","ref 2,5M"="#bdbdbd","2.5M"="#a1d99b","5M"="#41ab5d","7.5M"="#238b45")

g1 <- ggplot(d, aes(rot, score, fill = rot)) +
  geom_violin(alpha=.5, colour=NA) + geom_boxplot(width=.16, fill="white", outlier.size=.7) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = cores, guide = "none") +
  labs(title="Score por orcamento de treino", x=NULL, y="Score (log)") +
  theme_minimal(base_size=10)

g2 <- ggplot(d[rot != "aleatorio"], aes(rot, vel, fill = rot)) +
  geom_boxplot(width=.5) + scale_fill_manual(values=cores, guide="none") +
  geom_hline(yintercept=0.17, linetype="22", colour="#d95f0e") +
  annotate("text", x=1.6, y=1.2, label="faixa do berco", colour="#d95f0e", size=3) +
  labs(title="Velocidade da bola (anomalia?)", x=NULL, y="Velocidade mediana") +
  theme_minimal(base_size=10)

g3 <- ggplot(d[rot != "aleatorio"], aes(rot, topo, fill = rot)) +
  geom_boxplot(width=.5) + scale_fill_manual(values=cores, guide="none") +
  labs(title="Tempo no topo (onde ficam os alvos)", x=NULL, y="% do tempo") +
  theme_minimal(base_size=10)

g4 <- ggplot(d[rot != "aleatorio"], aes(rot, alvos, fill = rot)) +
  geom_boxplot(width=.5) + scale_fill_manual(values=cores, guide="none") +
  labs(title="Alvos de missao acertados", x=NULL, y="por partida") +
  theme_minimal(base_size=10)

ggsave("C:/Users/drian/Games/pinball_rl/analise/eda_escala.png",
       (g1 | g2) / (g3 | g4), width=10, height=8, dpi=145)
cat("\neda_escala.png salvo\n")
