# TPC 6 - TF-IDF

**Data:** 2026-04-27

Este trabalho consiste na implementação de um pequeno sistema de pesquisa textual com base em `TF-IDF`.

O objetivo foi partir de um corpus curto, fazer o pré-processamento dos textos, calcular os pesos `TF-IDF` dos documentos e, por fim, medir a relevância de uma query com `similaridade cosseno`.


## O que foi feito

1. Criou-se um corpus pequeno com três frases de exemplo.
2. Definiu-se um `tokenizer` para:
	- remover pontuação;
	- normalizar o texto;
	- remover stop words em inglês.
3. Calculou-se o `TF` de cada documento.
4. Calculou-se o `IDF` a partir de todo o corpus.
5. Combinou-se `TF` e `IDF` para obter o peso `TF-IDF` de cada termo em cada documento.
6. Vetorizou-se cada documento numa matriz de pesos.
7. Processou-se também a query com o mesmo pré-processamento.
8. Calculou-se o vetor `TF-IDF` da query.
9. Comparou-se a query com cada documento através da `similaridade cosseno`.
10. Ordenaram-se os documentos por relevância e identificou-se o mais próximo da query.

## Fórmulas usadas

### TF - Term Frequency

`TF(t, d) = frequência do termo no documento / número total de tokens do documento`

### IDF - Inverse Document Frequency

`IDF(t) = log10(nº de documentos / nº de documentos que contêm o termo)`

### TF-IDF

`TF-IDF(t, d) = TF(t, d) × IDF(t)`

### Similaridade cosseno

`cos(θ) = (A · B) / (||A|| × ||B||)`

Esta métrica permite comparar a query com os documentos e perceber quais são os vetores mais relevantes.

## Exemplo de funcionamento

O corpus usado no script é este:

- `the sky is blue`
- `the sun is bright`
- `the sun in the sky`

Depois do pré-processamento, a query `the bright sun` é transformada num vetor e comparada com os documentos do corpus.

O resultado obtido mostra a seguinte lista de documentos por ordem de relevância:

- `doc 2: 1.000 -> the sun is bright`
- `doc 3: 0.245 -> the sun in the sky`
- `doc 1: 0.000 -> the sky is blue`


## Conclusão

O exercício serviu para perceber o fluxo completo de recuperação de informação com `TF-IDF`: limpeza dos dados, construção dos vetores e ranking final da query por similaridade.

---

## Autor
**Nome:** Tomás Pinto Rodrigues  
**ID:** A104448  
**Foto:**  
![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)