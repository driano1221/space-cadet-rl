# Pacotes R usados pelas figuras e pela analise.
pacotes <- c("data.table", "ggplot2", "patchwork", "scales", "png",
             "jsonlite", "ggrepel", "dplyr", "tidyr")
faltando <- pacotes[!pacotes %in% rownames(installed.packages())]
if (length(faltando)) {
  install.packages(faltando, repos = "https://cloud.r-project.org")
} else {
  cat("todos os pacotes ja instalados\n")
}
