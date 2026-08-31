# EDA dos tres agentes: base, custo por acionamento, recompensa por tacada.
# Pergunta central: premiar a TACADA ensinou a mirar, ou so' mudou o volume?

library(tidyverse)
library(patchwork)

ep <- read_csv("eda_episodios.csv", show_col_types = FALSE) |>
  mutate(modelo = fct_relevel(str_remove(modelo, "^ppo_c9_"),
                              "base", "prever", "i5_prog", "i4_pot",
                              "i2_nov", "i3_bolas", "i6_longo"))
ac <- read_csv("eda_acionamentos.csv", show_col_types = FALSE) |>
  mutate(modelo = fct_relevel(str_remove(modelo, "^ppo_c9_"),
                              "base", "prever", "i5_prog", "i4_pot",
                              "i2_nov", "i3_bolas", "i6_longo"))

# base e prever sao as referencias (cinza e azul); as cinco ideias em tons
# quentes, para separar visualmente referencia de tratamento
cores <- c(base = "#7f7f7f", prever = "#1f77b4",
           i5_prog = "#d62728", i4_pot = "#ff7f0e", i2_nov = "#9467bd",
           i3_bolas = "#8c564b", i6_longo = "#e377c2",
           custoflip = "#c49c94", acerto = "#2ca02c")

# 1. score: escala log, a cauda e' pesada demais para escala linear
p1 <- ep |>
  ggplot(aes(modelo, score, fill = modelo)) +
  geom_boxplot(alpha = .35, outlier.shape = NA, width = .55) +
  geom_jitter(aes(color = modelo), width = .12, size = 2.2, alpha = .85) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_fill_manual(values = cores) + scale_color_manual(values = cores) +
  labs(title = "Score por episodio", subtitle = "escala log; cada ponto e' uma partida",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "none")

# 2. o par que decide: volume de acionamento x pontaria
p2 <- ep |>
  ggplot(aes(acionamentos_s, acerto_por_acionamento, color = modelo)) +
  geom_point(size = 2.6, alpha = .85) +
  stat_summary(aes(group = modelo), fun = mean, geom = "point",
               shape = 4, size = 5, stroke = 1.3) +
  scale_y_continuous(labels = scales::label_percent()) +
  scale_color_manual(values = cores) +
  labs(title = "Volume x pontaria",
       subtitle = "x = quanto aperta | y = fracao que conecta (X = media)",
       x = "acionamentos por segundo", y = "acerto por acionamento", color = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "bottom")

# 3. tacadas por segundo: o alvo direto do treino
p3 <- ep |>
  ggplot(aes(modelo, tacadas_s, fill = modelo)) +
  geom_boxplot(alpha = .35, outlier.shape = NA, width = .55) +
  geom_jitter(aes(color = modelo), width = .12, size = 2.2, alpha = .85) +
  scale_fill_manual(values = cores) + scale_color_manual(values = cores) +
  labs(title = "Tacadas por segundo", subtitle = "flipper em movimento conectou com a bola",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "none")

# 4. tempo com o flipper erguido: onde o custoflip escapou
# "sempre ambos" durou 2h e fez 38 mil pontos; o base dura 6 min e faz 2,6M.
# O tempo em jogo e' o que converte em pontos, entao a duracao virou eixo.
p4b <- ep |>
  ggplot(aes(tempo_s, score, color = modelo)) +
  geom_point(size = 2.4, alpha = .85) +
  scale_y_log10(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  scale_color_manual(values = cores) +
  labs(title = "Duracao x score", subtitle = "cada ponto e' uma partida",
       x = "duracao (s)", y = NULL, color = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "bottom")
ggsave("eda_duracao_score.png", p4b, width = 8, height = 5.5, dpi = 140, bg = "white")

p4 <- ep |>
  ggplot(aes(modelo, flipper_ligado, fill = modelo)) +
  geom_boxplot(alpha = .35, outlier.shape = NA, width = .55) +
  geom_jitter(aes(color = modelo), width = .12, size = 2.2, alpha = .85) +
  scale_y_continuous(labels = scales::label_percent()) +
  scale_fill_manual(values = cores) + scale_color_manual(values = cores) +
  labs(title = "Tempo com flipper erguido",
       subtitle = "o escape que o custo por acionamento produziu", x = NULL, y = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "none")

((p1 | p3) / (p2 | p4)) +
  plot_annotation(title = "Premiar a tacada x punir o acionamento",
                  theme = theme(plot.title = element_text(face = "bold", size = 15)))
ggsave("eda_flip_painel.png", width = 12, height = 9, dpi = 150, bg = "white")

# 5. a nuvem que define a area util: onde a bola estava nas tacadas que
#    conectaram, medida no INICIO do movimento (inclui a antecipacao da pa')
p5 <- ac |>
  filter(acertou == 1) |>
  ggplot(aes(rel_x, rel_y)) +
  geom_point(data = \(d) filter(ac, acertou == 0) |> slice_sample(n = 4000),
             color = "grey82", size = .5, alpha = .5) +
  geom_point(aes(color = modelo), size = 1.5, alpha = .8) +
  scale_color_manual(values = cores) +
  facet_grid(lado ~ modelo) +
  labs(title = "Onde a bola estava quando a tacada conectou",
       subtitle = "cinza = acionamento que nao conectou | colorido = tacada real",
       x = "posicao relativa X", y = "posicao relativa Y", color = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "none")
ggsave("eda_zona_tacada.png", p5, width = 11, height = 7, dpi = 150, bg = "white")

# resumo numerico que acompanha os graficos
ep |>
  summarise(n = n(), score_mediano = median(score), tacadas_s = mean(tacadas_s),
            acionam_s = mean(acionamentos_s), pontaria = mean(acerto_por_acionamento),
            erguido = mean(flipper_ligado), .by = modelo) |>
  mutate(across(c(tacadas_s, acionam_s), \(x) round(x, 2)),
         across(c(pontaria, erguido), \(x) scales::percent(x, .1))) |>
  print(width = Inf)

# --- testes: cada tratamento contra o base, pareados por metrica ---------
# Mann-Whitney porque score tem cauda pesada (CV ~0,6) e n e' pequeno:
# a media e' instavel e o t-test assume normalidade que os dados nao tem.
testar <- function(dados, coluna) {
  base <- dados |> filter(modelo == "base") |> pull({{ coluna }})
  dados |>
    filter(modelo != "base") |>
    summarise(
      mediana_base = median(base),
      mediana = median({{ coluna }}),
      variacao = median({{ coluna }}) / median(base) - 1,
      p = suppressWarnings(wilcox.test({{ coluna }}, base)$p.value),
      .by = modelo
    ) |>
    mutate(metrica = rlang::as_label(rlang::enquo(coluna)), .before = 1)
}

testes <- bind_rows(
  testar(ep, score), testar(ep, tempo_s), testar(ep, tacadas_s),
  testar(ep, acionamentos_s),
  testar(ep, acerto_por_acionamento), testar(ep, flipper_ligado)
) |>
  mutate(variacao = scales::percent(variacao, .1), p = round(p, 4))
print(testes, n = Inf, width = Inf)
write_csv(testes, "eda_testes.csv")

# 6. o resumo visual da pergunta central, em uma figura so'
p6 <- testes |>
  filter(metrica %in% c("score", "tacadas_s", "acerto_por_acionamento")) |>
  mutate(efeito = as.numeric(str_remove(variacao, "%")),
         sig = if_else(p < .05, "p < 0,05", "nao significativo"),
         metrica = recode(metrica, score = "Score",
                          tacadas_s = "Tacadas/s",
                          acerto_por_acionamento = "Pontaria")) |>
  ggplot(aes(efeito, fct_rev(metrica), fill = modelo, alpha = sig)) +
  geom_col(position = position_dodge(.7), width = .62) +
  geom_vline(xintercept = 0, linewidth = .4) +
  scale_alpha_manual(values = c("p < 0,05" = 1, "nao significativo" = .35)) +
  scale_x_continuous(labels = scales::label_percent(scale = 1)) +
  scale_fill_manual(values = cores[c("custoflip", "acerto")]) +
  labs(title = "Efeito de cada tratamento sobre o agente base",
       subtitle = "barra clara = diferenca nao significativa",
       x = "variacao sobre o base", y = NULL, fill = NULL, alpha = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "bottom")
ggsave("eda_efeitos.png", p6, width = 9, height = 5, dpi = 150, bg = "white")
