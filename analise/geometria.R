# A critica do Adriano a' area: alta demais em cima, estreita demais na largura,
# e a bola que desce pela lateral entraria so' na metade do flipper.
# Aqui os dados respondem, sem retangulo imposto.
library(tidyverse)
library(png); library(grid)

mesa <- readPNG("mesa_fundo.png"); H <- dim(mesa)[1]; W <- dim(mesa)[2]
tac <- read_csv("tacadas_tela.csv", show_col_types = FALSE) |>
  mutate(y_plot = H - tela_y,
         lado = factor(lado, c("esq", "dir"), c("flipper esquerdo", "flipper direito")))
so_tac <- filter(tac, acertou == 1)

cat("=== extensao real das tacadas (percentis) ===\n")
so_tac |>
  summarise(
    x_p1 = quantile(tela_x, .01), x_p50 = median(tela_x), x_p99 = quantile(tela_x, .99),
    largura = quantile(tela_x, .99) - quantile(tela_x, .01),
    y_p1 = quantile(y_plot, .01), y_p50 = median(y_plot), y_p99 = quantile(y_plot, .99),
    altura = quantile(y_plot, .99) - quantile(y_plot, .01),
    .by = lado) |> print(width = Inf)

cat("\n=== a area e' alta demais? distribuicao vertical das tacadas ===\n")
so_tac |>
  mutate(faixa = cut(y_plot, breaks = quantile(y_plot, seq(0, 1, .2)),
                     include.lowest = TRUE, labels = paste0("q", 1:5))) |>
  summarise(n = n(), y_min = min(y_plot), y_max = max(y_plot), .by = faixa) |>
  arrange(faixa) |> print()

cat("\n=== a bola que desce pela LATERAL aparece? ===\n")
# tacadas nos extremos de x: se existirem, a area estreita as cortaria
so_tac |>
  mutate(regiao = case_when(tela_x < quantile(so_tac$tela_x, .10) ~ "extremo esquerdo",
                            tela_x > quantile(so_tac$tela_x, .90) ~ "extremo direito",
                            TRUE ~ "centro")) |>
  summarise(n = n(), pct = scales::percent(n() / nrow(so_tac), .1),
            y_mediano = median(y_plot), .by = c(lado, regiao)) |>
  arrange(lado, regiao) |> print(n = Inf)

# contorno de densidade em vez de retangulo: mostra o FORMATO real
p <- ggplot(so_tac, aes(tela_x, y_plot)) +
  annotation_custom(rasterGrob(mesa, width = unit(1, "npc"), height = unit(1, "npc")),
                    xmin = 0, xmax = W, ymin = 0, ymax = H) +
  coord_fixed(xlim = c(90, 290), ylim = c(0, 130), expand = FALSE) +
  stat_density_2d(aes(fill = after_stat(level)), geom = "polygon",
                  alpha = .5, bins = 10) +
  geom_point(size = .7, alpha = .5, color = "#0b3d16") +
  scale_fill_gradient(low = "#a1d99b", high = "#00441b") +
  facet_wrap(~ lado) +
  labs(title = "Formato real da zona (ampliado na regiao dos flippers)",
       subtitle = "contorno de densidade das tacadas, sem retangulo imposto",
       x = NULL, y = NULL, fill = "densidade") +
  theme_minimal(base_size = 11) +
  theme(axis.text = element_blank(), panel.grid = element_blank())
ggsave("zona_formato.png", p, width = 11, height = 6, dpi = 130, bg = "white")
