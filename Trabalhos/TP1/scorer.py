import json
import sys
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.util import ngrams

if len(sys.argv) < 3:
    print("Uso: python scorer.py <ficheiro_original_txt> <ficheiro_modelo_json>")
    sys.exit(1)

ficheiro_texto = sys.argv[1]
ficheiro_modelo = sys.argv[2]
nome_base = os.path.splitext(os.path.basename(ficheiro_texto))[0]

with open(ficheiro_modelo, 'r', encoding='utf-8') as f:
    modelo_linguagem = json.load(f)

with open(ficheiro_texto, 'r', encoding='utf-8') as f:
    texto = f.read()

# Dividir primeiro por quebras de linha
frases_originais = []
for bloco_de_texto in texto.split('\n'):
    bloco_de_texto = bloco_de_texto.strip()
    if bloco_de_texto: 
        frases_do_bloco = sent_tokenize(bloco_de_texto, language='portuguese')
        frases_originais.extend(frases_do_bloco)

pontuacoes_das_frases = []

# Calcular o Score para cada frase
for frase in frases_originais:
    # Tokenizar na hora apenas para calcular os bigramas
    tokens = word_tokenize(frase.lower().strip(), language='portuguese')
    tokens_filtrados = [t for t in tokens if t.isalnum()]
    if len(tokens_filtrados) < 12:
        continue
    if "festival eurovisão da canção" in frase.lower():
        continue
    if frase.strip().endswith("?"):
        continue
    bigramas_da_frase = list(ngrams(tokens_filtrados, 2))
    
    score_total = 0
    # Somar a frequência de cada bigrama consultando o nosso JSON
    for bigrama in bigramas_da_frase:
        chave_json = " ".join(bigrama)
        score_total += modelo_linguagem.get(chave_json, 0)
    
    # Dividir pelo número de bigramas para não favorecer frases gigantes
    score_normalizado = score_total / len(bigramas_da_frase)
    
    palavras_unicas = len(set(tokens_filtrados))
    score_normalizado *= (palavras_unicas / len(tokens_filtrados))
    
    # Guardar a frase original e o seu score num tuplo
    pontuacoes_das_frases.append((score_normalizado, frase))

pontuacoes_das_frases.sort(reverse=True, key=lambda x: x[0])
top_3 = pontuacoes_das_frases[:3]

print(f"\nTOP 3 Frases para: {nome_base}")
print("-" * 50)

top_3_texto = []

for i, (score, frase) in enumerate(top_3, 1):
    print(f"{i}. [Score: {score:.2f}] {frase}\n")
    top_3_texto.append(frase)

pasta_destino = "fontes_top3" 
caminho_saida = os.path.join(pasta_destino, f"{nome_base}.json")

with open(caminho_saida, 'w', encoding='utf-8') as f:
    json.dump(top_3_texto, f, ensure_ascii=False, indent=4)

print(f"Ficheiro guardado com sucesso em: {caminho_saida}\n")