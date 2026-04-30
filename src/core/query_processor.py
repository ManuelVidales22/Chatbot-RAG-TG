import re
import unicodedata
import spacy
import os
import pickle
from rank_bm25 import BM25Okapi
from langchain.schema import Document

_NLP_MODEL = None

#Ruta del corpus de BM25
BM25_CORPUS_PATH = "bm25_corpus.pkl"

ACADEMIC_STRUCTURE_TERMS = (
    "contenido",
    "contenidos",
    "tema",
    "temas",
    "subtema",
    "subtemas",
    "unidad",
    "unidades",
    "eje tematico",
    "ejes tematicos",
    "temario",
    "apartado",
    "apartados",
    "seccion",
    "secciones",
)

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


def normalize_label(text):
    normalized_text = unicodedata.normalize("NFKD", text)
    normalized_text = "".join(character for character in normalized_text if not unicodedata.combining(character))
    normalized_text = normalized_text.replace("_", " ").replace("-", " ").lower()
    normalized_text = re.sub(r"\s+", " ", normalized_text)
    return normalized_text.strip()


def contains_academic_structure_terms(text):
    normalized_text = normalize_label(text)
    return any(term in normalized_text for term in ACADEMIC_STRUCTURE_TERMS)


def expand_academic_query(query):
    normalized_query = normalize_label(query)
    extra_terms = []

    if any(term in normalized_query for term in ["contenido", "contenidos", "temario", "apartado", "seccion"]):
        extra_terms.extend(["tema", "temas", "subtema", "subtemas", "unidad", "unidades", "microcurriculo"])

    if any(term in normalized_query for term in ["tema", "temas", "subtema", "subtemas", "unidad", "unidades"]):
        extra_terms.extend(["contenido", "contenidos", "temario", "apartado", "seccion", "microcurriculo"])

    if any(term in normalized_query for term in ["eje tematico", "ejes tematicos"]):
        extra_terms.extend(["tema", "temas", "contenido", "contenidos", "subtema", "subtemas", "microcurriculo"])

    if any(term in normalized_query for term in ["subtema", "subtemas"]):
        extra_terms.extend(["tema", "temas", "contenido", "contenidos", "unidad", "unidades", "microcurriculo"])

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
    if parts and parts[0].lower() == "microcurriculos":
        # Devuelve el nombre del archivo (último elemento) como nombre de asignatura,
        # independientemente de si hay subcarpetas de semestre intermedias.
        return parts[-1] if len(parts) > 1 else "microcurriculos"
    if len(parts) > 1:
        return parts[0]
    return os.path.splitext(os.path.basename(source_name))[0]


def choose_target_subject(query, documents):
    subject_scores = {}
    normalized_query = normalize_label(query)
    explicit_subject_match = False

    for position, doc in enumerate(documents):
        source = doc.metadata.get("source", "")
        subject = doc.metadata.get("subject") or extract_subject_from_source(source)
        score = max(1, len(documents) - position)

        if normalize_label(subject) in normalized_query:
            score += len(documents)
            explicit_subject_match = True

        subject_scores[subject] = subject_scores.get(subject, 0) + score

    if not subject_scores:
        return None

    if explicit_subject_match:
        return max(subject_scores, key=subject_scores.get)

    return max(subject_scores, key=subject_scores.get)


def filter_documents_by_subject(query, documents):
    target_subject = choose_target_subject(query, documents)
    if not target_subject:
        return []

    normalized_query = normalize_label(query)
    is_structure_request = any(
        term in normalized_query
        for term in ["contenido", "contenidos", "tema", "temas", "subtema", "subtemas", "unidad", "unidades", "eje tematico", "ejes tematicos"]
    )

    filtered_documents = []
    for doc in documents:
        source = doc.metadata.get("source", "")
        subject = doc.metadata.get("subject") or extract_subject_from_source(source)
        if subject == target_subject:
            doc.metadata["subject"] = subject
            filtered_documents.append(doc)

    if is_structure_request:
        structure_documents = []
        for doc in documents:
            if contains_academic_structure_terms(doc.page_content):
                source = doc.metadata.get("source", "")
                doc.metadata["subject"] = doc.metadata.get("subject") or extract_subject_from_source(source)
                structure_documents.append(doc)

        if structure_documents:
            merged_documents = []
            seen_ids = set()

            for doc in structure_documents + filtered_documents:
                doc_id = doc.metadata.get("id", doc.page_content)
                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)
                merged_documents.append(doc)

            return merged_documents[:8]

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
