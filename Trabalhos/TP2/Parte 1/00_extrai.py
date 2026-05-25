import os
import re
import time
import urllib.request
import urllib.error

# Configuração Base Unificada
BASE_URL = "https://en.wikipedia.org"
OUTPUT_DIR = "fontes"

def criar_diretorio():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Pasta '{OUTPUT_DIR}' criada com sucesso.\n")

def descarregar_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'EurovisionUnifiedScraper/2.0 (contact: tom@di.uminho.pt) Python-requests'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Erro ao descarregar {url}: {e}")
        return None

def extrair_texto_puro_wikipedia(html_content, titulo_documento):
    """
    Função Universal de Extração: Limpa código, tabelas, infoboxes, referências
    e extrai o conteúdo textual de forma contínua em linhas por parágrafo.
    """
    # 1. Limpeza de blocos estruturais de código, tabelas e infoboxes
    html_limpo = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content, flags=re.IGNORECASE)
    html_limpo = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', html_limpo, flags=re.IGNORECASE)
    html_limpo = re.sub(r'<table\b[^<]*(?:(?!<\/table>)<[^<]*)*<\/table>', '', html_limpo, flags=re.IGNORECASE)
    html_limpo = re.sub(r'<sup class="reference"\b[^<]*(?:(?!<\/sup>)<[^<]*)*<\/sup>', '', html_limpo, flags=re.IGNORECASE)
    
    # Remover divs de classes conhecidas por acumular ruído ou imagens
    html_limpo = re.sub(r'<div class="thumb\b[^<]*(?:(?!<\/div>)<[^<]*)*<\/div>', '', html_limpo, flags=re.IGNORECASE)

    # 2. Capturar sequencialmente as tags de conteúdo útil (<p>, <h2>, <h3>, <li>)
    tags_interesse = re.findall(r'<(p|h2|h3|li)(?:\s[^>]*)?>(.*?)<\/\1>', html_limpo, flags=re.IGNORECASE | re.DOTALL)
    
    linhas_texto = [titulo_documento, ""]
    para_remover = False
    
    # Filtros para remover a navegação global e menus da Wikipédia
    links_menu_wiki = [
        "main page", "contents", "current events", "random article", "about wikipedia", 
        "contact us", "learn to edit", "community portal", "recent changes", "upload file", 
        "special pages", "donate", "create account", "log in", "article", "view history", 
        "what links here", "related changes", "permanent link", "page information", 
        "cite this page", "get shortened url", "download as pdf", "printable version", 
        "wikimedia commons", "wikidata item", "toggle notes"
    ]

    for tag, conteudo in tags_interesse:
        # Remover tags HTML internas (hiperligações, spans, estilos locais)
        texto_limpo = re.sub(r'<[^>]+>', '', conteudo)
        
        # Corrigir decodificações de entidades e caracteres especiais
        texto_limpo = texto_limpo.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&#160;', ' ')
        texto_limpo = texto_limpo.replace('&#8211;', '–').replace('&#32;', ' ')
        
        # Limpar os marcadores de parênteses retos residuais ex: &#91;1&#93; ou &#91;fr&#93;
        texto_limpo = re.sub(r'&#91;.*?&#93;', '', texto_limpo)
        texto_limpo = texto_limpo.replace('&#91;', '[').replace('&#93;', ']')

        # Normalizar múltiplos espaços no meio do parágrafo
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
        
        if not texto_limpo:
            continue
            
        # Processar títulos de secções
        if tag in ['h2', 'h3']:
            texto_limpo = re.sub(r'\[\s*edit\s*\]', '', texto_limpo, flags=re.IGNORECASE).strip()
            
            # Condição de fecho (ignora referências bibliográficas e links externos finais)
            if any(p in texto_limpo.lower() for p in ["references", "external links", "bibliography", "notes", "see also", "contents"]):
                para_remover = True
            else:
                para_remover = False
                
            if not para_remover and texto_limpo:
                linhas_texto.append(f"\n{texto_limpo}")
                
        # Processar blocos de texto corrido
        elif tag in ['p', 'li'] and not para_remover:
            texto_minusculo = texto_limpo.lower()
            
            # Aplicar filtros anti-ruído de menus
            if any(menu in texto_minusculo for menu in links_menu_wiki):
                continue
            if "coordinates" in texto_minusculo or "jump to" in texto_minusculo or texto_limpo == "International song competition":
                continue
            # Ignorar o menu lateral de idiomas
            if tag == 'li' and len(texto_limpo) < 35 and not texto_limpo.endswith('.'):
                continue
                
            if len(texto_limpo) > 5:
                linhas_texto.append(texto_limpo)

    return "\n\n".join(linhas_texto)

def obter_links_dinamicos(html_content, pattern_regex):
    """Auxiliar para varrer a página principal e extrair os links de cada ano válido."""
    links = {}
    matches = pattern_regex.findall(html_content)
    for ano in set(matches):
        links[ano] = f"{BASE_URL}/wiki/Eurovision_Song_Contest_{ano}" if "Junior" not in pattern_regex.pattern else f"{BASE_URL}/wiki/Junior_Eurovision_Song_Contest_{ano}"
    return links

def processar_e_guardar(url, titulo_doc, nome_ficheiro):
    """Descarrega, purifica e guarda uma página individual."""
    print(f"A processar: {titulo_doc}...")
    html = descarregar_html(url)
    if html:
        texto_limpo = extrair_texto_puro_wikipedia(html, titulo_doc)
        caminho_saida = os.path.join(OUTPUT_DIR, nome_ficheiro)
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(texto_limpo)
        print(f"  -> Sucesso: {nome_ficheiro}")
        return html
    return None

def main():
    criar_diretorio()
    
    # =========================================================================
    # PARTE 1: EUROVISION SONG CONTEST (ESC)
    # =========================================================================
    print("--- INICIANDO CONCURSO REGULAR (ESC) ---")
    url_esc_geral = f"{BASE_URL}/wiki/Eurovision_Song_Contest"
    html_esc_geral = processar_e_guardar(url_esc_geral, "Eurovision Song Contest - General Page", "Eurovision_Song_Contest_General.txt")
    
    if html_esc_geral:
        regex_esc = re.compile(r'href="/wiki/Eurovision_Song_Contest_(195[6-9]|19[6-9]\d|20[0-1]\d|202[0-6])"')
        links_esc_anos = obter_links_dinamicos(html_esc_geral, regex_esc)
        
        for ano in sorted(links_esc_anos.keys(), key=int):
            processar_e_guardar(links_esc_anos[ano], f"Eurovision Song Contest {ano}", f"Eurovision_Song_Contest_{ano}.txt")
            time.sleep(1.0)
            
    # =========================================================================
    # PARTE 2: JUNIOR EUROVISION SONG CONTEST (JESC)
    # =========================================================================
    print("\n--- INICIANDO JUNIOR EUROVISION (JESC) ---")
    url_jesc_geral = f"{BASE_URL}/wiki/Junior_Eurovision_Song_Contest"
    html_jesc_geral = processar_e_guardar(url_jesc_geral, "Junior Eurovision Song Contest - General Page", "Junior_Eurovision_Song_Contest_General.txt")
    
    if html_jesc_geral:
        regex_jesc = re.compile(r'href="/wiki/Junior_Eurovision_Song_Contest_(200[3-9]|201\d|202[0-6])"')
        links_jesc_anos = obter_links_dinamicos(html_jesc_geral, regex_jesc)
        
        for ano in sorted(links_jesc_anos.keys(), key=int):
            processar_e_guardar(links_jesc_anos[ano], f"Junior Eurovision Song Contest {ano}", f"Junior_Eurovision_Song_Contest_{ano}.txt")
            time.sleep(1.0)

    # =========================================================================
    # PARTE 3: OUTROS FESTIVAIS (DANCE, AMERICAN & ASIA)
    # =========================================================================
    print("\n--- INICIANDO FESTIVAIS ESPECIAIS E SPIN-OFFS ---")
    paginas_manuais = [
        {"url": f"{BASE_URL}/wiki/Eurovision_Dance_Contest", "titulo": "Eurovision Dance Contest - General Page", "fich": "Eurovision_Dance_Contest_General.txt"},
        {"url": f"{BASE_URL}/wiki/Eurovision_Dance_Contest_2007", "titulo": "Eurovision Dance Contest 2007", "fich": "Eurovision_Dance_Contest_2007.txt"},
        {"url": f"{BASE_URL}/wiki/Eurovision_Dance_Contest_2008", "titulo": "Eurovision Dance Contest 2008", "fich": "Eurovision_Dance_Contest_2008.txt"},
        {"url": f"{BASE_URL}/wiki/American_Song_Contest", "titulo": "American Song Contest", "fich": "American_Song_Contest.txt"},
        {"url": f"{BASE_URL}/wiki/Eurovision_Song_Contest_Asia", "titulo": "Eurovision Song Contest Asia", "fich": "Eurovision_Song_Contest_Asia.txt"}
    ]
    
    for pag in paginas_manuais:
        processar_e_guardar(pag["url"], pag["titulo"], pag["fich"])
        time.sleep(1.0)

    print(f"\n[Dataset Concluído] Todos os ficheiros foram gerados na pasta '{OUTPUT_DIR}'!")

if __name__ == "__main__":
    main()