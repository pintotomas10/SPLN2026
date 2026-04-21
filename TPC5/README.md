# TPC 5 - NER com spaCy

**Data:** 2026-04-21

Este trabalho tem duas partes:

1. O exercício da aula, que já estava a funcionar e serviu como ponto de comparação.
2. O treino de um modelo de `Named Entity Recognition` com `spaCy` usando os ficheiros `.iob` do trabalho.

Em termos práticos, o trabalho consistiu em preparar os dados, converter os ficheiros de treino e teste para o formato esperado pelo spaCy, correr o treino do modelo e depois comparar os resultados obtidos com os valores já registados no exercício da aula.

## Ficheiros

- `aula_1.ipynb` - exercício da aula.
- `spacy.ipynb` - notebook com os comandos principais do spaCy.
- `arquivo_ner_train.iob` e `arquivo_ner_test.iob` - dados de treino e teste.
- `datasets/` - ficheiros convertidos para formato `.spacy`.
- `output/` - modelo treinado pelo spaCy, incluindo `model-best`.

## Comandos usados

Os passos principais foram estes:

```bash
spacy convert arquivo_ner_train.iob ./datasets -c iob
spacy convert arquivo_ner_test.iob ./datasets -c iob
spacy init config config.cfg --lang pt --pipeline ner --optimize accuracy
spacy train config.cfg --output ./output --paths.train ./datasets/arquivo_ner_train.spacy --paths.dev ./datasets/arquivo_ner_test.spacy
```

## Resultados da aula

| Epoch | Training Loss | Validation Loss | Precision | Recall | F1 | Accuracy |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | No log | 0.077688 | 0.931162 | 0.959164 | 0.944956 | 0.981128 |
| 2 | No log | 0.068289 | 0.939114 | 0.966762 | 0.952737 | 0.983755 |

O melhor resultado do modelo da aula foi o da época 2, com `F1 = 0.952737`.

## Resultados do spaCy

Durante o treino do spaCy, o melhor valor observado foi:

| Epoch | LOSS TOK2VEC | LOSS NER | ENTS_F | ENTS_P | ENTS_R | SCORE |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 26 | 222.67 | 478.23 | 99.11 | 99.34 | 98.89 | 0.99 |

## Comparação

O modelo do spaCy ficou acima do modelo da aula nos valores de `Precision`, `Recall` e `F1`, pelo que foi o melhor resultado final deste trabalho.

## Conclusão

O trabalho consistiu em reutilizar o exercício da aula como base de comparação e treinar um modelo de NER com `spaCy` sobre os ficheiros `.iob` fornecidos. Depois da conversão dos dados e do treino, foi possível comparar os resultados e concluir que o modelo spaCy obteve valores superiores.

---

## Autor
**Nome:** Tomás Pinto Rodrigues  
**ID:** A104448  
**Foto:**  
![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)