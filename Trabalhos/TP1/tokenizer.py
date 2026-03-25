import json
import sys
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.util import ngrams
from collections import Counter

if len(sys.argv) < 2:
    print("Uso: python tokenizer.py <ficheiro_entrada>")
    sys.exit(1)

ficheiro_entrada = sys.argv[1]
nome_base = os.path.splitext(os.path.basename(ficheiro_entrada))[0]
ficheiro_saida_frases = f"fontes_tokenizadas/{nome_base}.txt"
ficheiro_saida_modelo = f"fontes_ngramas/{nome_base}.json"

with open(ficheiro_entrada, 'r', encoding='utf-8') as f:
    texto = f.read()

# Separar o texto em frases
frases = sent_tokenize(texto, language='portuguese')

todos_os_ngrams = []

# Processar frase a frase
frases_tokenizadas = []
for frase in frases:
    tokens = word_tokenize(frase.lower().strip(), language='portuguese')
    tokens_filtrados = [t for t in tokens if t.isalnum()]
    if not tokens_filtrados:
        continue
    frases_tokenizadas.append(" ".join(tokens_filtrados))
    # Gerar os 2-grams
    bigramas_da_frase = list(ngrams(tokens_filtrados, 2))
    todos_os_ngrams.extend(bigramas_da_frase)

# Construir o Modelo de Linguagem (Contar as frequências)
modelo_linguagem = Counter(todos_os_ngrams)

with open(ficheiro_saida_frases, 'w', encoding='utf-8') as f:
    for frase in frases_tokenizadas:
        f.write(frase + '\n')

modelo_para_guardar = {" ".join(bigrama): freq for bigrama, freq in modelo_linguagem.items()}

with open(ficheiro_saida_modelo, 'w', encoding='utf-8') as f:
    json.dump(modelo_para_guardar, f, ensure_ascii=False, indent=4)

print("Modelo de N-grams construído e guardado com sucesso!")
print(f"Frases guardadas em: {ficheiro_saida_frases}")
print(f"Modelo guardado em: {ficheiro_saida_modelo}\n")

print("Top 5 bigramas mais frequentes:")
for bigrama, frequencia in modelo_linguagem.most_common(5):
    print(f"{bigrama}: {frequencia} vezes")