# Regenera as figuras do artigo a partir dos dados versionados em data/paper/.
#
# Os scripts de analise leem de analise/ e analise/dados/, que sao diretorios de
# trabalho ignorados pelo git. Este script materializa os dados publicados
# naqueles caminhos antes de rodar, para que um clone limpo funcione.
raiz <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
if (!dir.exists(file.path(raiz, "analise"))) raiz <- normalizePath(".")

pacotes <- c("data.table", "ggplot2", "patchwork", "scales", "png",
              "jsonlite", "ggrepel", "dplyr", "tidyr")
faltando <- pacotes[!pacotes %in% rownames(installed.packages())]
if (length(faltando)) {
  stop("pacotes R ausentes: ", paste(faltando, collapse = ", "),
       "\nrode: Rscript analise/install_packages.R")
}

origem <- file.path(raiz, "data", "paper")
destino <- file.path(raiz, "analise")
dir.create(file.path(destino, "dados"), showWarnings = FALSE, recursive = TRUE)

for (f in list.files(origem, full.names = TRUE)) {
  nome <- basename(f)
  # cada script espera o arquivo num diretorio especifico: os dumps de medicao
  # em analise/dados/, os dados de avaliacao direto em analise/
  em_dados <- c("reacao.csv", "rank_medido.csv", "baseline_1000_aleatoria.csv",
                "py_prob_030.csv", "eda_aleatoria.csv", "eda_heuristica.csv")
  alvo_dir <- if (sub("\.gz$", "", nome) %in% em_dados)
    file.path(destino, "dados") else destino
  if (grepl("\.gz$", nome)) {
    alvo <- file.path(alvo_dir, sub("\.gz$", "", nome))
    if (!file.exists(alvo)) {
      cat("descomprimindo", nome, "\n")
      dados <- data.table::fread(f)
      data.table::fwrite(dados, alvo)
    }
  } else {
    alvo <- file.path(alvo_dir, nome)
    if (!file.exists(alvo)) file.copy(f, alvo)
  }
}

setwd(destino)
scripts <- c("figuras_artigo.R", "mapa_mesa.R", "mesa_tacadas_claro.R", "eda_flip.R")
for (s in scripts) {
  if (file.exists(s)) {
    cat("\n=== ", s, " ===\n", sep = "")
    tryCatch(source(s), error = function(e) cat("  falhou:", conditionMessage(e), "\n"))
  }
}
cat("\nfiguras em artigo/img/\n")
