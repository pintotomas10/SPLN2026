import os
import json
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer


# =========================
# CONFIGURAÇÕES
# =========================

FICHEIRO_CHUNKS = "corpus/chunks.json"

PASTA_OUTPUT = "corpus"

FICHEIRO_VECTORIZER = "tfidf_vectorizer.pkl"
FICHEIRO_MATRIZ = "tfidf_matrix.pkl"


# =========================
# CARREGAR CHUNKS
# =========================

def carregar_chunks():

    with open(FICHEIRO_CHUNKS, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return chunks


# =========================
# CRIAR TF-IDF
# =========================

def criar_tfidf(textos):

    """
    Cria a matriz TF-IDF.
    """

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=None,
        max_df=0.95,
        min_df=2,
        ngram_range=(1, 3)
    )

    matriz_tfidf = vectorizer.fit_transform(textos)

    return vectorizer, matriz_tfidf


# =========================
# GUARDAR OBJETOS
# =========================

def guardar_pickle(nome_ficheiro, objeto):

    caminho = os.path.join(PASTA_OUTPUT, nome_ficheiro)

    with open(caminho, "wb") as f:
        pickle.dump(objeto, f)

    print(f"Guardado: {caminho}")


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar chunks...\n")

    chunks = carregar_chunks()

    print(f"Chunks carregados: {len(chunks)}")

    textos = [chunk["texto"] for chunk in chunks]

    print("\nA criar matriz TF-IDF...\n")

    vectorizer, matriz_tfidf = criar_tfidf(textos)

    print("TF-IDF criado com sucesso!")

    print(f"\nNúmero de documentos: {matriz_tfidf.shape[0]}")
    print(f"Número de termos: {matriz_tfidf.shape[1]}")

    # guardar vectorizer
    guardar_pickle(FICHEIRO_VECTORIZER, vectorizer)

    # guardar matriz
    guardar_pickle(FICHEIRO_MATRIZ, matriz_tfidf)

    print("\nProcesso concluído!")


if __name__ == "__main__":
    main()