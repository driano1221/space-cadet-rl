# Pacotes R usados pelas figuras e pela analise.
# tidyverse porque eda_flip.R faz library(tidyverse); ele ja traz dplyr,
# tidyr, readr e forcats
pacotes <- c("data.table", "ggplot2", "patchwork", "scales", "png",
             "jsonlite", "ggrepel", "tidyverse")
faltando <- pacotes[!pacotes %in% rownames(installed.packages())]
if (length(faltando)) {
  install.packages(faltando, repos = "https://cloud.r-project.org")
} else {
  cat("todos os pacotes ja instalados\n")
}
