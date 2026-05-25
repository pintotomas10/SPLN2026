import json
import pickle
import re
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# CONFIGURAÇÕES
# =========================

FICHEIRO_CHUNKS = "corpus/chunks.json"
FICHEIRO_EMBEDDINGS = "corpus/sbert_embeddings.pkl"

MODELO_S_BERT = "all-MiniLM-L6-v2"

TOP_K = 5

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


# =========================
# CARREGAR DADOS
# =========================

def carregar_chunks():

    with open(FICHEIRO_CHUNKS, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_embeddings():

    with open(FICHEIRO_EMBEDDINGS, "rb") as f:
        return pickle.load(f)


def extrair_ano(query):

    match = YEAR_RE.search(query)
    return match.group(0) if match else None


def normalizar_query(query):

    query_norm = query.lower()
    query_norm = query_norm.replace("winer", "winner")
    query_norm = query_norm.replace("winnner", "winner")
    return query_norm


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


# =========================
# RETRIEVER S-BERT
# =========================

def pesquisar(query, modelo, embeddings, chunks, top_k=5):

    query_norm = normalizar_query(query)
    ano = extrair_ano(query_norm)
    fonte_ano_exato = f"eurovision_song_contest_{ano}.txt" if ano else None
    junior_fonte_exata = f"junior_eurovision_song_contest_{ano}.txt" if ano else None
    junior_query = "junior" in query_norm

    # transformar query em embedding
    query_embedding = modelo.encode([query], convert_to_numpy=True)

    indices_candidatos = []

    for idx, chunk in enumerate(chunks):

        texto = chunk["texto"].lower()
        fonte = chunk.get("fonte", "").lower()

        if ano:
            if junior_query:
                if junior_fonte_exata and junior_fonte_exata != fonte:
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
            if (
                (junior_query and ano in chunk.get("fonte", "").lower() and "junior_eurovision_song_contest" in chunk.get("fonte", "").lower())
                or (not junior_query and ano in chunk.get("fonte", "").lower())
                or ano in chunk["texto"].lower()
            )
        ]

    if not indices_candidatos:
        indices_candidatos = list(range(len(chunks)))

    # calcular similaridade
    embeddings_subset = embeddings[indices_candidatos]
    scores = cosine_similarity(query_embedding, embeddings_subset).flatten()

    scores = np.array([
        score + bonus_lexical(chunks[indices_candidatos[pos]]["texto"], query_norm)
        for pos, score in enumerate(scores)
    ])

    # ordenar por score
    indices = np.argsort(scores)[::-1]

    resultados = []

    for idx in indices[:top_k]:

        chunk_idx = indices_candidatos[idx]

        resultados.append({
            "score": float(scores[idx]),
            "chunk": chunks[chunk_idx]
        })

    return resultados


# =========================
# MOSTRAR RESULTADOS
# =========================

def mostrar_resultados(resultados):

    print("\n========== RESULTADOS S-BERT ==========\n")

    for i, r in enumerate(resultados, start=1):

        print(f"Resultado #{i}")
        print(f"Score: {r['score']:.4f}")
        print(f"Fonte: {r['chunk']['fonte']}")
        print("\nTexto:")
        print(r['chunk']['texto'][:700])
        print("\n" + "-" * 50 + "\n")


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar dados...\n")

    chunks = carregar_chunks()
    embeddings = carregar_embeddings()

    print("A carregar modelo S-BERT...\n")

    modelo = SentenceTransformer(MODELO_S_BERT)

    print("Modelo carregado com sucesso!")

    while True:

        query = input("\nPergunta (ou 'sair'): ")

        if query.lower() == "sair":
            break

        resultados = pesquisar(
            query,
            modelo,
            embeddings,
            chunks,
            TOP_K
        )

        mostrar_resultados(resultados)


if __name__ == "__main__":
    main()