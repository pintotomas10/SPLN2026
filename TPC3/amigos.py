import spacy
import json
import itertools
from collections import defaultdict

nlp = spacy.load("pt_core_news_sm")

with open("Harry Potter e A Pedra Filosofal.txt", "r", encoding="utf-8") as f:
    texto = f.read()

# Limpeza básica: remover aspas e travessões
for char in ['"', "'", "“", "”", "—", "–"]:
    texto = texto.replace(char, " ")

doc = nlp(texto)

MAPA_NOMES = {
        "sr. potter": "Harry Potter",
    "harry": "Harry Potter",
    "harry potter": "Harry Potter",
    "potter": "Harry Potter",

    "rony": "Rony Weasley",
    "rony weasley": "Rony Weasley",
    "ron": "Rony Weasley",

    "hermione": "Hermione Granger",
    "hermione granger": "Hermione Granger",

    "hagrid": "Rúbeo Hagrid",
    "rúbeo hagrid": "Rúbeo Hagrid",

    "dumbledore": "Alvo Dumbledore",
    "alvo dumbledore": "Alvo Dumbledore",
    "professor dumbledore": "Alvo Dumbledore",

    "snape": "Severo Snape",
    "severo snape": "Severo Snape",
    "professor snape": "Severo Snape",

    "mcgonagall": "Minerva McGonagall",
    "minerva": "Minerva McGonagall",
    "minerva mcgonagall": "Minerva McGonagall",
    "professora mcgonagall": "Minerva McGonagall",

    "draco": "Draco Malfoy",
    "malfoy": "Draco Malfoy",
    "draco malfoy": "Draco Malfoy",

    "neville": "Neville Longbottom",
    "neville longbottom": "Neville Longbottom",

    "fred": "Fred Weasley",
    "fred weasley": "Fred Weasley",

    "jorge": "Jorge Weasley",
    "george": "Jorge Weasley",
    "jorge weasley": "Jorge Weasley",

    "percy": "Percy Weasley",
    "percy weasley": "Percy Weasley",

    "duda": "Dudley Dursley",
    "dudley": "Dudley Dursley",

    "válter": "Vernon Dursley",
    "vernon": "Vernon Dursley",
    "tio válter": "Vernon Dursley",

    "petúnia": "Petúnia Dursley",
    "tia petúnia": "Petúnia Dursley",

    "olívio": "Olívio Wood",
    "olívio wood": "Olívio Wood",
    "wood": "Olívio Wood",

    "flamel": "Nicolau Flamel",
    "nicolau flamel": "Nicolau Flamel",

    "quirrell": "Quirrell",
    "voldemort": "Voldemort",
    "crabbe": "Crabbe",
    "goyle": "Goyle",
    "filch": "Argus Filch",

    "seamus": "Seamus Finnigan",
    "seamus finnigan": "Seamus Finnigan",

    "lavender": "Lavender Brown",
    "lavender brown": "Lavender Brown",

    "lee": "Lee Jordan",
    "lee jordan": "Lee Jordan",

    "argus": "Argus Filch",
    "argus filch": "Argus Filch",

    "lupin": "Lupin",
}

ocorrencias = defaultdict(lambda: defaultdict(int))

for sent in doc.sents:
    pessoas_na_frase = set()
    for ent in sent.ents:
        if ent.label_ == "PER":
            nome_original = ent.text.strip()
            nome_normalizado = nome_original.lower()
            nome_final = MAPA_NOMES.get(nome_normalizado, nome_normalizado)
            pessoas_na_frase.add(nome_final)
            
    pessoas_lista = list(pessoas_na_frase)
    
    if len(pessoas_lista) > 1:
        for p1, p2 in itertools.combinations(pessoas_lista, 2):
            ocorrencias[p1][p2] += 1
            ocorrencias[p2][p1] += 1 


# Ordenar as relações de cada personagem por número de coocorrências (maior para menor)
resultado_final = {}
for personagem, relacoes in ocorrencias.items():
    relacoes_ordenadas = dict(sorted(relacoes.items(), key=lambda item: item[1], reverse=True))
    resultado_final[personagem] = relacoes_ordenadas

with open("relacoes_harry_potter.json", "w", encoding="utf-8") as f_json:
    json.dump(resultado_final, f_json, indent=4, ensure_ascii=False)

print("Concluído! O ficheiro 'relacoes_harry_potter.json' foi gerado.")