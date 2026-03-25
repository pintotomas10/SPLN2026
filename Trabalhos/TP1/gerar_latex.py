import sys
import os
import json

if len(sys.argv) < 3:
    print("Uso: python gerar_latex.py <ficheiro_top3_json> <ficheiro_ner_txt>")
    sys.exit(1)

ficheiro_top3 = sys.argv[1]
ficheiro_ner = sys.argv[2]
nome_base = os.path.splitext(os.path.basename(ficheiro_top3))[0]

pasta_saida = "latex"
os.makedirs(pasta_saida, exist_ok=True)
ficheiro_saida_tex = os.path.join(pasta_saida, f"{nome_base}.tex")

print(f"\nA montar o documento LaTeX para '{nome_base}'...")

with open(ficheiro_top3, 'r', encoding='utf-8') as f:
    top_3_frases = json.load(f)

with open(ficheiro_ner, 'r', encoding='utf-8') as f:
    texto_anotado = f.read()

latex_template = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[portuguese]{{babel}}
\\usepackage{{hyperref}}

\\title{{{nome_base.replace('_', ' ').title()}}}
\\author{{Tomás Pinto - Scripting no Processamento de Linguagem Natural}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
Com base no modelo de n-grams desenvolvido e no método de scoring aplicado, as três frases selecionadas do texto são:
\\begin{{itemize}}
    \\item {top_3_frases[0] if len(top_3_frases) > 0 else "N/A"}
    \\item {top_3_frases[1] if len(top_3_frases) > 1 else "N/A"}
    \\item {top_3_frases[2] if len(top_3_frases) > 2 else "N/A"}
\\end{{itemize}}
\\end{{abstract}}

\\section{{Texto Original com Entidades (NER)}}
{texto_anotado}

\\vspace{{1cm}}
\\begin{{thebibliography}}{{9}}
\\bibitem{{{nome_base}}}
    Fonte analisada: \\texttt{{{nome_base.replace('_', '\\_')}}}. Texto processado automaticamente.
\\end{{thebibliography}}

\\end{{document}}
"""

with open(ficheiro_saida_tex, 'w', encoding='utf-8') as f:
    f.write(latex_template)

print(f"SUCESSO! O ficheiro LaTeX foi guardado em: {ficheiro_saida_tex}")