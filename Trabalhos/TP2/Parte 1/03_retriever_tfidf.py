import json
import pickle
import re
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity


# =========================
# CONFIGURAÇÕES
# =========================

FICHEIRO_CHUNKS = "corpus/chunks.json"

FICHEIRO_VECTORIZER = "corpus/tfidf_vectorizer.pkl"
FICHEIRO_MATRIZ = "corpus/tfidf_matrix.pkl"

TOP_K = 5

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


# =========================
# CARREGAR DADOS
# =========================

def carregar_chunks():

    with open(FICHEIRO_CHUNKS, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return chunks


def carregar_pickle(caminho):

    with open(caminho, "rb") as f:
        objeto = pickle.load(f)

    return objeto


def extrair_ano(query):

    match = YEAR_RE.search(query)
    return match.group(0) if match else None


def bonus_lexical(texto, query):

    texto_l = texto.lower()
    query_l = query.lower()

    bonus = 0.0

    for termo in ["winner", "won", "win", "final", "contest", "eurovision", "song"]:
        if termo in query_l and termo in texto_l:
            bonus += 0.25

    if "who" in query_l and ("won" in texto_l or "winner" in texto_l):
        bonus += 0.5

    return bonus


def normalizar_query(query):

    query_norm = query.lower()
    return query_norm


# =========================
# RETRIEVER TF-IDF
# =========================

def pesquisar(query, vectorizer, matriz_tfidf, chunks, top_k=5):

    query_norm = normalizar_query(query)
    ano = extrair_ano(query_norm)
    fonte_ano_exato = f"eurovision_song_contest_{ano}.txt" if ano else None
    junior_query = "junior" in query_norm

    # transformar query em vetor TF-IDF
    query_vector = vectorizer.transform([query])

    # candidatos mais relevantes antes de ordenar
    indices_candidatos = []

    for idx, chunk in enumerate(chunks):

        texto = chunk["texto"].lower()
        fonte = chunk.get("fonte", "").lower()

        if ano:
            if junior_query:
                if not fonte.startswith("junior_eurovision_song_contest_"):
                    continue
            elif fonte_ano_exato and fonte_ano_exato != fonte:
                continue

        if "eurovision" in query_norm and not junior_query:
            if "junior_eurovision" in fonte:
                continue

        indices_candidatos.append(idx)

    if ano and len(indices_candidatos) < 3:
        indices_candidatos = [
            idx for idx, chunk in enumerate(chunks)
            if ano in chunk.get("fonte", "").lower() or ano in chunk["texto"].lower()
        ]

    if not indices_candidatos:
        indices_candidatos = list(range(len(chunks)))

    matriz_subset = matriz_tfidf[indices_candidatos]

    # calcular similaridade
    similaridades = cosine_similarity(query_vector, matriz_subset).flatten()

    similaridades = np.array([
        score + bonus_lexical(chunks[indices_candidatos[pos]]["texto"], query_norm)
        for pos, score in enumerate(similaridades)
    ])

    # ordenar índices
    indices_ordenados = np.argsort(similaridades)[::-1]

    # top resultados
    resultados = []

    for idx in indices_ordenados[:top_k]:

        chunk_idx = indices_candidatos[idx]

        resultado = {
            "score": float(similaridades[idx]),
            "chunk": chunks[chunk_idx]
        }

        resultados.append(resultado)

    return resultados


# =========================
# MOSTRAR RESULTADOS
# =========================

def mostrar_resultados(resultados):

    print("\n========== RESULTADOS ==========\n")

    for i, resultado in enumerate(resultados, start=1):

        print(f"Resultado #{i}")
        print(f"Score: {resultado['score']:.4f}")

        print(f"Fonte: {resultado['chunk']['fonte']}")

        print("\nTexto:")
        print(resultado['chunk']['texto'][:700])

        print("\n" + "="*50 + "\n")


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar dados...\n")

    chunks = carregar_chunks()

    vectorizer = carregar_pickle(FICHEIRO_VECTORIZER)

    matriz_tfidf = carregar_pickle(FICHEIRO_MATRIZ)

    print("Dados carregados com sucesso!")

    while True:

        query = input("\nInsere uma pergunta (ou 'sair'): ")

        if query.lower() == "sair":
            break

        resultados = pesquisar(
            query,
            vectorizer,
            matriz_tfidf,
            chunks,
            TOP_K
        )

        mostrar_resultados(resultados)


if __name__ == "__main__":
    main()