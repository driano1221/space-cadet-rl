#!/bin/sh
# 3 processos, cada um rodando 10 partidas SEQUENCIAIS sem teto.
# A diversidade vem da sequencia dentro do processo (o gerador aleatorio do jogo
# avanca a cada partida); processos novos sempre comecam do mesmo estado, entao
# paralelizar ambientes no mesmo lote nao funciona.
for i in 1 2 3; do
    python sem_teto.py ppo_c9_base 10 > lote_base_$i.log 2>&1 &
done
wait
echo "lotes do base prontos"
