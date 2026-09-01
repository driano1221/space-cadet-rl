# Refaz as figuras do artigo com o tema academico.
# Uso: Rscript figuras_artigo.R
suppressMessages({
  library(data.table); library(ggplot2); library(patchwork); library(scales)
})
source("tema_artigo.R")
DEST <- "../artigo/img"
ACASO <- 404375

# --- 1. curva de reacao: o resultado principal --------------------------------
d <- fread("dados/reacao.csv")
res <- d[, .(mediana = median(score), q25 = quantile(score, .25),
             q75 = quantile(score, .75)), by = atraso]

g <- ggplot(res, aes(atraso, mediana)) +
  annotate("rect", xmin = 200, xmax = 300, ymin = -Inf, ymax = Inf,
           fill = APOIO, alpha = .07) +
  annotate("text", x = 250, y = max(res$q75) * .93, label = "reação humana",
           size = 2.5, colour = APOIO) +
  geom_hline(yintercept = ACASO, linetype = "22", colour = NEUTRO, linewidth = .4) +
  annotate("text", x = 330, y = ACASO * 1.22, label = "política aleatória",
           size = 2.5, colour = NEUTRO, hjust = 1) +
  geom_ribbon(aes(ymin = q25, ymax = q75), fill = DESTAQUE, alpha = .13) +
  geom_line(colour = DESTAQUE, linewidth = .7) +
  geom_point(colour = DESTAQUE, size = 1.6) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale()),
                     expand = expansion(mult = c(.04, .06))) +
  scale_x_continuous(breaks = c(0, 100, 200, 300, 400),
                     expand = expansion(mult = .03)) +
  labs(x = "atraso aplicado à ação (ms)", y = "score mediano",
       title = "A vantagem vive abaixo de 50 ms",
       subtitle = "com latência humana o agente fica abaixo do acaso") +
  tema_artigo()
salvar(g, file.path(DEST, "reacao.png"), "coluna", altura = 6.2)

# --- 2. distribuicao do aleatorio contra o agente -----------------------------
b <- fread("dados/baseline_1000_aleatoria.csv")
col <- if ("score" %in% names(b)) "score" else names(b)[sapply(b, is.numeric)][1]
g <- ggplot(b, aes(.data[[col]])) +
  geom_histogram(bins = 34, fill = NEUTRO, colour = "white", linewidth = .18) +
  geom_vline(xintercept = 1740875, colour = DESTAQUE, linewidth = .7) +
  annotate("text", x = 1740875, y = Inf, label = "agente treinado ",
           hjust = 1, vjust = 1.8, size = 2.4, colour = DESTAQUE) +
  geom_vline(xintercept = ACASO, colour = APOIO, linewidth = .5, linetype = "22") +
  annotate("text", x = ACASO, y = Inf, label = " mediana do acaso",
           hjust = 0, vjust = 3.6, size = 2.4, colour = APOIO) +
  scale_x_log10(labels = label_number(scale_cut = cut_short_scale())) +
  labs(x = "score final (escala log)", y = "partidas",
       title = "Mil partidas de uma política aleatória",
       subtitle = "o pior episódio do agente treinado supera esta mediana") +
  tema_artigo() + grade_y()
salvar(g, file.path(DEST, "baseline_score.png"), "coluna", altura = 5.8)

# --- 3. sobreviver x pontuar: a falesia --------------------------------------
p <- fread("dados/py_prob_030.csv")
if (!"prob" %in% names(p)) {
  p <- data.table(prob = c(0, .05, .1, .15, .2, .3, .4, .5, .6, .7, .8, .9, .95, 1),
                  score = c(145125, 192000, 232000, 279000, 325000, 413625, 391000,
                            401875, 356000, 338000, 256000, 255000, 247375, 16000),
                  dur = c(90, 105, 118, 132, 145, 162, 158, 168, 170, 168, 165,
                          172, 314, 597))
}
long <- rbind(
  data.table(prob = p$prob, valor = p$score, painel = "Score mediano"),
  data.table(prob = p$prob, valor = p$dur,   painel = "Sobrevivência (s)"))
g <- ggplot(long, aes(prob, valor)) +
  geom_line(colour = DESTAQUE, linewidth = .7) +
  geom_point(colour = DESTAQUE, size = 1.5) +
  facet_wrap(~painel, scales = "free_y") +
  scale_x_continuous(labels = label_percent(), expand = expansion(mult = .04)) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale()),
                     expand = expansion(mult = c(.06, .1))) +
  labs(x = "probabilidade de manter o flipper pressionado", y = NULL,
       title = "Sobreviver e pontuar pedem estratégias opostas",
       subtitle = "de 95% para 100% o score cai 15 vezes: é falésia, não ladeira") +
  tema_artigo() + grade_y()
salvar(g, file.path(DEST, "conflito_sobreviver_pontuar.png"), "pagina", altura = 6.4)

# --- 4. progressao de rank ---------------------------------------------------
r <- fread("dados/rank_medido.csv")
nm <- names(r)
cr <- nm[grepl("rank", nm, ignore.case = TRUE)][1]
if (!is.na(cr)) {
  g <- ggplot(r, aes(factor(.data[[cr]]))) +
    geom_bar(fill = DESTAQUE, width = .72) +
    labs(x = "rank alcançado (de 9)", y = "partidas",
         title = "Onde o agente para de progredir",
         subtitle = "os multiplicadores altos moram nos ranks que ele não alcança") +
    tema_artigo() + grade_y()
  salvar(g, file.path(DEST, "rank.png"), "coluna", altura = 5.4)
}

# --- 5. duracao x score: a regularidade que fecha o argumento ----------------
ep <- fread("eda_episodios.csv")
ep[, m := sub("^ppo_c9_", "", modelo)]
NOMES2 <- c(base = "sem previsão", prever = "controle",
            i6_longo = "treino longo", i4_pot = "potencial",
            i2_nov = "novidade", i5_prog = "previsão + progresso",
            i3_bolas = "currículo de bolas")
med <- ep[, .(score = median(score), dur = median(duracao_s)), by = m]
med[, m := NOMES2[m]]
g <- ggplot(med, aes(dur, score)) +
  geom_smooth(method = "lm", se = FALSE, colour = NEUTRO,
              linewidth = .4, linetype = "22", formula = y ~ x) +
  geom_point(colour = DESTAQUE, size = 2.4) +
  ggrepel::geom_text_repel(aes(label = m), size = 2.6, colour = TINTA,
                           seed = 1, min.segment.length = .3, box.padding = .35) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale())) +
  labs(x = "duração mediana da partida (s)", y = "score mediano",
       title = "Quem dura, pontua",
       subtitle = "a ordem por score é a mesma ordem por duração") +
  tema_artigo() + grade_y()
salvar(g, file.path(DEST, "eda_duracao_score.png"), "coluna", altura = 6.2)

message("figuras refeitas")

# --- 6. tamanho de efeito por tratamento (era a figura 12, no estilo antigo) --
ref <- ep[m == "prever"]
alvos <- setdiff(unique(ep$m), "prever")
ef <- rbindlist(lapply(alvos, function(k) {
  d <- ep[m == k]
  data.table(
    modelo = k,
    var = median(d$score) / median(ref$score) - 1,
    p   = suppressWarnings(wilcox.test(d$score, ref$score)$p.value))
}))
# p >= 0,05 nao demonstra ausencia de efeito, so' falta de deteccao
ef[, sig := ifelse(p < 0.05, "p < 0,05", "p >= 0,05")]
# nomes de experimento nao dizem nada ao leitor
NOMES <- c(base = "sem previsão", i6_longo = "treino longo",
           i4_pot = "potencial", i2_nov = "novidade",
           i5_prog = "previsão + progresso", i3_bolas = "currículo de bolas")
ef[, modelo := NOMES[as.character(modelo)]]
ef[, modelo := factor(modelo, levels = ef[order(var)]$modelo)]

g <- ggplot(ef, aes(var, modelo, colour = sig)) +
  geom_vline(xintercept = 0, colour = TINTA, linewidth = .4) +
  geom_segment(aes(x = 0, xend = var, yend = modelo), linewidth = .7) +
  geom_point(size = 2.6) +
  scale_x_continuous(labels = label_percent(),
                     expand = expansion(mult = c(.1, .12))) +
  scale_colour_manual(values = c("p < 0,05" = APOIO, "p >= 0,05" = NEUTRO)) +
  labs(x = "variação do score mediano contra o controle", y = NULL,
       title = "Nenhum tratamento superou o controle",
       subtitle = "cinco tratamentos e o base, comparados ao controle; 10 episódios cada") +
  tema_artigo() +
  theme(panel.grid.major.x = element_line(colour = "#e3e6e9", linewidth = .35))
salvar(g, file.path(DEST, "eda_efeitos.png"), "pagina", altura = 6.0)

# --- 7. painel dos agentes: score e duracao lado a lado ----------------------
ordem <- ep[, .(s = median(score)), by = m][order(-s)]$m
ep[, mo := factor(m, levels = ordem)]
p1 <- ggplot(ep, aes(mo, score)) +
  geom_boxplot(fill = "#dfe5eb", colour = DESTAQUE, linewidth = .4,
               outlier.size = .8, width = .6) +
  scale_y_log10(labels = label_number(scale_cut = cut_short_scale())) +
  labs(x = NULL, y = "score (log)", title = "Score por episódio") +
  tema_artigo() + grade_y() +
  theme(axis.text.x = element_text(angle = 30, hjust = 1))
p2 <- ggplot(ep, aes(mo, duracao_s)) +
  geom_boxplot(fill = "#e9e2dd", colour = APOIO, linewidth = .4,
               outlier.size = .8, width = .6) +
  labs(x = NULL, y = "duração (s)", title = "Tempo de partida") +
  tema_artigo() + grade_y() +
  theme(axis.text.x = element_text(angle = 30, hjust = 1))
salvar(p1 | p2, file.path(DEST, "eda_flip_painel.png"), "pagina", altura = 7.4)

# A saliencia por canal NAO e regerada aqui: os valores por canal foram
# medidos uma vez pelo script de saliencia e nao estao neste CSV. Uma versao
# anterior deste arquivo reconstruia o grafico a partir dos agregados do
# texto, o que equivalia a inventar os valores individuais. A figura
# original fica em analise/saliencia.png.
