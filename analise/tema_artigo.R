# Tema academico para as figuras do artigo.
#
# Segue a convencao de publicacao (referencia: mintandkiwi/academic-plot):
# ticks para dentro nos quatro lados, sem grade de fundo, legenda sem moldura,
# fios finos. O padrao do ggplot2 (fundo cinza, grade branca) denuncia
# "grafico de tutorial" e nao combina com texto em Libertine.

library(ggplot2)
library(grid)

TINTA     <- "#1a1a1a"
DESTAQUE  <- "#1f3a5f"   # o mesmo azul dos titulos do artigo
APOIO     <- "#a33b2a"
NEUTRO    <- "#8a949c"
PALETA    <- c(DESTAQUE, APOIO, "#4c7a34", "#7d5ba6", "#b8862b", NEUTRO)

tema_artigo <- function(base = 9) {
  theme_minimal(base_size = base, base_family = "serif") +
    theme(
      text             = element_text(colour = TINTA),
      plot.title       = element_text(face = "bold", size = base + 1.5,
                                      margin = margin(b = 2)),
      plot.subtitle    = element_text(colour = NEUTRO, size = base - 0.5,
                                      margin = margin(b = 6)),
      plot.caption     = element_text(colour = NEUTRO, size = base - 1.5),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      panel.background = element_blank(),
      plot.background  = element_rect(fill = "white", colour = NA),
      # a moldura fechada e os ticks para dentro sao a marca do estilo
      panel.border     = element_rect(colour = TINTA, fill = NA, linewidth = .5),
      axis.ticks       = element_line(colour = TINTA, linewidth = .4),
      axis.ticks.length = unit(-3, "pt"),          # negativo = para dentro
      axis.text        = element_text(colour = TINTA, size = base - 1),
      axis.text.x      = element_text(margin = margin(t = 6)),
      axis.text.y      = element_text(margin = margin(r = 6)),
      axis.title       = element_text(size = base),
      legend.position  = "bottom",
      legend.key       = element_blank(),
      legend.title     = element_blank(),
      legend.margin    = margin(t = -4),
      strip.background = element_blank(),
      strip.text       = element_text(face = "bold", size = base - 0.5,
                                      margin = margin(b = 4)),
      plot.margin      = margin(6, 8, 4, 6)
    )
}

# grade leve so' onde ela ajuda a ler valor (graficos de barra/linha longos)
grade_y <- function() {
  theme(panel.grid.major.y = element_line(colour = "#e3e6e9", linewidth = .35))
}

escala_cor  <- function(...) scale_colour_manual(values = PALETA, ...)
escala_fill <- function(...) scale_fill_manual(values = PALETA, ...)

# salva no tamanho da coluna (8,5 cm) ou da pagina inteira (17,2 cm)
salvar <- function(g, arq, largura = c("coluna", "pagina"), altura = NULL) {
  largura <- match.arg(largura)
  w <- if (largura == "coluna") 8.5 else 17.2
  h <- if (is.null(altura)) w * 0.62 else altura
  ggsave(arq, g, width = w, height = h, units = "cm", dpi = 300, bg = "white")
  message(sprintf("  %s  %.1f x %.1f cm", arq, w, h))
}
