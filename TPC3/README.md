# TPC3 - Relações de Personagens em Harry Potter

**Data:** 2026-03-23

## Descrição

Este projeto consiste numa análise automática das relações entre personagens do livro **Harry Potter e a Pedra Filosofal**. Utilizando **Processamento de Linguagem Natural (spaCy)**, o script identifica personagens em cada frase do texto e constrói uma rede de coocorrências, indicando quantas vezes cada par de personagens aparece junto.

O resultado é exportado para um ficheiro **JSON** que representa as relações entre personagens.

---

## Dados extraídos

Para cada personagem são recolhidas as seguintes informações:

* **nome** – nome normalizado da personagem
* **relações** – dicionário com outros personagens e o número de frases em que aparecem juntos

Todos os dados são guardados no ficheiro [relacoes_harry_potter.json](relacoes_harry_potter.json)

---

## Funcionamento do Script

O script segue os seguintes passos:

1. Lê o texto completo do livro "Harry Potter e a Pedra Filosofal".
2. Remove caracteres especiais e faz uma limpeza básica do texto.
3. Utiliza o modelo spaCy para identificar entidades do tipo pessoa (PER).
4. Normaliza os nomes das personagens usando um dicionário de mapeamento para garantir consistência (ex: “harry”, “sr. potter” → “Harry Potter”).
5. Para cada frase, regista pares de personagens que aparecem juntos.
6. Conta o número de coocorrências entre cada par de personagens.
7. Exporta os resultados para um ficheiro **JSON**.

---

## Executar o script

```bash
python amigos.py
```

Após a execução será criado o ficheiro [relacoes_harry_potter.json](relacoes_harry_potter.json)

---

## Autor
**Nome:** Tomás Pinto Rodrigues  
**ID:** A104448  
**Foto:**  
![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)