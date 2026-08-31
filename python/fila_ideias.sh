#!/bin/bash
# As 5 ideias, em sequencia para nao brigarem por CPU.
# argumentos: passos tag n_envs recompensa prog alvo mult medal custo acerto prever pot nov bolas
cd "C:/Users/drian/Games/pinball_rl/python"
L="C:/Users/drian/Games/pinball_rl/analise"

# IDEIA 5 - previsao + peso em progresso (as duas que mais chegaram perto)
python treinar_visao_par.py 2500000 c9_i5_prog 6 score 1.0 0 0 0 0 0 prever 0 0 0 > "$L/i5_prog.log" 2>&1
# IDEIA 4 - shaping por potencial (telescopico, rank/9)
python treinar_visao_par.py 2500000 c9_i4_pot 6 score 0 0 0 0 0 0 prever 10 0 0 > "$L/i4_pot.log" 2>&1
# IDEIA 2 - bonus de novidade em (rank, multiplicador)
python treinar_visao_par.py 2500000 c9_i2_nov 6 score 0 0 0 0 0 0 prever 0 0.05 0 > "$L/i2_nov.log" 2>&1
# IDEIA 3 - curriculo de bolas (6 em vez de 3)
python treinar_visao_par.py 2500000 c9_i3_bolas 6 score 0 0 0 0 0 0 prever 0 0 6 > "$L/i3_bolas.log" 2>&1
# IDEIA 6 - treino longo com previsao (a escala saturou ANTES das features)
python treinar_visao_par.py 7500000 c9_i6_longo 6 score 0 0 0 0 0 0 prever 0 0 0 > "$L/i6_longo.log" 2>&1
echo "FILA CONCLUIDA"
