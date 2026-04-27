from collections import Counter

from nltk import word_tokenize # type: ignore
from nltk.corpus import stopwords # type: ignore
import math

# coleção de frases
corpus = [
    "the sky is blue",
    "the sun is bright",
    "the sun in the sky"
]

# remover pontuação, normalizar as palavras e remover stop words (the, is, in)
def tokenizer(doc):
    return[w for w in word_tokenize(doc) if w not in stopwords.words('english')]

corpus_tokens = [tokenizer(doc) for doc in corpus]

print(corpus_tokens)
# [['sky', 'blue'], ['sun', 'bright'], ['sun', 'sky']]

# def tf(t, doc_tokens):
#     N = len(doc_tokens)
#     res = 0
#     for p in doc_tokens:
#         if p == t:
#             res += 1
#     return res / N
# 
# def doc_tf(doc_tokens):
#     res = {}
#     for t in doc_tokens:
#         res[t] = tf(t, doc_tokens)
#     return res

def doc_tf(doc_tokens):
    N = len(doc_tokens)
    count = Counter(doc_tokens)
    for c in count:
        count[c] /= N
    return count

def idf_aux(t, corpus_tokens):
    N = len(corpus_tokens)
    df = 0
    for d in corpus_tokens:
        if t in d:
            df += 1
    return math.log(N/df, 10)

def idf(corpus_tokens):
    tokens = set([token for d in corpus_tokens for token in d])
    res = {}
    for t in tokens:
        res[t] = idf_aux(t, corpus_tokens)
    return res

def tf_idf(corpus_tokens):
    res = []
    idf_dict = idf(corpus_tokens)
    for doc_tokens in corpus_tokens:
        tf_dict = doc_tf(doc_tokens)
        tf_idf_dict = {}
        for termo in tf_dict:
            tf_idf_dict[termo] = tf_dict[termo] * idf_dict[termo]
        res.append(tf_idf_dict)
    return res

# print(tf_idf(corpus_tokens))

def vectorize(tf_idf_list, vocab=None):
    if vocab is None:
        vocab = sorted({token for d in corpus_tokens for token in d})
    res = []
    for doc in tf_idf_list:
        res.append([doc.get(t, 0) for t in vocab])
    return res, vocab

def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

tf_idf_list = tf_idf(corpus_tokens)
doc_vector, vocab = vectorize(tf_idf_list)
print(doc_vector)

query = "the bright sun"

query_tokens = tokenizer(query)
query_tf = doc_tf(query_tokens)
query_idf = idf(corpus_tokens)

def query_tf_idf(query_tf, query_idf):
    res = {}
    for termo in query_tf:
        res[termo] = query_tf[termo] * query_idf.get(termo, 0)
    return res
print (query_tf_idf(query_tf, query_idf))

query_tf_idf_dict = query_tf_idf(query_tf, query_idf)
query_vector = [query_tf_idf_dict.get(t, 0) for t in vocab]

scores = []
for i, doc_vector_item in enumerate(doc_vector):
    score = cosine_similarity(query_vector, doc_vector_item)
    scores.append((i, score, corpus[i]))

scores.sort(key=lambda x: x[1], reverse=True)

print("\nSimilaridade da query com cada documento:")
for i, score, doc in scores:
    print(f"doc {i + 1}: {score:.3f} -> {doc}")

print("\nDocumento mais relevante:")
print(scores[0])

# tf query {bright: 0,5, sun: 0,5}
# idf query {bright: 0.477, sun: 0.176}    
# tf_idf query {sun: 0.176*0.5, bright: 0.477*0.5, sky: 0.0, blue: 0.0}

