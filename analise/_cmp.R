suppressMessages(library(tidyverse))
ep <- read_csv("eda_episodios.csv", show_col_types = FALSE) |>
  mutate(m = str_remove(modelo, "^ppo_c9_"))
ref <- ep |> filter(m == "prever")
saida <- ep |> filter(m != "prever") |> group_by(m) |> group_modify(~ tibble(
  score = median(.x$score),
  var   = sprintf("%+.0f%%", 100 * (median(.x$score) / median(ref$score) - 1)),
  p_sc  = round(wilcox.test(.x$score, ref$score)$p.value, 3),
  dur   = round(median(.x$duracao_s)),
  p_dur = round(wilcox.test(.x$duracao_s, ref$duracao_s)$p.value, 3),
  pont  = sprintf("%.1f%%", 100 * mean(.x$acerto_por_acionamento)),
  p_pt  = round(wilcox.test(.x$acerto_por_acionamento, ref$acerto_por_acionamento)$p.value, 3)
)) |> arrange(desc(score))
print(as.data.frame(saida), row.names = FALSE)
cat("\nCONTROLE prever: score", format(median(ref$score), big.mark = ","),
    "| dur", round(median(ref$duracao_s)), "s | pontaria",
    sprintf("%.1f%%", 100 * mean(ref$acerto_por_acionamento)), "\n")
