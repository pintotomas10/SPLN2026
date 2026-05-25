import os
import json
import pickle

from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# =========================
# CONFIGURAÇÕES
# =========================

FICHEIRO_CHUNKS = "corpus/chunks.json"

PASTA_OUTPUT = "corpus"

FICHEIRO_EMBEDDINGS = "sbert_embeddings.pkl"

MODELO_S_BERT = "all-MiniLM-L6-v2"


# =========================
# CARREGAR CHUNKS
# =========================

def carregar_chunks():

    with open(FICHEIRO_CHUNKS, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return chunks


# =========================
# CRIAR EMBEDDINGS
# =========================

def criar_embeddings(modelo, textos):

    """
    Cria embeddings semânticos usando S-BERT.
    """

    embeddings = modelo.encode(
        textos,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return embeddings


# =========================
# GUARDAR EMBEDDINGS
# =========================

def guardar_embeddings(embeddings):

    caminho = os.path.join(PASTA_OUTPUT, FICHEIRO_EMBEDDINGS)

    with open(caminho, "wb") as f:
        pickle.dump(embeddings, f)

    print(f"\nEmbeddings guardados em: {caminho}")


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar chunks...\n")

    chunks = carregar_chunks()

    print(f"Chunks carregados: {len(chunks)}")

    textos = [chunk["texto"] for chunk in chunks]

    print("\nA carregar modelo S-BERT...\n")

    modelo = SentenceTransformer(MODELO_S_BERT)

    print(f"Modelo carregado: {MODELO_S_BERT}")

    print("\nA criar embeddings...\n")

    embeddings = criar_embeddings(modelo, textos)

    print("\nEmbeddings criados com sucesso!")

    print(f"Shape dos embeddings: {embeddings.shape}")

    guardar_embeddings(embeddings)

    print("\nProcesso concluído!")


if __name__ == "__main__":
    main()