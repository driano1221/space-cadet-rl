# EDA: por que a heuristica sobrevive 4x mais e pontua 24x menos?
suppressMessages({library(data.table); library(ggplot2); library(dplyr)})
dir <- "C:/Users/drian/Games/pinball_rl/analise/dados"

d <- rbindlist(list(
  fread(file.path(dir, "eda_aleatoria.csv"))[, pol := "Aleatoria"],
  fread(file.path(dir, "eda_heuristica.csv"))[, pol := "Heuristica"]))

cat("=== SCORE POR EPISODIO (metricas completas) ===\n")
ep <- d[, .(score = max(score), duracao = max(tempo_s)), by = .(pol, episodio)]
print(as.data.frame(ep[, .(n = .N, media = mean(score), dp = sd(score),
      min = min(score), q25 = quantile(score, .25), mediana = median(score),
      q75 = quantile(score, .75), max = max(score),
      cv = sd(score)/mean(score), duracao = mean(duracao)), by = pol]), digits = 5)

cat("\n=== MOVIMENTO DA BOLA ===\n")
print(as.data.frame(d[, .(
  vel_media = mean(speed), vel_mediana = median(speed), vel_dp = sd(speed),
  pct_quase_parada = 100 * mean(speed < 2),
  pct_lenta = 100 * mean(speed < 6),
  y_media = mean(y), y_dp = sd(y)), by = pol]), digits = 4)

cat("\n=== ONDE A BOLA FICA (y: negativo = topo da mesa, positivo = fundo) ===\n")
d[, zona := cut(y, breaks = c(-Inf, -6, 0, 6, Inf),
                labels = c("topo (alvos)", "meio-alto", "meio-baixo", "fundo (flippers)"))]
print(as.data.frame(d[, .(pct = round(100 * .N / nrow(d[pol == .BY$pol]), 1)), by = .(pol, zona)] |>
        dcast(zona ~ pol, value.var = "pct")))

cat("\n=== PONTUACAO POR MINUTO DE JOGO ===\n")
print(as.data.frame(ep[, .(pontos_por_min = round(mean(score / (duracao/60)))), by = pol]))

cat("\n=== ACOES ===\n")
print(as.data.frame(d[, .(pct_esq = round(100*mean(acao_esq), 1),
                          pct_dir = round(100*mean(acao_dir), 1),
                          pct_ambos = round(100*mean(acao_esq & acao_dir), 1),
                          pct_nenhum = round(100*mean(!acao_esq & !acao_dir), 1)), by = pol]))
