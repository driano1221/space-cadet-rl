# Decisoes

## 2026-08-26

### Instrumentar a decompilacao em vez de capturar a tela

**Alternativa:** OpenCV + captura de tela, como o space-cadet-nn.
**Por que:** captura de tela fica presa ao tempo real (30 fps), estima
velocidade com erro, quebra se a janela mudar de lugar e nao da acesso a luzes
nem a missao ativa. Instrumentar da estado exato e velocidade ilimitada.
**Resultado:** 941x tempo real contra 1 partida/minuto do projeto de referencia.

### Nao criar um fork publico ainda

**Por que:** e' experimento. Publicar exige README, licenca, CI e suporte.
Decidir depois que houver agente treinado.

### Manter a instrumentacao em um unico commit numa branch propria

**Alternativa:** varios commits no master do clone.
**Por que:** o valor de portfolio esta no diff legivel - 159 linhas somadas a
uma decompilacao de 142 arquivos. Branch `rl-instrumentation`.

### Aplicar acoes via MainTable->Message(), nao via eventos SDL

**Por que:** `pb::InputDown` faz varias checagens (pausa, single_step, demo) e
passa pelo mapeamento de teclado configuravel. Chamar `Message` direto e' uma
linha e nao depende de configuracao do usuario.

### Incluir politicas degeneradas como controle

**Por que:** foi o unico teste capaz de provar que o input realmente chega ao
jogo. Sem ele, um bug silencioso de input produziria dados que parecem bons.
**Resultado:** medianas de 147k / 402k / 16k para nunca aperta / aleatoria /
sempre apertado. Distribuicoes claramente diferentes.

### Usar escala log em toda comparacao de score

**Por que:** Shapiro-Wilk no score bruto da p < 2,2e-16. Em log, p = 0,001.
Ainda rejeita normalidade, mas melhora ~13 ordens de magnitude. Media
aritmetica de score aqui e' estatistica enganosa.

### Exportar tambem a coordenada de tela

**Alternativa:** mapear as coordenadas fisicas para pixels na analise.
**Por que:** a projecao do jogo e' perspectiva 3D, com matriz documentada em
`proj.cpp`. Mapeamento linear nao alinha. Pedir ao jogo via `proj::xform_to_2d`
resolve exatamente e ainda entrega uma observacao util para visao computacional.

### Varrer a probabilidade de apertar em vez de so' comparar politicas fixas

**Por que:** com tres pontos (0%, 50%, 100%) nao da' para saber se o score cai
de forma suave ou tem um pico. A varredura mostrou pico em 30% e colapso apenas
no extremo 100%, o que muda a leitura do problema.

### Thread + handshake em vez de refatorar o winmain

**Alternativa:** extrair a inicializacao de `winmain::WinMain` em funcoes.
**Por que:** a inicializacao tem ~200 linhas com variaveis locais usadas no
cleanup e um `do/while(restart)` em volta. Extrair era arriscado e mexeria em
codigo do upstream. Rodar o jogo em uma thread e conversar por
mutex + condition_variable reaproveita a inicializacao testada inteira, e o
gancho ja existia (`rlmode::ParseAndRun`, entre init e cleanup).
**Custo:** ~20 us por chamada, irrelevante perto do custo da rede neural.

### Comprimir a recompensa com raiz quadrada

**Por que:** o ganho de score e' esparso (97,3% dos passos valem zero) e tem
cauda pesada (picos de 20 contra desvio de 0,73). Com a recompensa crua, o PPO
colapsou para "nunca apertar" - 100% das acoes deterministicas - e ficou 2,4x
PIOR que o aleatorio. A raiz comprime a cauda; `VecNormalize` cuida da escala.
