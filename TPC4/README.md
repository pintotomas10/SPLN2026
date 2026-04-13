# TPC4 - Word2Vec com Harry Potter

**Data:** 2026-04-10

## Objetivo
Treinar um modelo Word2Vec com os textos dos livros de Harry Potter e explorar relacoes semanticas com:
- most_similar
- similarity
- doesnt_match
- analogy
- visualizacao com scatterplot (PCA)

## Resumo
Este trabalho foi desenvolvido em 3 fases incrementais:

- Fase 1 (2 livros):
	- validacao inicial do pipeline (pre-processamento + treino Word2Vec + testes basicos)
	- foco em confirmar que as funcoes semanticas produziam resultados coerentes

- Fase 2 (7 livros):
	- expansao do corpus para toda a saga principal usada no projeto
	- reexecucao completa dos testes para comparar com a Fase 1
	- analise das diferencas de vocabulario e de similaridade entre personagens/termos

- Fase 3 (7 livros + MAPA_NOMES):
	- normalizacao de aliases de personagens (ex.: `mione` -> `hermione_granger`)
	- canonizacao de entidades para reduzir ruido de OCR/variantes nominais
	- testes executados com conversao automatica para tokens canonicos

Resultado geral:
- o modelo ficou progressivamente mais robusto ao longo das fases,
- e a Fase 3 melhorou a consistencia das comparacoes semanticas entre personagens.

## Dados usados
Fase 1 (validacao inicial):
- Harry Potter e A Pedra Filosofal
- Harry Potter e a Camara Secreta

Fase 2 (expansao do corpus):
- Harry Potter e A Pedra Filosofal
- Harry Potter e a Camara Secreta
- Harry Potter e o Prisioneiro de Azkaban
- Harry Potter e o Calice de Fogo
- Harry Potter e a Ordem da Fenix
- Harry Potter e o Enigma do Principe
- Harry Potter e as Reliquias da Morte

Observacao: primeiro os testes e exemplos foram executados com os 2 primeiros livros; depois, o mesmo fluxo foi repetido com todos os livros acima.

## Pre-processamento
Foi aplicado um pre-processamento simples:
- conversao para minusculas
- remocao de pontuacao e caracteres fora do intervalo textual esperado
- normalizacao de espacos
- tokenizacao por espaco

## Treino do modelo
Modelo treinado com Gensim Word2Vec.

Configuracao usada no notebook:
- vector_size = 300
- epochs = 20

## Estado atual do experimento
Para permitir comparacao entre fases, os resultados antigos (2 livros) e atuais (7 livros) sao mantidos abaixo.

Fase 1 (2 livros):
- experimento inicial de validacao (Pedra Filosofal + Camara Secreta)

Fase 2 (7 livros):
- num_sentencas = 118958
- vocab_size = 11337

Fase 3 (7 livros + normalizacao por lista de nomes):
- num_sentencas_f3 = 118958
- vocab_size_f3 = 11329
- validacao: tokens de alias deixaram de existir separadamente e passaram para formas canonicas (ex.: `mione` -> `hermione_granger`, `harry` -> `harry_potter`, `rony` -> `rony_weasley`)

Observacao: os testes continuam a usar `rony` (em vez de `ron`) porque essa forma esta mais presente no vocabulario processado.
Observacao 2: na Fase 3, as consultas dos testes sao automaticamente convertidas para os tokens canonicos antes de calcular similaridades/analogias.

## Testes realizados

### 1) most_similar
Resultados historicos (2 livros):
- most_similar('harry') trouxe personagens proximas no contexto narrativo (como hermione/rony/neville/draco).
- most_similar('dumbledore') trouxe nomes de professores e personagens ligados ao ambiente escolar.
- most_similar('rony'), 'snape', 'voldemort' e 'hagrid' tambem mostraram vizinhancas semanticas coerentes com o contexto dos livros.

Resultados (7 livros):
- harry -> garoto, arry, ele, cho, moody
- rony -> gina, cho, travers, irritada, luna
- hermione -> mione, cho, grampo, nervoso, luna
- hogwarts -> azkaban, hogsmeade, durmstrang, setembro, outubro
- dumbledore -> binns, slughorn, diretor, moody, quirrell

Resultados (Fase 3 - com aliases):
- hermione_granger -> grampo, cho, garota, luna, zangado, parvati...
- harry_potter -> garoto, ele, cho, moody, neville_longbottom...
- `mione` ja nao aparece como similar de `hermione_granger` porque foi normalizado para o mesmo nome canonico.

Leitura:
- O modelo aproxima personagens e elementos que aparecem em contextos semelhantes.
- Tambem aparecem tokens ruidosos (ex.: `arry`, `mione`), provavelmente por OCR/pre-processamento.

### 2) similarity
Comparacao direta (2 livros vs 7 livros):
- sim(harry, rony): 0.5963 -> 0.3374
- sim(hermione, rony): 0.7244 -> 0.1971
- sim(hagrid, dumbledore): 0.6593 -> 0.3297
- sim(voldemort, dumbledore): 0.3294 -> 0.4239

Resultado adicional da Fase 3:
- sim(harry, rony) [harry_potter, rony_weasley] = 0.3533
- sim(harry, hermione) [harry_potter, hermione_granger] = 0.2856
- sim(harry, voldemort) [harry_potter, voldemort] = 0.2070
- sim(hogwarts, escola) [hogwarts, escola] = 0.4783

Resultados adicionais (7 livros):
- sim(harry, hermione) = 0.2661
- sim(harry, voldemort) = 0.1752
- sim(hogwarts, escola) = 0.4714
- sim(harry, snape) = 0.2552

Leitura geral:
- O par com maior proximidade neste conjunto de exemplos foi (hogwarts, escola).
- Pares de oposicao narrativa (ex.: harry, voldemort) ficam mais baixos do que pares do mesmo contexto escolar.
- Em varios pares, a expansao do corpus alterou as magnitudes de similaridade, indicando mudanca na distribuicao de contexto.

### 3) doesnt_match
Resultados historicos (2 livros):
- [harry, rony, hermione, voldemort] -> voldemort
- [snape, dumbledore, hagrid, varinha] -> varinha
- [hogwarts, magia, escola, draco] -> draco

Exemplos (7 livros):
- [harry, rony, hermione, voldemort] -> voldemort
- [snape, dumbledore, hagrid, varinha] -> varinha
- [hogwarts, magia, escola, draco] -> draco
- [harry, rony, hermione, vassoura] -> vassoura
- [hogwarts, dumbledore, snape, escola] -> snape

Exemplos (Fase 3 canonicos):
- [harry, rony, hermione, voldemort] -> [harry_potter, rony_weasley, hermione_granger, voldemort] -> voldemort
- [snape, dumbledore, hagrid, varinha] -> [severo_snape, alvo_dumbledore, rubeo_hagrid, varinha] -> varinha
- [hogwarts, magia, escola, draco] -> [hogwarts, magia, escola, draco_malfoy] -> draco_malfoy

Interpretacao:
- o modelo consegue separar bem personagens de objetos/conceitos
- tambem distingue elementos de categoria diferente na mesma lista

### 4) analogy
Resultados historicos (2 livros):
- harry : hermione :: rony : ?
- snape : dumbledore :: draco : ?
- Saidas tipicas incluiram termos semanticamente relacionados (ex.: malfoy na segunda analogia).

Exemplos testados (7 livros):
- harry : hermione :: rony : ?
- snape : dumbledore :: draco : ?
- harry : rony :: hermione : ?
- dumbledore : hogwarts :: hagrid : ?

Resultados observados incluem, por exemplo:
- harry : hermione :: rony : ? -> mione, luna, gina
- snape : dumbledore :: draco : ? -> lucio, papai, aberforth
- harry : rony :: hermione : ? -> mione, luna, gina, lilá
- dumbledore : hogwarts :: hagrid : ? -> londres, hogsmeade, azkaban

Resultados observados (Fase 3 canonica), por exemplo:
- harry : rony :: hermione : ? -> luna, parvati, lilá, gina, grampo
- dumbledore : hogwarts :: hagrid : ? -> hogsmeade, londres, gruta, caça, azkaban
- snape : dumbledore :: draco : ? -> crouch, borgin, gaunt

Leitura:
- O espaco vetorial capta relacoes uteis, mas tambem mistura associacoes de contexto com ruido textual.

## Visualizacao (PCA Scatterplot)
Foi criado um grafico 2D com PCA para palavras do universo Harry Potter.

Palavras usadas no grafico incluem:
- personagens: harry/harry_potter, rony/rony_weasley, hermione/hermione_granger, dumbledore/alvo_dumbledore, snape/severo_snape, hagrid/rubeo_hagrid, voldemort, draco/draco_malfoy
- conceitos: magia, escola, varinha, bruxo
- local: hogwarts

Leitura da visualizacao:
- Houve agrupamento de personagens (ex.: snape, draco, dumbledore, hermione, hagrid, rony) em regiao proxima.
- Termos mais gerais (magia, escola) e `hogwarts` ficaram afastados desse cluster.
- `varinha` apareceu como outlier forte, distante dos outros pontos.
- Na Fase 3, os labels passam a aparecer no formato canonico (ex.: `harry_potter`, `severo_snape`, `alvo_dumbledore`).

## Conclusoes
- A expansao para os 7 livros aumentou a cobertura lexical e permitiu analises mais ricas.
- Os resultados da fase com 2 livros foram preservados para comparacao historica com a fase completa.
- As funcoes most_similar, similarity e doesnt_match continuam coerentes em varios exemplos narrativos.
- A Fase 3 reduz parte do ruido de entidades, consolidando variantes de nomes (ex.: `mione` -> `hermione_granger`).
- A Fase 3 com MAPA_NOMES melhorou a consistencia dos testes, porque as consultas passam a comparar entidades canonicas.
- Analogias funcionam parcialmente, com presenca de ruido residual (ex.: `arry`), ainda mitigavel com mais aliases/limpeza.
- A normalizacao dos tokens continua essencial para estabilidade dos resultados (caso `rony`).

---

## Autor
**Nome:** Tomás Pinto Rodrigues  
**ID:** A104448  
**Foto:**  
![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)