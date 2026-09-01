"""Ajusta afirmacoes que prometiam mais do que o experimento mostra.

Cada troca vem de um ponto levantado na revisao: latencia nao e' o mesmo que
tempo de reacao humano, o teste de historico nao prova Markov, a garantia de
Ng et al. nao implica empate, e um unico treino por tratamento nao autoriza
inferencia sobre o metodo em geral.
"""
import io
import os

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")


def troca(arq, pares):
    """Idempotente: uma troca ja aplicada e' pulada em vez de derrubar o script,
    porque uma execucao anterior pode ter falhado no meio da lista."""
    p = os.path.join(CORE, arq)
    s = io.open(p, encoding="utf-8").read()
    feitas = puladas = 0
    for a, b in pares:
        if s.count(a) == 1:
            s = s.replace(a, b)
            feitas += 1
        elif b in s:
            puladas += 1
        else:
            raise AssertionError(f"{arq}: ancora nao encontrada -> {a[:55]}")
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"  {arq}: {feitas} aplicadas, {puladas} ja estavam")


troca("07_reacao.md", [
    ("É o equivalente a dar a ele um tempo de reação humano.",
     "É uma aproximação simples de latência em escala humana. Não é simular uma\n"
     "pessoa: ele continua emitindo comandos a 40 Hz, só que deslocados no tempo."),
    ("Com tempo de reação humano, **meu agente joga pior que apertar botão ao acaso**.",
     "Com latência na faixa humana, **ele deixa de superar até a política aleatória**."),
    ("Com esse resultado, dá para dizer com alguma segurança que em\ncondições humanas de reação, o agente não competiria comigo. Nem com você.",
     "Como eu não cheguei a coletar uma linha de base\n"
     "humana, o que dá para afirmar é o que está medido: sob latência nessa faixa,\n"
     "o agente cai abaixo do acaso."),
])

troca("08_teto.md", [
    ("A intuição diz que o agente precisa lembrar\ndo passado para jogar bem. Testei empilhar quadros e medir quanto isso melhora a\nprevisão do estado seguinte. Ganho: 0,012 de AUC, e satura imediatamente.\n\nO estado do pinball é quase markoviano: posição e velocidade da bola contam\npraticamente toda a história. Passado não ajuda.",
     "A intuição diz que o agente precisa lembrar\n"
     "do passado para jogar bem. Testei empilhar quadros e medir quanto isso melhora\n"
     "uma tarefa auxiliar: prever o estado seguinte. A métrica é a AUC dessa\n"
     "previsão, e ela vai de 0,847 para 0,859 antes de saturar.\n\n"
     "Nesse teste, acrescentar histórico rendeu quase nada, o que sugere que posição\n"
     "e velocidade já carregam boa parte da informação relevante. Não é prova formal\n"
     "de que o estado é markoviano, mas indica que memória longa não é onde está o\n"
     "gargalo."),
])

troca("06_berco.md", [
    ("A diferença de **23 vezes** no score vem inteiramente do que cada um faz com o\nmesmo tempo de jogo. Sem variável de confusão, sem explicação alternativa. Duas\ninteligências idênticas, objetivos opostos, e uma delas passa a partida\nabraçada na bola.",
     "A diferença de **23 vezes** no score vem do que cada um faz com o mesmo tempo\n"
     "de jogo. A duração praticamente igual elimina a explicação mais óbvia para a\n"
     "diferença. Duas inteligências idênticas, objetivos opostos, e uma delas passa\n"
     "a partida abraçada na bola."),
])

troca("11_ultima_rodada.md", [
    ("**Shaping por potencial empatou** ($p = 0{,}17$), que é o comportamento esperado\nde um método cuja garantia é não alterar a estratégia ótima. Não havia o que\nacelerar.",
     "**Shaping por potencial não trouxe ganho mensurável** ($p = 0{,}17$). Vale notar\n"
     "que a garantia de Ng et al. é preservar a política ótima, não produzir empate:\n"
     "o método poderia perfeitamente ter acelerado a chegada a uma política melhor.\n"
     "Aqui não acelerou."),
])

# o 'so' do capitulo 9 ja' esta' correto no PDF (byte 0xf3 = o acudo); o que
# a revisao leu como 'so~' era ruido de renderizacao na tela

troca("04_rl.md", [
    ("Eu já tinha o básico de aprendizado por reforço, de estudar por conta por gostar\nda área: agente, ambiente, recompensa, a ideia geral de política. O suficiente\npara achar que sabia, e não o suficiente para prever onde ia me atrapalhar.",
     "Eu já tinha o básico de RL, de estudar por conta, por gostar da área: agente,\n"
     "ambiente, recompensa, a ideia geral de política. O suficiente para achar que\n"
     "sabia, e não o suficiente para prever onde ia me atrapalhar."),
])

print("suavizacoes aplicadas")
