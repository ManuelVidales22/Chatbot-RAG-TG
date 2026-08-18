import re
import unicodedata
import spacy
import os
import pickle
from rank_bm25 import BM25Okapi
from langchain.schema import Document

_NLP_MODEL = None
_BM25_INDEX = None
_BM25_CORPUS_MTIME = None
_LEMMATIZED_INDEX_MAP = None

#Ruta del corpus de BM25
BM25_CORPUS_PATH = "bm25_corpus.pkl"
SYLLABUS_SECTION = "temario"
SUBTOPIC_PATTERN = re.compile(r"\b\d+\.\d+\b")
DEFAULT_RESULT_LIMIT = 8
SYLLABUS_RESULT_LIMIT = 12

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

SYLLABUS_LISTING_TERMS = (
    "contenido",
    "contenidos",
    "temario",
    "tema",
    "temas",
    "subtema",
    "subtemas",
    "unidad",
    "unidades",
    "eje tematico",
    "ejes tematicos",
    "que se ve",
    "que ven",
    "que trata",
    "que temas",
    "cuales son los temas",
    "cuales son los contenidos",
)

ADMIN_INFO_TERMS = (
    "credito",
    "creditos",
    "horas",
    "hora",
    "prerequisito",
    "prerrequisito",
    "prerequisitos",
    "prerrequisitos",
    "correquisito",
    "correquisitos",
    "validable",
    "habilitable",
    "tipo de asignatura",
    "asignatura basica",
    "asignatura profesional",
    "asignatura electiva",
    "obligatoria",
    "electiva",
    "descripcion",
    "descripcion del curso",
    "descripcion general",
    "informacion basica",
    "informacion de la asignatura",
    "cuantos creditos",
    "cuantas horas",
    "presencial",
    "independiente",
    "trabajo independiente",
    "formacion general",
    "quien dicta",
    "que facultad",
    "unidad academica",
    "programa academico",
)

EXPLANATION_TERMS = (
    "explica",
    "explicar",
    "explicame",
    "define",
    "definir",
    "definicion",
    "profundiza",
    "profundizar",
    "como funciona",
    "ejemplo",
    "ejemplos",
    "desarrolla el tema",
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
    # Quitar signos de puntuación (?, ¿, ., ,, etc.) para que no queden pegados
    # a la última palabra de una oración y rompan las comparaciones por token.
    normalized_text = re.sub(r"[^\w\s]", " ", normalized_text)
    normalized_text = re.sub(r"\s+", " ", normalized_text)
    return normalized_text.strip()


def contains_academic_structure_terms(text):
    normalized_text = normalize_label(text)
    return any(term in normalized_text for term in ACADEMIC_STRUCTURE_TERMS)


def is_syllabus_listing_query(query):
    normalized_query = normalize_label(query)
    has_listing = any(term in normalized_query for term in SYLLABUS_LISTING_TERMS)
    if not has_listing:
        return False

    has_explanation = any(term in normalized_query for term in EXPLANATION_TERMS)
    has_catalog_phrase = any(
        phrase in normalized_query
        for phrase in [
            "contenidos de",
            "contenido de",
            "temas de",
            "temario de",
            "subtemas de",
            "que contenidos",
            "que temas",
            "dime los contenidos",
            "dime que contenidos",
            "dime los temas",
            "dime que temas",
            "lista de contenidos",
            "lista de temas",
        ]
    )

    if has_explanation and not has_catalog_phrase:
        return False
    return True


def count_subtopics(text):
    return len(SUBTOPIC_PATTERN.findall(text))


def is_admin_info_query(query):
    """Devuelve True cuando la consulta pregunta por datos administrativos de una asignatura."""
    normalized_query = normalize_label(query)
    return any(term in normalized_query for term in ADMIN_INFO_TERMS)


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

    if is_syllabus_listing_query(query):
        extra_terms.extend(["contenidos tematicos", "1.1", "2.1", "subtemas", "temario"])

    if is_admin_info_query(query):
        extra_terms.extend(["creditos", "horas de trabajo", "informacion basica", "codigo", "microcurriculo"])

    if not extra_terms:
        return query

    expanded_terms = " ".join(dict.fromkeys(extra_terms))
    return f"{query} {expanded_terms}"

#Cargar el corpus de BM25
def load_bm25_corpus():
    with open(BM25_CORPUS_PATH, "rb") as f:
        corpus = pickle.load(f)
    if "sections" not in corpus:
        corpus["sections"] = [""] * len(corpus.get("ids", []))
    return corpus


def invalidate_search_cache():
    global _BM25_INDEX, _BM25_CORPUS_MTIME, _LEMMATIZED_INDEX_MAP
    _BM25_INDEX = None
    _BM25_CORPUS_MTIME = None
    _LEMMATIZED_INDEX_MAP = None


def get_bm25_resources(corpus):
    global _BM25_INDEX, _BM25_CORPUS_MTIME, _LEMMATIZED_INDEX_MAP

    corpus_mtime = (
        os.path.getmtime(BM25_CORPUS_PATH)
        if os.path.exists(BM25_CORPUS_PATH)
        else 0
    )
    if _BM25_INDEX is None or _BM25_CORPUS_MTIME != corpus_mtime:
        lemmatized_texts = corpus["lemmatized"]
        tokenized_docs = [doc.split() for doc in lemmatized_texts]
        _BM25_INDEX = BM25Okapi(tokenized_docs)
        _LEMMATIZED_INDEX_MAP = {
            text: index for index, text in enumerate(lemmatized_texts)
        }
        _BM25_CORPUS_MTIME = corpus_mtime

    return _BM25_INDEX, _LEMMATIZED_INDEX_MAP

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


STOP_WORDS = {
    "de", "y", "la", "el", "los", "las", "en", "a", "del", "al", "o", "un", "una",
    "con", "por", "para", "que", "su", "se", "e",
}

# Numerales romanos usados para distinguir asignaturas homónimas del mismo nombre
# base (ej. "Desarrollo de Software I/II/III", "Proyecto Integrador I/II").
# OJO: NO deben tratarse como stopwords ni descartarse por longitud corta, porque
# son precisamente la parte del nombre que distingue una asignatura de otra.
ROMAN_NUMERAL_WORDS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}


def _strip_subject_code(normalized_subject):
    """Elimina el código de asignatura (ej. "750012c", "111023c") del inicio del nombre."""
    return re.sub(r"^\d+\w*\s*", "", normalized_subject)


def _split_trailing_numeral(words):
    """Separa un numeral romano final (I, II, III, ...) del resto de las palabras.

    Devuelve (palabras_base, numeral_o_None).
    """
    if words and words[-1] in ROMAN_NUMERAL_WORDS:
        return words[:-1], words[-1]
    return words, None


def _subject_matches_query(normalized_subject, normalized_query):
    """Devuelve True si el nombre de la asignatura tiene coincidencia significativa con la consulta.

    Compara las palabras clave del nombre de la asignatura (sin stopwords y sin el
    código numérico inicial) contra la consulta. Si el nombre termina en un numeral
    romano (asignaturas homónimas como "... I" / "... II" / "... III"), exige que la
    consulta mencione ese mismo numeral explícitamente, para no confundir asignaturas
    con nombre base idéntico pero numeral distinto.
    """
    subject_words = _strip_subject_code(normalized_subject).split()
    base_words, subject_numeral = _split_trailing_numeral(subject_words)
    meaningful_words = [w for w in base_words if w not in STOP_WORDS and len(w) > 2]

    if not meaningful_words:
        return False

    query_words = normalized_query.split()
    query_words_set = set(query_words)

    if subject_numeral is None:
        return all(w in query_words_set for w in meaningful_words)

    query_numerals = {w for w in query_words if w in ROMAN_NUMERAL_WORDS}
    if subject_numeral not in query_numerals:
        return False

    # Asignaturas homónimas: el numeral ya distingue sin ambigüedad esta asignatura
    # de sus hermanas (mismo nombre base, distinto numeral), así que no exigimos que
    # la consulta mencione TODAS las palabras del nombre completo. Nombres largos
    # como "Inglés con fines generales y académicos II" rara vez se escriben así;
    # basta con que la consulta incluya al menos una palabra significativa del
    # nombre (ej. "ingles") junto con el numeral correcto (ej. "ingles ii").
    return any(w in query_words_set for w in meaningful_words)


def get_known_subjects(corpus):
    return list(dict.fromkeys(corpus.get("subjects", [])))


def detect_explicit_subject(query, corpus):
    """Busca coincidencia de asignatura contra TODO el catálogo (no solo contra los
    documentos ya recuperados por embeddings/BM25). Esto es necesario porque una
    consulta con solo el nombre de la asignatura (sin código) puede no rankear bien
    frente a otras asignaturas con vocabulario similar, dejando la asignatura correcta
    fuera del top-k antes de que 'choose_target_subject' pueda considerarla siquiera.
    """
    normalized_query = normalize_label(query)
    matches = [
        subject for subject in get_known_subjects(corpus)
        if _subject_matches_query(normalize_label(subject), normalized_query)
    ]
    if not matches:
        return None
    # Si varios nombres coinciden (uno es subcadena de otro), preferir el más específico.
    return max(matches, key=lambda subject: len(normalize_label(subject)))


def choose_target_subject(query, documents):
    subject_scores = {}
    normalized_query = normalize_label(query)
    explicit_subject_match = False

    for position, doc in enumerate(documents):
        source = doc.metadata.get("source", "")
        subject = doc.metadata.get("subject") or extract_subject_from_source(source)
        score = max(1, len(documents) - position)

        if _subject_matches_query(normalize_label(subject), normalized_query):
            score += len(documents)
            explicit_subject_match = True

        subject_scores[subject] = subject_scores.get(subject, 0) + score

    if not subject_scores:
        return None

    return max(subject_scores, key=subject_scores.get)


def build_document_from_corpus(corpus, index):
    sections = corpus.get("sections", [])
    section = sections[index] if index < len(sections) else ""
    source = corpus["sources"][index]
    return Document(
        page_content=corpus["originals"][index],
        metadata={
            "id": corpus["ids"][index],
            "source": source,
            "subject": corpus["subjects"][index],
            "section": section,
        },
    )


def get_temario_documents_for_subject(corpus, target_subject):
    documents = []
    sections = corpus.get("sections", [])
    for index, subject in enumerate(corpus.get("subjects", [])):
        section = sections[index] if index < len(sections) else ""
        if subject == target_subject and section == SYLLABUS_SECTION:
            documents.append(build_document_from_corpus(corpus, index))
    return documents


def syllabus_document_score(doc):
    score = 0
    if doc.metadata.get("section") == SYLLABUS_SECTION:
        score += 1000
    score += count_subtopics(doc.page_content) * 20
    if contains_academic_structure_terms(doc.page_content):
        score += 50
    if "contenidos tematicos" in normalize_label(doc.page_content):
        score += 100
    return score


def rank_documents_for_syllabus(documents):
    return sorted(documents, key=syllabus_document_score, reverse=True)


def merge_unique_documents(primary_docs, secondary_docs):
    merged = []
    seen_ids = set()
    for doc in primary_docs + secondary_docs:
        doc_id = doc.metadata.get("id", doc.page_content)
        if doc_id in seen_ids:
            continue
        seen_ids.add(doc_id)
        merged.append(doc)
    return merged


def filter_documents_by_subject(query, documents, corpus=None, forced_subject=None):
    target_subject = forced_subject or choose_target_subject(query, documents)
    if not target_subject:
        return []

    normalized_query = normalize_label(query)
    is_structure_request = is_syllabus_listing_query(query) or any(
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
        # OJO: restringir explícitamente a target_subject aquí (y no solo confiar en que
        # `documents` ya venga filtrado) evita que texto de OTRA asignatura que también
        # contenga palabras como "contenido"/"tema"/"unidad" (algo común a casi todos los
        # microcurrículos) se cuele en la respuesta de listado de temario.
        structure_documents = []
        for doc in documents:
            source = doc.metadata.get("source", "")
            subject = doc.metadata.get("subject") or extract_subject_from_source(source)
            if subject != target_subject:
                continue
            if contains_academic_structure_terms(doc.page_content) or count_subtopics(doc.page_content) >= 3:
                doc.metadata["subject"] = subject
                structure_documents.append(doc)

        temario_documents = []
        if corpus is not None:
            temario_documents = get_temario_documents_for_subject(corpus, target_subject)

        merged_documents = merge_unique_documents(
            temario_documents,
            rank_documents_for_syllabus(structure_documents + filtered_documents),
        )
        return merged_documents

    return filtered_documents

# Función para realizar la búsqueda híbrida en ChromaDB + BM25
def hybrid_search(query, vector_db):
    expanded_query = expand_academic_query(query)
    listing_query = is_syllabus_listing_query(query)
    admin_query = is_admin_info_query(query)
    result_limit = SYLLABUS_RESULT_LIMIT if listing_query else DEFAULT_RESULT_LIMIT

    #Cargar corpus BM25 primero: se necesita el catálogo completo de asignaturas
    #para poder detectar coincidencias explícitas antes de rankear nada.
    corpus = load_bm25_corpus()
    lemmatized_texts = corpus["lemmatized"]
    original_texts = corpus["originals"]
    sources = corpus["sources"]
    ids = corpus["ids"]
    subjects = corpus.get("subjects", [extract_subject_from_source(source) for source in sources])
    sections = corpus.get("sections", [])

    #Si la consulta nombra explícitamente una asignatura conocida (con o sin código),
    #restringimos tanto la búsqueda vectorial como BM25 a esa asignatura, en vez de
    #dejar que la asignatura correcta compita por espacio en el top-k contra las demás.
    explicit_subject = detect_explicit_subject(query, corpus)
    subject_filter = {"subject": explicit_subject} if explicit_subject else None

    #Búsqueda por embeddings
    embedding_results = vector_db.similarity_search(expanded_query, k=15, filter=subject_filter)

    bm25, lemmatized_index_map = get_bm25_resources(corpus)

    #Procesar la consulta para BM25
    lemmatized_query = clean_text(expanded_query)
    tokenized_query = lemmatized_query.split()

    if explicit_subject:
        allowed_indices = [index for index, subject in enumerate(subjects) if subject == explicit_subject]
        bm25_scores = bm25.get_scores(tokenized_query)
        ranked_indices = sorted(allowed_indices, key=lambda index: bm25_scores[index], reverse=True)[:10]
        bm25_documents = [
            Document(
                page_content=original_texts[index],
                metadata={
                    "id": ids[index],
                    "source": sources[index],
                    "subject": subjects[index],
                    "section": sections[index] if index < len(sections) else "",
                },
            )
            for index in ranked_indices
        ]
    else:
        bm25_ranking = bm25.get_top_n(tokenized_query, lemmatized_texts, n=10)
        #Recuperar los textos originales correspondientes
        bm25_documents = []
        for doc_text in bm25_ranking:
            idx = lemmatized_index_map.get(doc_text)
            if idx is None:
                continue
            bm25_documents.append(Document(
                page_content=original_texts[idx],
                metadata={
                    "id": ids[idx],
                    "source": sources[idx],
                    "subject": subjects[idx],
                    "section": sections[idx] if idx < len(sections) else "",
                },
            ))

    #Fusionar resultados sin duplicados
    all_documents = embedding_results + bm25_documents

    # Para consultas administrativas, inyectar los primeros chunks (información básica)
    # de cada microcurrículo que coincida por nombre con la consulta.
    if admin_query:
        normalized_q = normalize_label(query)
        seen_admin_subjects = set()
        admin_docs = []
        corpus_subjects = corpus.get("subjects", [])
        for idx, subject in enumerate(corpus_subjects):
            if subject in seen_admin_subjects:
                continue
            if _subject_matches_query(normalize_label(subject), normalized_q):
                seen_admin_subjects.add(subject)
                # Inyectar los primeros 3 chunks del documento (portada + descripción)
                for offset in range(3):
                    target_idx = idx + offset
                    if target_idx < len(corpus_subjects) and corpus_subjects[target_idx] == subject:
                        admin_docs.append(build_document_from_corpus(corpus, target_idx))
        all_documents = admin_docs + all_documents

    unique_docs = {}
    for doc in all_documents:
        source = doc.metadata.get("source", "")
        doc.metadata["subject"] = doc.metadata.get("subject") or extract_subject_from_source(source)
        unique_docs[doc.metadata.get("id", doc.page_content)] = doc

    filtered_docs = filter_documents_by_subject(
        expanded_query, list(unique_docs.values()), corpus=corpus, forced_subject=explicit_subject
    )
    if listing_query:
        filtered_docs = rank_documents_for_syllabus(filtered_docs)
    return filtered_docs[:result_limit]
