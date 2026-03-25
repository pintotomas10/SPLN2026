import re

def limpar_xml_para_txt(xml_path, txt_path):
    ignorar = False
    buffer_linha = ""
    with open(xml_path, 'r', encoding='utf-8') as xml_file, open(txt_path, 'w', encoding='utf-8') as txt_file:
        for line in xml_file:
            # Ignorar números de página
            if re.search(r'<text[^>]*font="0"[^>]*>\d+\s*</text>', line):
                continue
            # Ignorar figuras e mapas
            if re.search(r'<text[^>]*font="9"[^>]*>.*?(Figura|Mapa).*?</text>', line):
                continue
            # Ignorar notas de rodapé (font="7" e só número)
            if re.search(r'<text[^>]*font="7"[^>]*>\d+</text>', line):
                ignorar = True
                continue
            # Ignorar notas explicativas logo após nota de rodapé
            if ignorar and re.search(r'<text[^>]*font="(4|8)"[^>]*>.*?</text>', line):
                continue
            ignorar = False
            # Ignorar linhas com height="11"
            if re.search(r'<text[^>]*height="11"[^>]*>.*?</text>', line):
                continue
            # Extrair o texto limpo e remover tags <b>...</b> e <i>...</i>
            m = re.search(r'<text[^>]*>(.*?)</text>', line)
            if m:
                texto = m.group(1)
                texto = re.sub(r'<b>(.*?)</b>', r'\1', texto)
                texto = re.sub(r'<i>(.*?)</i>', r'\1', texto)
                texto = texto.strip()

                if not texto:
                    continue
                if buffer_linha:
                    buffer_linha += " " + texto
                else:
                    buffer_linha = texto

                # Se terminar frase → escreve
                if texto.endswith(('.', '!', '?')):
                    txt_file.write(buffer_linha + '\n')
                    buffer_linha = ""

limpar_xml_para_txt('content.xml', 'fontes/content.txt')