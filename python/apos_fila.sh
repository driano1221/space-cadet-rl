#!/bin/bash
# Espera a fila das 5 ideias e roda o coletor pareado com os 7 agentes.
# Avaliacao interna do treinador (n=6, nao pareada) nao serve para comparar
# entre agentes - ja induziu leitura errada duas vezes.
cd "$(dirname "$0")"
L="../analise"
while true; do
  grep -q "FILA CONCLUIDA" "$L/fila.log" 2>/dev/null && break
  n=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*treinar_visao*' } | Measure-Object).Count" 2>/dev/null | tr -d '[:space:]')
  [ "$n" = "0" ] && { sleep 120; n2=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*treinar_visao*' } | Measure-Object).Count" 2>/dev/null | tr -d '[:space:]'); [ "$n2" = "0" ] && break; }
  sleep 120
done
echo "fila encerrada, coletando pareado"
python coletar_eda.py 10 ppo_c9_base ppo_c9_prever ppo_c9_i5_prog ppo_c9_i4_pot \
  ppo_c9_i2_nov ppo_c9_i3_bolas ppo_c9_i6_longo
echo "COLETA CONCLUIDA"
