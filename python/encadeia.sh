#!/bin/sh
# Espera o treino de medal terminar e ja' dispara os dois testes sem teto.
while ! grep -q "^salvo" treino_medal.log 2>/dev/null; do
    if ! tasklist //FI "IMAGENAME eq python.exe" 2>/dev/null | grep -q python; then
        echo "TREINO MORREU"; tail -3 treino_medal.log; exit 1
    fi
    sleep 60
done
echo "treino terminou; rodando teste sem teto"
python sem_teto.py ppo_medal 6 > semteto_medal.log 2>&1
echo "medal sem teto pronto"
python sem_teto.py ppo_c9_base 6 > semteto_base.log 2>&1
echo "base sem teto pronto"
