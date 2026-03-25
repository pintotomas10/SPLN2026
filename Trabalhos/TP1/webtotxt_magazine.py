import requests
from bs4 import BeautifulSoup
import re

def extrair_texto_magazinehd(soup):
    textos = []

    # Conteúdo principal do artigo
    conteudo = soup.find("div", class_="entry-content")
    if not conteudo:
        return ""  # retorna vazio se não encontrou

    for tag in conteudo.find_all("p", recursive=True):
        # Ignora parágrafos dentro de divs de anúncio ou vídeos
        if tag.find_parent("div", class_=re.compile("magaz|rll-youtube-player")):
            continue
        texto = tag.get_text(separator=" ", strip=True)
        texto = re.sub(r"\[\d+\]", "", texto)
        texto = re.sub(r"\s+", " ", texto)
        if len(texto) > 50:
            textos.append(texto)

    return "\n\n".join(textos)

def obter_titulo_magazinehd(soup):
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    title_tag = soup.find("title")
    return title_tag.get_text(strip=True) if title_tag else "Sem título"

url = "https://www.magazine-hd.com/apps/wp/eurovisao-2025-napa-entrevista/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}

html = requests.get(url, headers=headers)
soup = BeautifulSoup(html.text, "html.parser")

titulo = obter_titulo_magazinehd(soup)
texto = extrair_texto_magazinehd(soup)

with open("fontes/eurovisao_napa_2025.txt", "w", encoding="utf-8") as f:
    f.write(titulo + "\n\n")
    f.write(texto)

print("Ficheiro limpo criado!")