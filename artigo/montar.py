"""Monta o PDF a partir dos capitulos em core/*.md.

Pipeline: pandoc (com --citeproc para a bibliografia) gera o .tex a partir dos
capitulos em Markdown, e o pdflatex do MiKTeX compila. O pandoc vem do pacote
pypandoc_binary, entao nao precisa de instalacao separada no sistema.

Uso: python montar.py
"""
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(AQUI, "core")
SAIDA = os.path.join(AQUI, "saida")
MIKTEX = r"C:\Users\drian\AppData\Local\Programs\MiKTeX\miktex\bin\x64"

RESUMO = (
    "Relato de quinze passos de experimento treinando um agente de aprendizado "
    "por reforço no 3D Pinball Space Cadet do Windows XP, sobre a decompilação "
    "em C++ do jogo instrumentada para expor o estado interno da física. O "
    "agente alcança 2,6 milhões de pontos, 4,3 vezes uma política aleatória, "
    "mas com 250 ms de latência de ação, na faixa usada como referência "
    "humana, cai para 0,62 vezes o acaso: a vantagem é reflexo, não estratégia. "
    "Mais de dez intervenções distintas falharam em mover o teto, e a ordem por "
    "pontuação mostrou-se idêntica à ordem por tempo de sobrevivência em todas."
)


def pandoc():
    import pypandoc
    return pypandoc.get_pandoc_path()


def ajustar_tex(caminho):
    """Duas correcoes que o pandoc nao faz sozinho.

    1. longtable nao existe em modo duas colunas ("longtable not in 1-column
       mode"), e o writer LaTeX do pandoc usa longtable para toda pipe table.
       Vira tabular, com resizebox para nao estourar a largura da coluna.
    2. tipografia unicode que o inputenc nao conhece.
    """
    import re
    s = io_ler(caminho)

    def troca(m):
        """Remonta a tabela: o longtable do pandoc espalha cabecalho e corpo
        entre \\endfirsthead/\\endhead/\\endlastfoot, e apagar so' os comandos
        deixa \\bottomrule antes do corpo e chaves orfas."""
        bruto = m.group(2)
        # o cabecalho fica entre o primeiro \toprule e o primeiro \midrule
        cab = re.search(r"\\toprule[^\n]*\n(.*?)\\midrule", bruto, re.S)
        cabecalho = cab.group(1).strip() if cab else ""
        # o corpo comeca depois da ultima marca de estrutura
        corte = max(bruto.rfind(r"\endlastfoot"), bruto.rfind(r"\endhead"),
                    bruto.rfind(r"\endfirsthead"))
        corpo = bruto[corte:] if corte > 0 else bruto
        corpo = re.sub(r"^\\end(lastfoot|head|firsthead)", "", corpo)
        for lixo in (r"\endhead", r"\endfirsthead", r"\endfoot", r"\endlastfoot",
                     r"\noalign{}", r"\toprule", r"\midrule", r"\bottomrule"):
            corpo = corpo.replace(lixo, "")
            cabecalho = cabecalho.replace(lixo, "")
        corpo = re.sub(r"\\caption\{[^}]*\}\\tabularnewline", "", corpo)
        corpo = "\n".join(l for l in corpo.split("\n") if l.strip())
        cabecalho = "\n".join(l for l in cabecalho.split("\n") if l.strip())
        # as colunas do pandoc vem como >{\raggedright...}p{...}: viram l
        n = max(1, m.group(1).count("p{") or m.group(1).count("l")
                or len(re.findall(r"[lcr]", m.group(1))))
        # tabela fechada: fio externo, colunas separadas por linha vertical e
        # cabecalho com fundo. O padrao do booktabs (so' fios horizontais) e'
        # bonito em artigo academico mas ficou apagado demais neste layout.
        cols = "|" + "l|" * n
        cab = ("\\rowcolor{fundotab}\n" + cabecalho + "\n\\hline\n"
               if cabecalho else "")
        # O pandoc quebra linha longa em varias linhas de texto. Agrupar por
        # quebra de texto e inserir \hline entre elas partia a linha da tabela
        # ao meio, e o LaTeX passava a imprimir lixo ("height") no lugar da
        # celula. O fim real de uma linha de tabela e' o "\\".
        bruto_l = [l.strip() for l in corpo.split("\n") if l.strip()]
        linhas, atual = [], []
        for l in bruto_l:
            atual.append(l)
            if l.rstrip().endswith(r"\\"):
                linhas.append(" ".join(atual))
                atual = []
        if atual:
            linhas.append(" ".join(atual))
        corpo_h = "\n\\hline\n".join(linhas)
        return ("\\vspace{0.2em}\n\\begin{center}\\small\n"
                "\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi}{!}{%\n"
                "\\begin{tabular}{" + cols + "}\n\\hline\n" + cab +
                corpo_h + "\n\\hline\n\\end{tabular}}\n\\end{center}\n"
                "\\vspace{0.1em}\n")

    # O pandoc envolve cada tabela em "{\def\LTcaptype{none} ... }". Removido o
    # longtable, essa chave de abertura fica orfa e desbalanceia o arquivo
    # inteiro, o que aparece como "File ended while scanning use of \caption".
    s = re.sub(r"\{\\def\\LTcaptype\{none\}[^\n]*\n", "", s)
    s = re.sub(r"\\begin\{longtable\}\[\]\{@\{\}([^}]*)@\{\}\}(.*?)\\end\{longtable\}\s*\}",
               troca, s, flags=re.S)
    s = re.sub(r"\\begin\{longtable\}\[\]\{([^}]*)\}(.*?)\\end\{longtable\}\s*\}",
               troca, s, flags=re.S)
    s = re.sub(r"\\begin\{longtable\}\[\]\{([^}]*)\}(.*?)\\end\{longtable\}",
               troca, s, flags=re.S)

    for u, tex in (("\u2212", "--"), ("\u00d7", r"$\times$"),
                   ("\u2248", r"$\approx$"), ("\u2192", r"$\rightarrow$"),
                   ("\u2265", r"$\geq$"), ("\u2264", r"$\leq$")):
        s = s.replace(u, tex)

    io_gravar(caminho, s)


def io_ler(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def io_gravar(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    # as imagens precisam estar ao lado do .tex para o pdflatex acha-las
    destino_img = os.path.join(SAIDA, "img")
    if os.path.isdir(destino_img):
        shutil.rmtree(destino_img)
    shutil.copytree(os.path.join(AQUI, "img"), destino_img)

    caps = [os.path.join(CORE, f) for f in sorted(os.listdir(CORE))
            if f.endswith(".md")]
    assert caps, "nenhum capitulo em core/"

    tex = os.path.join(SAIDA, "artigo.tex")
    cmd = [pandoc(), *caps,
           "--from", "markdown+tex_math_dollars+pipe_tables+footnotes",
           "--to", "latex",
           "--template", os.path.join(AQUI, "controls", "modelo.latex"),
           "--citeproc",
           "--bibliography", os.path.join(AQUI, "bib", "referencias.bib"),
           "--csl", os.path.join(AQUI, "csl", "abnt.csl"),
           "--metadata", "title=Pinball, Paciência e um Viking",
           "--metadata", "subtitle=Como treinar um agente de aprendizado por "
                         "reforço no 3D Pinball me fez descobrir que eu estava "
                         "medindo a coisa errada",
           "--metadata", "author=Adriano Pires Cunha",
           "--metadata", "date=Agosto de 2026",
           "--metadata", f"abstract={RESUMO}",
           "--metadata", "lang=pt-BR",
           "--top-level-division=section",
           "-o", tex]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        print("pandoc falhou:")
        print(r.stderr[-1500:].encode("ascii", "replace").decode("ascii"))
        sys.exit(1)
    ajustar_tex(tex)
    print(f"{len(caps)} capitulos -> {os.path.relpath(tex, AQUI)}")

    # caminho absoluto: no Windows o subprocess nao resolve o PATH do shell
    exe = os.path.join(MIKTEX, "pdflatex.exe")
    assert os.path.exists(exe), f"pdflatex nao encontrado em {exe}"
    for passada in (1, 2):                     # duas passadas: refs e layout
        r = subprocess.run([exe, "-interaction=nonstopmode", "artigo.tex"],
                           cwd=SAIDA, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        pdf = os.path.join(SAIDA, "artigo.pdf")
        if not os.path.exists(pdf):
            erros = [l for l in r.stdout.split("\n") if l.startswith("!")][:4]
            print(f"pdflatex falhou (passada {passada}):")
            # o console do Windows e cp1252 e nao imprime o log cru
            msg = "\n".join(erros) or r.stdout[-800:]
            print(msg.encode("ascii", "replace").decode("ascii"))
            sys.exit(1)
    print(f"PDF: {os.path.relpath(pdf, AQUI)} ({os.path.getsize(pdf)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
