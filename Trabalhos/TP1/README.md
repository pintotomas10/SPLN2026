# Resumo do Projeto (Passo a Passo)

1. Extração de texto das fontes online
   - Foi extraído texto limpo de um artigo Magazine HD, ignorando anúncios e vídeos (fontes/eurovisao_napa_2025.txt).
   - Foi extraído texto limpo de várias páginas da Wikipédia sobre o Festival Eurovisão da Canção, navegando automaticamente entre anos (fontes/eurovisao_todos.txt).

2. Converção do PDF para XML
   - `pdftohtml -xml -f 11 -l 78 content.pdf`
   - O PDF original foi transformado em XML para facilitar a extração de texto.

3. Extração do texto limpo do XML
   - Foram removidos números de página, figuras, mapas, notas de rodapé e as frases foram juntadas.
   - O resultado ficou em fontes/content.txt.

4. Tokenização e criação de modelos de 2-gramas
   - As frases foram tokenizadas, as palavras filtradas, os bigramas gerados e as frequências contadas.
   - As frases tokenizadas e os modelos de n-gramas foram guardados.

5. Scoring das frases com base nos 2-gramas
   - O score das frases foi calculado usando os bigramas e foram selecionadas as 3 melhores frases de cada texto.
   - As top 3 frases foram guardadas.

6. Reconhecimento de entidades (NER)
   - As entidades (PER, LOC, ORG, MISC) foram identificadas com spaCy e marcadas no texto para LaTeX.
   - Os textos anotados foram guardados.

7. Geração dos documentos LaTeX
   - As 3 frases selecionadas e o texto anotado com entidades foram reunidos num documento LaTeX.
   - Os ficheiros ficaram prontos para compilar.

---

## webtoptxt_wiki.py
Gera: fontes/eurovisao_todos.txt
- Extrai texto limpo de várias páginas da Wikipédia sobre o Festival Eurovisão da Canção.
- Executa: python webtoptxt_wiki.py

## webtotxt_magazine.py
Gera: fontes/eurovisao_napa_2025.txt
- Extrai texto limpo de um artigo Magazine HD.
- Executa: python webtotxt_magazine.py

## xmltotxt.py
Gera: fontes/content.txt
- Script para converter o ficheiro XML exportado do PDF para texto limpo.
- Executa: python xmltotxt.py

## tokenizer.py
Gera: frases tokenizadas e modelos de n-gramas em fontes_tokenizadas/ e fontes_ngramas
- python tokenizer.py fontes/eurovisao_napa_2025.txt
- python tokenizer.py fontes/eurovisao_todos.txt
- python tokenizer.py fontes/content.txt

## scorer.py
- python scorer.py fontes/eurovisao_todos.txt fontes_ngramas/eurovisao_todos.json
```
TOP 3 Frases para: eurovisao_todos.txt
--------------------------------------------------
1. [Score: 117.82] Também todos os países de leste e a Tunísia transmitiram o festival.

2. [Score: 88.93] O país vencedor do festival foi a Suécia, com a canção "Euphoria" interpretada por Loreen.

3. [Score: 85.25] Esta foi a primeira vez que o concurso foi realizado na Irlanda .
```

- python scorer.py fontes/eurovisao_napa_2025.txt fontes_ngramas/eurovisao_napa_2025.json
```
TOP 3 Frases para: eurovisao_napa_2025.txt
--------------------------------------------------
1. [Score: 1.36] E o mais bonito tem sido o que acontece longe das câmaras, ou seja, conversas reais sobre música, países, histórias de vida.

2. [Score: 1.31] Nascidos numa cave na ilha da Madeira, os NAPA formaram-se entre amigos que partilhavam a paixão pela música.

3. [Score: 1.29] Numa conversa descontraída, entre gargalhadas cúmplices e reflexões honestas, os NAPA abriram o coração sobre a reação intensa que se seguiu à vitória no Festival da Canção — “foi duro, mas sabíamos ao que vínhamos”, admitem.
```

- python scorer.py fontes/content.txt fontes_ngramas/content.json
```
TOP 3 Frases para: content.txt
--------------------------------------------------
1. [Score: 8.89] As  opiniões  sobre  o  FEC  podem,  assim,  mudar  consoante  o  indivíduo  e  a comunidade em  que  este se  insere.     

2. [Score: 8.88] Mas não só os conflitos contribuem para a alteração das fronteiras dos países que compõem o continente europeu.

3. [Score: 8.78] Apesar de menos comum, é possível encontrarmos este mesmo feito, em 1997, com a Grécia e a Turquia.
```

## ner.py
Gera: textos anotados com entidades em fontes_anotadas
- python ner.py fontes/eurovisao_todos.txt
- python ner.py fontes/eurovisao_napa_2025.txt
- python ner.py fontes/content.txt


## gerar_latex.py
Gera: ficheiros LaTeX em latex
- python gerar_latex.py fontes_top3\eurovisao_todos.json fontes_anotadas\eurovisao_todos_ner.txt
- python gerar_latex.py fontes_top3\eurovisao_napa_2025.json fontes_anotadas\eurovisao_napa_2025_ner.txt
- python gerar_latex.py fontes_top3\content.json fontes_anotadas\content_ner.txt

## pdflatex
Gera: pdf do ficheiro latex
- pdflatex eurovisao_todos.tex 
- pdflatex eurovisao_napa_2025.tex
- pdflatex content.tex