import json
import pickle
import numpy as np
import torch
import re

from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# =========================
# CONFIGURAÇÃO
# =========================

CHUNKS_FILE = "corpus/chunks.json"
EMBEDDINGS_FILE = "corpus/sbert_embeddings.pkl"

SBERT_MODEL = "all-MiniLM-L6-v2"
GEN_MODEL = "google/flan-t5-base"

TOP_K = 5

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


# =========================
# CARREGAR CHUNKS
# =========================

def load_chunks():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "chunks" in data:
        return data["chunks"]

    raise ValueError("Formato de chunks.json inválido")


# =========================
# EXTRAIR TEXTO DO CHUNK
# =========================

def get_chunk_text(chunk):

    # caso seja string direta
    if isinstance(chunk, str):
        return chunk

    # caso seja dicionário
    if isinstance(chunk, dict):

        if "texto" in chunk:
            return chunk["texto"]

        if "chunk" in chunk:
            return chunk["chunk"]

        if "text" in chunk:
            return chunk["text"]

        if "content" in chunk:
            return chunk["content"]

    return ""


def get_chunk_source(chunk):

    if isinstance(chunk, dict):
        return str(chunk.get("fonte", ""))

    return ""


def extract_year(query):

    match = YEAR_RE.search(query)
    return match.group(0) if match else None


def normalize_query(query):

    query_norm = query.lower()
    query_norm = query_norm.replace("winer", "winner")
    query_norm = query_norm.replace("winnner", "winner")
    return query_norm


def lexical_bonus(texto, query):

    texto_l = texto.lower()
    query_l = query.lower()

    bonus = 0.0

    for termo in ["winner", "won", "win", "vencedor", "final", "contest", "eurovision", "song"]:
        if termo in query_l and termo in texto_l:
            bonus += 0.5

    if "win" in query_l and ("won" in texto_l or "winner" in texto_l):
        bonus += 1.0

    if "who" in query_l and ("won" in texto_l or "winner" in texto_l):
        bonus += 1.5

    if extract_year(query_l):
        year = extract_year(query_l)
        if year in texto_l and ("won" in texto_l or "winner" in texto_l):
            bonus += 1.5

    if ("who" in query_l or "win" in query_l or "winner" in query_l) and "won with" in texto_l:
        bonus += 5.0

    if extract_year(query_l):
        year = extract_year(query_l)
        if year in texto_l and "won with" in texto_l:
            bonus += 3.0

    if "winner's trophy" in texto_l or "main winner" in texto_l or "awards" in texto_l:
        bonus -= 0.5

    return bonus


def select_evidence(context, query, max_sentences=2):

    query_l = query.lower()
    year = extract_year(query_l)
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(context) if s.strip()]

    if not sentences:
        return context.strip()

    query_terms = [
        term for term in re.findall(r"[a-záàâãéêíóôõúç0-9]+", query_l)
        if term not in {"the", "a", "an", "of", "in", "on", "for", "to", "and", "or", "who", "what", "when", "where", "why", "how"}
    ]

    ranked = []

    for sentence in sentences:

        sentence_l = sentence.lower()
        score = 0.0

        if year and year in sentence_l:
            score += 2.0

        if "who" in query_l and ("won" in sentence_l or "winner" in sentence_l):
            score += 2.0

        if any(term in sentence_l for term in ["won", "winner", "win", "final", "points"]):
            score += 0.5

        for term in query_terms:
            if term in sentence_l:
                score += 0.25

        ranked.append((score, sentence))

    ranked.sort(key=lambda item: item[0], reverse=True)

    best = [sentence for score, sentence in ranked[:max_sentences] if score > 0]

    if not best:
        best = sentences[:max_sentences]

    return " ".join(best)


def extract_winner_from_text(text):

    # Try several patterns commonly used to state the winner
    patterns = [
        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,60}?) won with [0-9,]+ points",
        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,60}?) won the [0-9]{4} Eurovision",
        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,60}?) won the Eurovision Song Contest",
        r"winner was ([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,60}?)",
        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,60}?) was declared the winner",
        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,60}?) came first",
    ]

    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            # prefer the full matched substring if it contains 'won with' or similar
            full = m.group(0).strip()
            if 'won with' in full.lower() or 'won the' in full.lower() or 'was declared the winner' in full.lower():
                return full
            # otherwise return the captured name if present
            if m.lastindex and m.group(1):
                return m.group(1).strip()

    return None


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar chunks...\n")
    chunks = load_chunks()

    print(f"Chunks carregados: {len(chunks)}")

    # debug opcional
    print("\nExemplo de chunk:")
    print(chunks[0])

    print("\nA carregar modelo S-BERT...\n")
    embedder = SentenceTransformer(SBERT_MODEL)

    print("\nA carregar embeddings...\n")

    with open(EMBEDDINGS_FILE, "rb") as f:
        embeddings = pickle.load(f)

    print("\nA carregar modelo generativo (FLAN-T5)...\n")

    tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL)

    print("\nSistema pronto! Escreve 'sair' para terminar.\n")

    while True:

        query = input("Pergunta: ")

        if query.lower() == "sair":
            break

        query_norm = normalize_query(query)

        # =========================
        # RETRIEVAL
        # =========================

        ano = extract_year(query_norm)
        junior_query = "junior" in query_norm

        candidate_indices = []

        fonte_ano_exata = f"eurovision_song_contest_{ano}.txt" if ano else None
        junior_fonte_exata = f"junior_eurovision_song_contest_{ano}.txt" if ano else None

        for idx, chunk in enumerate(chunks):

            texto = get_chunk_text(chunk)
            fonte = get_chunk_source(chunk).lower()

            if ano:
                if junior_query:
                    if junior_fonte_exata and fonte != junior_fonte_exata:
                        continue
                else:
                    if fonte_ano_exata and fonte != fonte_ano_exata:
                        continue
                    if "junior_eurovision" in fonte:
                        continue

            candidate_indices.append(idx)

        if ano and not candidate_indices:
            candidate_indices = [
                idx for idx, chunk in enumerate(chunks)
                if ano in get_chunk_text(chunk) or ano in get_chunk_source(chunk).lower()
            ]

        if not ano and len(candidate_indices) < 10:
            candidate_indices = list(range(len(chunks)))

        query_emb = embedder.encode(
            query_norm,
            convert_to_tensor=True
        )

        embeddings_subset = embeddings[candidate_indices]

        scores = util.cos_sim(
            query_emb,
            embeddings_subset
        )[0].cpu().numpy()

        bonus_scores = np.array([
            lexical_bonus(get_chunk_text(chunks[idx]), query)
            for idx in candidate_indices
        ])

        scores = scores + bonus_scores

        top_results = np.argsort(scores)[-TOP_K:]
        top_results = top_results[::-1]

        # =========================
        # CONTEXTO
        # =========================

        contextos = []

        for i in top_results:

            chunk_idx = candidate_indices[i]
            texto = get_chunk_text(chunks[chunk_idx])

            if texto.strip():
                contextos.append(texto)

        context = "\n".join(contextos)
        # try deterministic extraction first (avoid generator hallucination)
        deterministic_answer = None

        for texto in contextos:
            det = extract_winner_from_text(texto)
            if det:
                deterministic_answer = det
                break

        if deterministic_answer:
            print("\n========== RESPOSTA ==========")
            print(deterministic_answer)
            print("==============================\n")
            continue

        context = select_evidence(context, query_norm, max_sentences=2)

        if not context.strip():
            print("\n[AVISO] Nenhum contexto válido foi recuperado para esta pergunta.\n")
            continue

        print("\n--- CONTEXTO USADO ---")
        print(context[:1200])
        print("----------------------\n")

        # =========================
        # PROMPT
        # =========================

        prompt = f"""
    Answer the question using ONLY the context below.
    If the context does not clearly contain the answer, reply exactly: "Não sei".

    Return one short, specific answer with the winner, country, or person asked for. Do not repeat the question and do not answer with a generic word like "Eurovision".

Context:
{context}

Question:
{query}

    Answer:
"""

        # =========================
        # TOKENIZAÇÃO
        # =========================

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        # =========================
        # GERAÇÃO
        # =========================

        with torch.no_grad():

            outputs = model.generate(
                **inputs,
                max_new_tokens=20,
                do_sample=False,
                num_beams=4,
                repetition_penalty=1.1,
                early_stopping=True
            )

        answer = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        ).strip()

        print("\n========== RESPOSTA ==========")
        print(answer)
        print("==============================\n")


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":
    main()