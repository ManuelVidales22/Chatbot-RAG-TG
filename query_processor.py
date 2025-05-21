import spacy
import os
import pickle
from langchain_openai import ChatOpenAI
from rank_bm25 import BM25Okapi
from langchain.schema import Document

_NLP_MODEL = None

#Ruta del corpus de BM25
BM25_CORPUS_PATH = "bm25_corpus.pkl"

#Cargar el modelo de lenguaje de spaCy
def get_nlp_model():
    global _NLP_MODEL
    if _NLP_MODEL is None:
        try:
            _NLP_MODEL = spacy.load("es_core_news_sm")
        except OSError:
            raise Exception("Modelo spaCy no instalado. Ejecuta: python -m spacy download es_core_news_sm")
    return _NLP_MODEL

# Función para limpiar y lematizar la consulta
def clean_text(query):
    nlp = get_nlp_model()
    doc = nlp(query)
    clean_words = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(clean_words)

#Cargar el corpus de BM25
def load_bm25_corpus():
    with open(BM25_CORPUS_PATH, "rb") as f:
        return pickle.load(f)

# Función para realizar la búsqueda híbrida en ChromaDB + BM25
def hybrid_search(query, vector_db):
    #Búsqueda por embeddings
    embedding_results = vector_db.similarity_search(query, k=15)

    #Cargar corpus BM25
    corpus = load_bm25_corpus()
    lemmatized_texts = corpus["lemmatized"]
    original_texts = corpus["originals"]
    sources = corpus["sources"]
    ids = corpus["ids"]

    #Preparar BM25
    tokenized_docs = [doc.split() for doc in lemmatized_texts]
    bm25 = BM25Okapi(tokenized_docs)

    #Procesar la consulta para BM25
    lemmatized_query = clean_text(query)
    bm25_ranking = bm25.get_top_n(lemmatized_query.split(), lemmatized_texts, n=10)

    #Recuperar los textos originales correspondientes
    bm25_documents = []
    for doc_text in bm25_ranking:
        idx = lemmatized_texts.index(doc_text)
        bm25_documents.append(Document(
            page_content=original_texts[idx],
            metadata={"id": ids[idx], "source": sources[idx]}
        ))

    #Fusionar resultados sin duplicados
    all_documents = embedding_results + bm25_documents
    unique_docs = {doc.metadata.get("id", doc.page_content): doc for doc in all_documents}

    return list(unique_docs.values())
