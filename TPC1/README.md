# TPC1 - Processamento de Dicionário Médico em XML

**Data:** 2026-03-08

## Resumo
Processamento de um ficheiro XML com conceitos médicos, extraindo e estruturando a informação relevante num ficheiro JSON para facilitar a consulta e análise.

O ficheiro XML (`medicina.xml`) foi gerado a partir do PDF original usando o seguinte comando:

```bash
pdftohtml -xml -f 20 -l 544 medicina.pdf
```
Assim, apenas as páginas relevantes do PDF foram convertidas para XML.

## Tarefas
### 1. Leitura e extração do texto
- Leitura do ficheiro `medicina.xml` como texto.
- Extração do conteúdo das tags `<text>` usando expressões regulares.

### 2. Limpeza e preparação dos dados
- Remoção de tags internas (`<i>`, `<b>`, etc.).
- Remoção de linhas irrelevantes (ex: linhas com "Vid.").
- Identificação dos conceitos pelo número no início da linha.

### 3. Processamento dos conceitos
- Extração do termo principal, classe gramatical, sinónimos, variantes, notas e traduções (es, en, pt, la).
- Estruturação dos conceitos numa lista de dicionários.

### 4. Exportação
- Exportação dos dados processados para o ficheiro `dicionario_medicina_xml.json`.


## Ficheiros
- `aula_xml.py` — Script principal de processamento.
- `medicina.xml` — Ficheiro XML de entrada com os conceitos médicos.
- `dicionario_medicina_xml.json` — Ficheiro JSON gerado com os conceitos extraídos.

## Estrutura do JSON
Cada entrada do JSON tem a seguinte estrutura:

```json
{
	"id": "<número do conceito>",
	"ga": "<termo principal>",
	"classe": "<classe gramatical>",
	"sin": "<sinónimos>",
	"var": "<variantes>",
	"nota": "<nota>",
	"es": ["traduções em espanhol"],
	"en": ["traduções em inglês"],
	"pt": ["traduções em português"],
	"la": ["traduções em latim"]
}
```

Campos podem estar vazios ou ausentes se não existirem no conceito original.

## Autor
**Nome:** Tomás Pinto Rodrigues  
**ID:** A104448  
**Foto:**  
![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)