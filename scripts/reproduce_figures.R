# Regenerate every figure used in the paper.
#
#     Rscript scripts/reproduce_figures.R
#
# Reads the raw evaluation data in analise/ and writes to artigo/img/.
# No training required: the CSVs of the runs are in the repository.
setwd(file.path(dirname(sys.frame(1)$ofile), "..", "analise"))

fontes <- c("figuras_artigo.R",        # reaction curve, baseline, cliff, rank
            "mapa_mesa.R",             # ball density per policy
            "mesa_tacadas_claro.R")    # presses vs strikes over the table

for (f in fontes) {
  if (file.exists(f)) {
    message("running ", f)
    source(f, local = new.env())
  } else {
    warning("missing: ", f)
  }
}
message("figures written to artigo/img/")
