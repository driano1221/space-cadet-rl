# Para que lado cresce o y da fisica?
# tela_y e' coordenada de tela e cresce para BAIXO. A correlacao entre os dois
# diz se o y da fisica segue a mesma direcao.
suppressMessages(library(data.table))
d <- fread("dados/eda_aleatoria.csv", select = c("y", "tela_y", "x", "tela_x"))
r <- cor(d$y, d$tela_y)
cat("cor(y_fisica, tela_y) =", round(r, 3), "\n")
cat("cor(x_fisica, tela_x) =", round(cor(d$x, d$tela_x), 3), "\n")
cat(if (r > 0)
      "-> y da fisica cresce PARA BAIXO, igual a tela: o grafico precisa de scale_y_reverse\n"
    else
      "-> y da fisica cresce PARA CIMA: plotar direto esta correto\n")
