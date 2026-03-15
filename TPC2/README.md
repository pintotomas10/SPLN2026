# TPC1 - Atlas da Saúde - Web Scraper de Doenças

**Data:** 2026-03-15

## Descrição

Este projeto consiste num **web scraper em Python** que recolhe informação sobre várias doenças disponíveis no site **Atlas da Saúde**.

O script percorre todas as páginas de doenças organizadas alfabeticamente e extrai informação relevante de cada uma delas, criando automaticamente um **dataset em formato JSON**.

---

## Dados extraídos

Para cada doença são recolhidas as seguintes informações:

* **designação** – nome da doença
* **descrição** – pequeno resumo presente na lista de doenças
* **causas** – possíveis causas da doença
* **sintomas** – lista de sintomas associados
* **tratamento** – possíveis tratamentos

Todos os dados são guardados no ficheiro [doencas.json](doencas.json)

---

## Funcionamento do Script

O script segue os seguintes passos:

1. Percorre todas as letras do alfabeto (`A-Z`).
2. Para cada letra, acede à página correspondente de doenças:

	```
	https://www.atlasdasaude.pt/doencasaaz/<letra>
	```

3. Extrai todas as doenças listadas nessa página, incluindo:
	* nome
	* descrição pequena
	* link para a página completa

4. Acede à página individual de cada doença e extrai:
	* causas
	* sintomas
	* tratamento

5. Guarda os dados num **dicionário Python**.

6. No final, exporta toda a informação para um ficheiro **JSON**.

---

## Executar o script

```bash
python scrapping.py
```

Após a execução será criado o ficheiro [doencas.json](doencas.json)

---

## Autor
**Nome:** Tomás Pinto Rodrigues  
**ID:** A104448  
**Foto:**  
![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)
