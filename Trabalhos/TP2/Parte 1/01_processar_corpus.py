import os
import re
import json
from tqdm import tqdm


# =========================
# CONFIGURAÇÕES
# =========================

PASTA_FONTES = "fontes"
PASTA_OUTPUT = "corpus"

TAMANHO_CHUNK = 150      # número aproximado de palavras por chunk
OVERLAP = 30             # palavras repetidas entre chunks


# =========================
# LIMPEZA DE TEXTO
# =========================

def limpar_texto(texto):
    """
    Faz limpeza básica do texto:
    - remove múltiplos espaços
    - remove linhas vazias
    - remove caracteres estranhos
    """

    # remover quebras de linha
    texto = texto.replace("\n", " ")

    # remover tabs
    texto = texto.replace("\t", " ")

    # remover múltiplos espaços
    texto = re.sub(r"\s+", " ", texto)

    # remover espaços no início/fim
    texto = texto.strip()

    return texto


# =========================
# CRIAR CHUNKS
# =========================

def criar_chunks(texto, tamanho_chunk=200, overlap=50):
    """
    Divide texto em chunks com overlap.
    """

    palavras = texto.split()

    chunks = []

    inicio = 0

    while inicio < len(palavras):

        fim = inicio + tamanho_chunk

        chunk = palavras[inicio:fim]

        chunks.append(" ".join(chunk))

        inicio += (tamanho_chunk - overlap)

    return chunks


# =========================
# LER DOCUMENTOS
# =========================

def carregar_documentos():

    documentos = []

    ficheiros = os.listdir(PASTA_FONTES)

    doc_id = 0

    for ficheiro in tqdm(ficheiros):

        caminho = os.path.join(PASTA_FONTES, ficheiro)

        # ignorar pastas
        if not os.path.isfile(caminho):
            continue

        # apenas txt
        if not ficheiro.endswith(".txt"):
            continue

        try:

            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read()

            texto = limpar_texto(texto)

            documentos.append({
                "doc_id": doc_id,
                "fonte": ficheiro,
                "texto": texto
            })

            doc_id += 1

        except Exception as e:
            print(f"Erro ao ler {ficheiro}: {e}")

    return documentos


# =========================
# PROCESSAR CORPUS
# =========================

def processar_corpus(documentos):

    chunks_finais = []

    chunk_id = 0

    for doc in documentos:

        chunks = criar_chunks(
            doc["texto"],
            TAMANHO_CHUNK,
            OVERLAP
        )

        for chunk in chunks:

            chunks_finais.append({
                "chunk_id": chunk_id,
                "doc_id": doc["doc_id"],
                "fonte": doc["fonte"],
                "texto": chunk
            })

            chunk_id += 1

    return chunks_finais


# =========================
# GUARDAR JSON
# =========================

def guardar_json(nome_ficheiro, dados):

    os.makedirs(PASTA_OUTPUT, exist_ok=True)

    caminho = os.path.join(PASTA_OUTPUT, nome_ficheiro)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    print(f"\nFicheiro guardado em: {caminho}")


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar documentos...\n")

    documentos = carregar_documentos()

    print(f"\nDocumentos carregados: {len(documentos)}")

    print("\nA criar chunks...\n")

    chunks = processar_corpus(documentos)

    print(f"Chunks criados: {len(chunks)}")

    # guardar documentos completos
    guardar_json("corpus_processado.json", documentos)

    # guardar chunks
    guardar_json("chunks.json", chunks)

    print("\nProcessamento concluído com sucesso!")


if __name__ == "__main__":
    main()