import sys
import os
import spacy
import re 

if len(sys.argv) < 2:
    print("Uso: python ner.py <ficheiro_original_txt>")
    sys.exit(1)

ficheiro_texto = sys.argv[1]
nome_base = os.path.splitext(os.path.basename(ficheiro_texto))[0]

pasta_saida = "fontes_anotadas"
os.makedirs(pasta_saida, exist_ok=True)
ficheiro_saida = os.path.join(pasta_saida, f"{nome_base}_ner.txt")

print(f"\nA extrair entidades de '{nome_base}' com spaCy...")

with open(ficheiro_texto, 'r', encoding='utf-8') as f:
    texto = f.read()

nlp = spacy.load("pt_core_news_sm")
doc = nlp(texto)

texto_anotado = texto

for ent in reversed(doc.ents):
    if ent.label_ in ["PER", "LOC", "ORG", "MISC"]:
        inicio = ent.start_char
        fim = ent.end_char
        
        texto_entidade = ent.text.replace('\n', ' ').strip()
        
        # Formatar para LaTeX: \textbf{Entidade} (LABEL)
        texto_anotado = texto_anotado[:inicio] + f"\\textbf{{{texto_entidade}}} ({ent.label_})" + texto_anotado[fim:]

# Limpar caracteres sensíveis do LaTeX e espaços invisíveis
texto_anotado = texto_anotado.replace('%', '\\%').replace('&', '\\&').replace('$', '\\$').replace('_', '\\_').replace('#', '\\#')
texto_anotado = texto_anotado.replace('\u200b', '').replace('\xa0', ' ').replace('\u202f', ' ')
texto_anotado = texto_anotado.replace('′', "'").replace('’', "'").replace('‘', "'")
texto_anotado = texto_anotado.replace('“', '"').replace('”', '"')
texto_anotado = texto_anotado.replace('–', '-').replace('—', '--')
texto_anotado = texto_anotado.replace('^', '') 
texto_anotado = texto_anotado.replace('ð', 'd').replace('Ð', 'D') 
texto_anotado = re.sub(r'[^\x00-\x7F\xC0-\xFF\u0100-\u017F\u2000-\u206F]', '', texto_anotado)

texto_anotado = texto_anotado.replace('\n', '\n\n')

with open(ficheiro_saida, 'w', encoding='utf-8') as f:
    f.write(texto_anotado)

print(f"Texto com entidades guardado em: {ficheiro_saida}")