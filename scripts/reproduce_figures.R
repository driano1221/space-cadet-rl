# Regenera as figuras do artigo a partir dos dados versionados em data/paper/.
#
# Os scripts de analise leem de analise/ e analise/dados/, que sao diretorios de
# trabalho ignorados pelo git. Este script materializa os dados publicados
# naqueles caminhos antes de rodar, para que um clone limpo funcione.
#
# A saliencia por canal nao e' regenerada: os valores por canal nao estao nos
# CSVs publicados, e reconstrui-los dos agregados seria inventa-los. A imagem
# original fica versionada em artigo/img/saliencia_grade.png.

# raiz do repo: --file= quando chamado por Rscript, ofile quando por source().
# sys.frame() sozinho quebra no Rscript, que e' como o README manda rodar.
args <- commandArgs(trailingOnly = FALSE)
arq <- sub("^--file=", "", grep("^--file=", args, value = TRUE))
raiz <- if (length(arq)) {
  normalizePath(file.path(dirname(arq), ".."))
} else {
  normalizePath(".")
}
if (!dir.exists(file.path(raiz, "analise"))) raiz <- normalizePath(".")
if (!dir.exists(file.path(raiz, "analise"))) {
  stop("rode a partir da raiz do repositorio")
}

pacotes <- c("data.table", "ggplot2", "patchwork", "scales", "png",
             "jsonlite", "ggrepel", "tidyverse")
faltando <- pacotes[!pacotes %in% rownames(installed.packages())]
if (length(faltando)) {
  stop("pacotes R ausentes: ", paste(faltando, collapse = ", "),
       "\nrode: Rscript analise/install_packages.R")
}

origem <- file.path(raiz, "data", "paper")
destino <- file.path(raiz, "analise")
dir.create(file.path(destino, "dados"), showWarnings = FALSE, recursive = TRUE)

# cada script espera o arquivo num diretorio especifico: os dumps de medicao em
# analise/dados/, os dados de avaliacao direto em analise/
em_dados <- c("reacao.csv", "rank_medido.csv", "baseline_1000_aleatoria.csv",
              "py_prob_030.csv", "eda_aleatoria.csv", "eda_heuristica.csv")
gz <- "[.]gz$"

for (f in list.files(origem, full.names = TRUE)) {
  nome <- basename(f)
  nome_final <- sub(gz, "", nome)
  alvo_dir <- if (nome_final %in% em_dados) {
    file.path(destino, "dados")
  } else {
    destino
  }
  alvo <- file.path(alvo_dir, nome_final)
  # sempre sobrescreve: data/paper/ e' a fonte canonica, e uma copia de trabalho
  # mais antiga em analise/ nao pode vencer a publicada
  if (grepl(gz, nome)) {
    cat("descomprimindo", nome, "\n")
    data.table::fwrite(data.table::fread(f), alvo)
  } else {
    file.copy(f, alvo, overwrite = TRUE)
  }
}

setwd(destino)
scripts <- c("figuras_artigo.R", "mapa_mesa.R", "mesa_tacadas_claro.R",
             "eda_flip.R")
falhas <- character()
for (s in scripts) {
  if (!file.exists(s)) next
  cat("\n=== ", s, " ===\n", sep = "")
  tryCatch(source(s), error = function(e) {
    cat("  FALHOU:", conditionMessage(e), "\n")
    falhas <<- c(falhas, s)
  })
}

cat("\n")
if (length(falhas)) {
  # sem isto o processo termina com codigo 0 mesmo tendo falhado, e quem roda
  # acha que reproduziu tudo
  stop(length(falhas), " script(s) falharam: ", paste(falhas, collapse = ", "))
}
cat("todas as figuras regeneradas em artigo/img/\n")
