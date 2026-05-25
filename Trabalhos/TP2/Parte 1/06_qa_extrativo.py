import json
import pickle
import re
import torch
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForQuestionAnswering


# =========================
# CONFIGURAÇÕES
# =========================

FICHEIRO_CHUNKS = "corpus/chunks.json"
FICHEIRO_EMBEDDINGS = "corpus/sbert_embeddings.pkl"

MODELO_S_BERT = "all-MiniLM-L6-v2"
MODELO_QA = "modelos/qa_finetuned"

TOP_K = 5

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

BAD_ANSWER_RE = re.compile(
    r"\b(points?|score|contest|eurovision|song|final|semi-final)\b",
    re.IGNORECASE
)


# =========================
# HELPERS
# =========================

def normalize_query(query):

    query_norm = query.lower()

    query_norm = query_norm.replace("winer", "winner")
    query_norm = query_norm.replace("winnner", "winner")

    return query_norm


def extract_year(query):

    match = YEAR_RE.search(query)

    return match.group(0) if match else None


def is_winner_query(query):

    query_l = normalize_query(query)

    return any(
        term in query_l
        for term in ["who", "winner", "win", "won"]
    )


def extract_winner_from_sentence(sentence):

    patterns = [

        r"the winner was ([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?) represented by",

        r"the winner was ([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?)$",

        r"winner was ([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?) represented by",

        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?) won with [0-9,]+ points",

        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?) won the [0-9]{4} Eurovision",

        r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?) won the Eurovision Song Contest",

        r"was won by ([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?)",

        r"won by ([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?)",

        r"winner was ([A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-\' ]{1,80}?)",

    ]

    for pat in patterns:

        m = re.search(pat, sentence, flags=re.IGNORECASE)

        if m and m.lastindex and m.group(1):

            return m.group(1).strip()

    return None


def select_evidence(context, query, max_sentences=2):

    query_l = normalize_query(query)

    year = extract_year(query_l)

    winner_query = is_winner_query(query_l)

    sentences = [
        s.strip()
        for s in SENTENCE_SPLIT_RE.split(context)
        if s.strip()
    ]

    if not sentences:
        return context.strip()

    query_terms = [

        term for term in re.findall(
            r"[a-záàâãéêíóôõúç0-9]+",
            query_l
        )

        if term not in {
            "the", "a", "an", "of", "in",
            "on", "for", "to", "and",
            "or", "who", "what", "when",
            "where", "why", "how"
        }
    ]

    ranked = []

    for sentence in sentences:

        sentence_l = sentence.lower()

        score = 0.0

        if year and year in sentence_l:
            score += 3.0

        if winner_query and (
            "won" in sentence_l
            or "winner" in sentence_l
        ):
            score += 4.0

        if any(
            mark in sentence_l
            for mark in [
                "won the",
                "won with",
                "winner was",
                "was won by",
                "won eurovision",
                "won the eurovision song contest"
            ]
        ):
            score += 8.0

        if (
            winner_query
            and "junior" in sentence_l
            and "junior" not in query_l
        ):
            score -= 5.0

        for term in query_terms:

            if term in sentence_l:
                score += 0.5

        ranked.append((score, sentence))

    ranked.sort(
        key=lambda item: item[0],
        reverse=True
    )

    best = [

        sentence
        for score, sentence in ranked[:max_sentences]
        if score > 0
    ]

    if not best:
        best = sentences[:max_sentences]

    return " ".join(best)


def repair_answer(answer, contexto, pergunta):

    pergunta_l = normalize_query(pergunta)

    answer_l = answer.lower().strip()

    winner_query = is_winner_query(pergunta_l)

    if not winner_query:
        return answer

    bad_answer = (

        not answer

        or any(ch.isdigit() for ch in answer)

        or BAD_ANSWER_RE.search(answer_l)

        or len(answer.split()) > 4
    )

    if not bad_answer:
        return answer

    candidates = [

        s.strip()
        for s in SENTENCE_SPLIT_RE.split(contexto)
        if s.strip()
    ]

    for sentence in candidates:

        if not any(
            term in sentence.lower()
            for term in ["won", "winner"]
        ):
            continue

        winner = extract_winner_from_sentence(sentence)

        if winner:
            return winner

    return answer


# =========================
# CARREGAR DADOS
# =========================

def carregar_chunks():

    with open(FICHEIRO_CHUNKS, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_embeddings():

    with open(FICHEIRO_EMBEDDINGS, "rb") as f:
        return pickle.load(f)


# =========================
# SCORE HEURÍSTICO
# =========================

def score_bonus(texto, query):

    texto_l = texto.lower()

    query_l = query.lower()

    bonus = 0.0

    anos = YEAR_RE.findall(query_l)

    for ano in anos:

        if ano in texto_l:
            bonus += 3.0

    keywords = [
        "eurovision",
        "winner",
        "win",
        "won",
        "vencedor",
        "song",
        "contest"
    ]

    for k in keywords:

        if k in query_l and k in texto_l:
            bonus += 1.0

    if any(
        mark in texto_l
        for mark in [
            "won the",
            "won with",
            "winner was",
            "was won by",
            "won eurovision",
            "won the eurovision song contest"
        ]
    ):
        bonus += 8.0

    if (
        "junior" in texto_l
        and "junior" not in query_l
    ):
        bonus -= 6.0

    return bonus


# =========================
# RETRIEVER
# =========================

def recuperar_contexto(
    query,
    modelo_sbert,
    embeddings,
    chunks,
    top_k=5
):

    query_l = normalize_query(query)

    winner_query = is_winner_query(query_l)

    ano_principal = extract_year(query_l)

    junior_query = "junior" in query_l

    fonte_ano_exata = (
        f"eurovision_song_contest_{ano_principal}.txt"
        if ano_principal else None
    )

    junior_fonte_exata = (
        f"junior_eurovision_song_contest_{ano_principal}.txt"
        if ano_principal else None
    )

    candidatos = []

    for i, c in enumerate(chunks):

        texto_original = c["texto"]

        texto = texto_original.lower()

        fonte = c.get("fonte", "").lower()

        # filtro forte por ano
        if ano_principal:

            if junior_query:

                if (
                    junior_fonte_exata
                    and fonte != junior_fonte_exata
                ):
                    continue

            else:

                if (
                    fonte_ano_exata
                    and fonte != fonte_ano_exata
                ):
                    continue

                if "junior_eurovision" in fonte:
                    continue

            if (
                ano_principal not in texto
                and ano_principal not in fonte
            ):
                continue

        candidatos.append((i, texto_original))

    # =========================
    # FILTRO EXTRA PARA WINNERS
    # =========================

    if winner_query:

        strict_candidates = []

        for i, text in candidatos:

            text_l = text.lower()

            if (
                ano_principal
                and ano_principal in text_l
                and any(
                    mark in text_l
                    for mark in [
                        "won the",
                        "won with",
                        "winner was",
                        "was won by",
                        "won eurovision",
                        "won the eurovision song contest"
                    ]
                )
            ):
                strict_candidates.append((i, text))

        if strict_candidates:
            candidatos = strict_candidates

    # fallback
    if not candidatos:

        candidatos = [
            (i, c["texto"])
            for i, c in enumerate(chunks)
        ]

    indices = [i for i, _ in candidatos]

    textos = [t for _, t in candidatos]

    emb_subset = embeddings[indices]

    query_emb = modelo_sbert.encode(
        [query_l],
        convert_to_numpy=True
    )

    scores = cosine_similarity(
        query_emb,
        emb_subset
    ).flatten()

    bonus_scores = np.array([
        score_bonus(texto, query)
        for texto in textos
    ])

    combined_scores = scores + (0.25 * bonus_scores)

    best = np.argsort(combined_scores)[::-1]

    final_texts = []

    for i in best[:top_k]:

        texto = textos[i]

        final_texts.append(
            select_evidence(
                texto,
                query_l,
                max_sentences=1 if winner_query else 2
            )
        )

    return "\n".join(final_texts)[:1500]


# =========================
# QA EXTRATIVO
# =========================

def responder(
    pergunta,
    contexto,
    tokenizer,
    model
):

    inputs = tokenizer(
        pergunta,
        contexto,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)

    start_logits = outputs.start_logits[0]

    end_logits = outputs.end_logits[0]

    sequence_ids = inputs.sequence_ids(0)

    top_start = torch.topk(
        start_logits,
        k=min(20, len(start_logits))
    ).indices.tolist()

    top_end = torch.topk(
        end_logits,
        k=min(20, len(end_logits))
    ).indices.tolist()

    melhor_inicio = None

    melhor_fim = None

    melhor_score = float("-inf")

    for inicio in top_start:

        if sequence_ids[inicio] != 1:
            continue

        for fim in top_end:

            if sequence_ids[fim] != 1:
                continue

            if fim < inicio:
                continue

            if fim - inicio > 20:
                continue

            score = float(
                start_logits[inicio]
                + end_logits[fim]
            )

            if score > melhor_score:

                melhor_score = score

                melhor_inicio = inicio

                melhor_fim = fim

    if melhor_inicio is None:

        return {
            "answer": "Sem resposta encontrada.",
            "score": 0.0
        }

    tokens = inputs["input_ids"][0][
        melhor_inicio:melhor_fim + 1
    ]

    answer = tokenizer.decode(
        tokens,
        skip_special_tokens=True
    ).strip()

    answer = repair_answer(
        answer,
        contexto,
        pergunta
    )

    return {
        "answer": answer,
        "score": round(melhor_score, 4)
    }


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar dados...\n")

    chunks = carregar_chunks()

    embeddings = carregar_embeddings()

    print("Chunks carregados:", len(chunks))

    print("\nA carregar modelo S-BERT...\n")

    modelo_sbert = SentenceTransformer(MODELO_S_BERT)

    print("A carregar modelo QA...\n")

    tokenizer = AutoTokenizer.from_pretrained(MODELO_QA)

    model = AutoModelForQuestionAnswering.from_pretrained(MODELO_QA)

    print("\nSistema pronto!\n")

    while True:

        pergunta = input("Pergunta (ou 'sair'): ")

        if pergunta.lower() == "sair":
            break

        contexto = recuperar_contexto(
            pergunta,
            modelo_sbert,
            embeddings,
            chunks,
            TOP_K
        )

        print("\n--- CONTEXTO USADO ---")
        print(contexto[:1000])
        print("----------------------\n")

        resposta = responder(
            pergunta,
            contexto,
            tokenizer,
            model
        )

        print("\n========== RESPOSTA ==========")
        print("Resposta:", resposta["answer"])
        print("Score:", resposta["score"])
        print("==============================\n")


if __name__ == "__main__":
    main()