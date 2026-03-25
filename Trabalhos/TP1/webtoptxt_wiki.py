
import requests
from bs4 import BeautifulSoup
import re

def extrair_texto_limpo(soup):
    conteudo = soup.find("div", {"id": "mw-content-text"})
    textos = []
    if conteudo is None:
        return ""
    secao_atual = ""
    buffer_paragrafos = []
    for tag in conteudo.find_all(["h2", "p"], recursive=True):
        if tag.name == "h2":
            if buffer_paragrafos and secao_atual:
                textos.append(f"{secao_atual}\n" + "\n".join(buffer_paragrafos))
            elif buffer_paragrafos:
                textos.append("\n".join(buffer_paragrafos))
            secao_atual = tag.get_text(strip=True).replace("editareditar código", "")
            buffer_paragrafos = []
        elif tag.name == "p":
            texto = tag.get_text(separator=" ", strip=True)
            texto = re.sub(r"\[\s*\d+\s*\]", "", texto)
            texto = re.sub(r"\s+", " ", texto)
            texto = texto.strip()
            if len(texto) > 50:
                buffer_paragrafos.append(texto)
    # Adiciona o último bloco, se existir
    if buffer_paragrafos:
        if secao_atual:
            textos.append(f"{secao_atual}\n" + "\n".join(buffer_paragrafos))
        else:
            textos.append("\n".join(buffer_paragrafos))
    return "\n\n".join(textos)

def obter_link_ano_seguinte(soup, ano_atual):
    # Procura o link para o próximo ano (ex: 1957, 1958, ...)
    proximo_ano = str(int(ano_atual) + 1)
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("/wiki/Festival_Eurovis%C3%A3o_da_Can%C3%A7%C3%A3o_") and proximo_ano in a["href"]:
            return "https://pt.wikipedia.org" + a["href"]
    return None

url = "https://pt.wikipedia.org/wiki/Festival_Eurovis%C3%A3o_da_Can%C3%A7%C3%A3o_1956"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}

with open("fontes/eurovisao_todos.txt", "w", encoding="utf-8") as f:
    while url:
        html = requests.get(url, headers=headers)
        soup = BeautifulSoup(html.text, "html.parser")
        # -------- TÍTULO --------
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text
            # título completo para o ficheiro
            match_ano = re.search(r"(\d{4})", title)
            if match_ano:
                ano_atual = match_ano.group(1)
            else:
                ano_atual = "????"
            titulo_limpo = re.search(r"^(.+?\d{4})\b", title)
            if titulo_limpo:
                titulo_escrever = titulo_limpo.group(0)
            else:
                titulo_escrever = title
        else:
            ano_atual = "????"
            titulo_escrever = "Sem título encontrado"
        print(titulo_escrever)
        texto_final = extrair_texto_limpo(soup)
        f.write(titulo_escrever + "\n\n")
        f.write(texto_final + "\n\n")
        # Próximo ano
        url = obter_link_ano_seguinte(soup, ano_atual)
        if not url:
            print("Não foi encontrado o link para o próximo ano.")
            break
print("Ficheiro limpo de todos os anos criado!")