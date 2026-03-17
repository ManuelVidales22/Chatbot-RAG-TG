import spacy
import os
import pickle
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


def expand_academic_query(query):
    normalized_query = query.lower()
    extra_terms = []

    if any(term in normalized_query for term in ["contenido", "contenidos"]):
        extra_terms.extend(["temas", "subtemas", "unidades", "microcurriculo"])

    if any(term in normalized_query for term in ["tema", "temas"]):
        extra_terms.extend(["contenidos", "subtemas", "unidades", "microcurriculo"])

    if any(term in normalized_query for term in ["subtema", "subtemas"]):
        extra_terms.extend(["temas", "contenidos", "unidades", "microcurriculo"])

    if not extra_terms:
        return query

    expanded_terms = " ".join(dict.fromkeys(extra_terms))
    return f"{query} {expanded_terms}"

#Cargar el corpus de BM25
def load_bm25_corpus():
    with open(BM25_CORPUS_PATH, "rb") as f:
        return pickle.load(f)

#|
# identificar la materia/tema de cada documento
# Analiza la consulta del susuario 
# Calcula el puntaje para cada tema basado en la posición de los documentos relacionados en los resultados de búsqueda 
# y filtra los documentos para mantener solo aquellos que pertenecen al tema más relevante para la consulta.
 
def extract_subject_from_source(source_name):
    parts = source_name.split("/")
    if len(parts) > 1:
        return parts[0]
    return os.path.splitext(os.path.basename(source_name))[0]


def normalize_label(text):
    return text.replace("_", " ").replace("-", " ").strip().lower()


def choose_target_subject(query, documents):
    subject_scores = {}
    normalized_query = normalize_label(query)

    for position, doc in enumerate(documents):
        source = doc.metadata.get("source", "")
        subject = doc.metadata.get("subject") or extract_subject_from_source(source)
        score = max(1, len(documents) - position)

        if normalize_label(subject) in normalized_query:
            score += len(documents)

        subject_scores[subject] = subject_scores.get(subject, 0) + score

    if not subject_scores:
        return None

    return max(subject_scores, key=subject_scores.get)


def filter_documents_by_subject(query, documents):
    target_subject = choose_target_subject(query, documents)
    if not target_subject:
        return []

    filtered_documents = []
    for doc in documents:
        source = doc.metadata.get("source", "")
        subject = doc.metadata.get("subject") or extract_subject_from_source(source)
        if subject == target_subject:
            doc.metadata["subject"] = subject
            filtered_documents.append(doc)

    return filtered_documents

# Función para realizar la búsqueda híbrida en ChromaDB + BM25
def hybrid_search(query, vector_db):
    expanded_query = expand_academic_query(query)

    #Búsqueda por embeddings
    embedding_results = vector_db.similarity_search(expanded_query, k=15)

    #Cargar corpus BM25
    corpus = load_bm25_corpus()
    lemmatized_texts = corpus["lemmatized"]
    original_texts = corpus["originals"]
    sources = corpus["sources"]
    ids = corpus["ids"]
    subjects = corpus.get("subjects", [extract_subject_from_source(source) for source in sources])

    #Preparar BM25
    tokenized_docs = [doc.split() for doc in lemmatized_texts]
    bm25 = BM25Okapi(tokenized_docs)

    #Procesar la consulta para BM25
    lemmatized_query = clean_text(expanded_query)
    bm25_ranking = bm25.get_top_n(lemmatized_query.split(), lemmatized_texts, n=10)

    #Recuperar los textos originales correspondientes
    bm25_documents = []
    for doc_text in bm25_ranking:
        idx = lemmatized_texts.index(doc_text)
        bm25_documents.append(Document(
            page_content=original_texts[idx],
            metadata={"id": ids[idx], "source": sources[idx], "subject": subjects[idx]}
        ))

    #Fusionar resultados sin duplicados
    all_documents = embedding_results + bm25_documents
    unique_docs = {}
    for doc in all_documents:
        source = doc.metadata.get("source", "")
        doc.metadata["subject"] = doc.metadata.get("subject") or extract_subject_from_source(source)
        unique_docs[doc.metadata.get("id", doc.page_content)] = doc

    filtered_docs = filter_documents_by_subject(expanded_query, list(unique_docs.values()))
    return filtered_docs[:8]
