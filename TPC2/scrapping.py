import requests
from bs4 import BeautifulSoup
import json
import string




def extrai_pagina(url):
    res = {}
    html_doc = requests.get(url)
    soup = BeautifulSoup(html_doc.text, "html.parser")
    doencas_div = soup.find_all("div", class_="views-row")
    for div in doencas_div:
        designacao = div.div.h3.a.text
        link = div.div.h3.a['href']
        descricao = div.find("div",class_="views-field-body").div.text
        res[designacao] = {
            "descricao": descricao.strip(),
            "link": link
        }
    return res

    
url = "https://www.atlasdasaude.pt/doencasaaz/"
res = {}

def extrai_detalhes_doenca(doenca_url):
    detalhes = {"causas": "", "sintomas": [], "tratamento": ""}
    html_doc = requests.get(doenca_url)
    soup = BeautifulSoup(html_doc.text, "html.parser")
    for secao in soup.find_all("h2"):
        titulo = secao.text.lower()
        conteudo = ""
        next_tag = secao.find_next_sibling()
        if next_tag:
            conteudo = next_tag.text.strip()
        if "causa" in titulo:
            detalhes["causas"] = conteudo
        elif "sintoma" in titulo:
            # Dividir sintomas por '\n', ';'
            sintomas = [s.strip() for s in conteudo.split('\n') if s.strip()]
            detalhes["sintomas"] = sintomas
        elif "tratament" in titulo:
            detalhes["tratamento"] = conteudo
    return detalhes

for l in string.ascii_uppercase:
    pagina = extrai_pagina(url + l)
    for nome, info in pagina.items():
        link_completo = "https://www.atlasdasaude.pt" + info["link"]
        detalhes = extrai_detalhes_doenca(link_completo)
        res[nome] = {
            "descricao": info["descricao"],
            "causas": detalhes["causas"],
            "sintomas": detalhes["sintomas"],
            "tratamento": detalhes["tratamento"]
        }

with open("doencas.json", "w", encoding="utf-8") as f_out:
    json.dump(res, f_out, indent=4, ensure_ascii=False)
    