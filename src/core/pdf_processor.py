import os
import re
import hashlib
import unicodedata
import fitz  # PyMuPDF
import pytesseract
import platform
from PIL import Image
import spacy
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import pickle

from core.syllabus_extractor import extract_syllabus, EXTRACTOR_VERSION

# Configurar la ruta de Tesseract en Windows
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

_NLP_MODEL = None
_EMBEDDINGS_INSTANCE = None
_CHROMA_CONNECTION = None

# Directorios
PDF_FOLDER = os.path.join("data", "pdfs")
TEXT_FOLDER = os.path.join("data", "texts")
DB_DIR = "db"
BM25_CORPUS_PATH = "bm25_corpus.pkl"
INDEX_STATE_PATH = "index_state.pkl"
SYLLABUS_SECTION = "temario"

# Crear directorios si no existen
os.makedirs(TEXT_FOLDER, exist_ok=True)

#Cargar el modelo de lenguaje de spaCy
def get_nlp_model():
    global _NLP_MODEL
    if _NLP_MODEL is None:
        try:
            _NLP_MODEL = spacy.load("es_core_news_sm")
        except OSError:
            raise Exception("Modelo spaCy no instalado. Ejecuta: python -m spacy download es_core_news_sm")
    return _NLP_MODEL

def get_embeddings():
    global _EMBEDDINGS_INSTANCE
    if _EMBEDDINGS_INSTANCE is None:
        _EMBEDDINGS_INSTANCE = OpenAIEmbeddings(api_key=os.getenv("API_KEY"))
    return _EMBEDDINGS_INSTANCE

def get_chroma_connection():
    global _CHROMA_CONNECTION
    if _CHROMA_CONNECTION is None:
        _CHROMA_CONNECTION = Chroma(
            persist_directory=DB_DIR,
            embedding_function=get_embeddings()
        )
    return _CHROMA_CONNECTION


def normalize_text(text):
    # Reemplazar caracteres invisibles
    text = re.sub(r'[\u2028\u2029]', '', text)

    # Dividir en líneas
    lines = text.splitlines()

    # Unir líneas que no terminan en punto, dos puntos, etc. Asumimos que esas deben continuar
    normalized_lines = []
    current_line = ""

    for line in lines:
        line = line.strip()
        if not line:
            if current_line:
                normalized_lines.append(current_line.strip())
                current_line = ""
            continue

        if current_line:
            if re.match(r'.*[\.\:\;\?\!]$', current_line):
                normalized_lines.append(current_line.strip())
                current_line = line
            else:
                current_line += " " + line
        else:
            current_line = line

    if current_line:
        normalized_lines.append(current_line.strip())

    return "\n\n".join(normalized_lines)


def extract_text_from_pdf(pdf_path):
    """ Extrae texto de un PDF, usando OCR si es necesario. """
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        extracted_text = page.get_text("text")
        if extracted_text.strip():
            text += extracted_text + "\n"
        else:
            # Si no hay texto, aplicar OCR a la imagen renderizada
            print(f"Aplicando OCR al documento {pdf_path}")
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img, lang="spa") + "\n"

    
    text = normalize_text(text)

    return text.strip()


# Los microcurrículos de Univalle presentan el temario dentro de una tabla
# "DESARROLLO DEL CURSO" con columnas del tipo COMPETENCIA / RESULTADO DE
# APRENDIZAJE / INDICADORES DE LOGRO / CONTENIDO (o EJES/LÍNEAS TEMÁTICAS).
# `page.get_text("text")` aplana esas columnas en un solo párrafo por fila,
# por lo que los indicadores de logro y los contenidos temáticos terminan
# concatenados sin ningún separador confiable. Estas palabras identifican la
# columna que sí corresponde a contenidos/temas (nunca a RA ni indicadores).
CONTENT_COLUMN_HEADER_KEYWORDS = ("contenido", "ejes", "linea tematica", "lineas tematicas")
MAX_HEADER_ROW_SEARCH = 5


def _normalize_cell_text(text):
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return normalized.lower()


def _find_content_column_in_row(row):
    for index, cell in enumerate(row):
        normalized = _normalize_cell_text(cell).replace("\n", " ")
        if any(keyword in normalized for keyword in CONTENT_COLUMN_HEADER_KEYWORDS):
            return index
    return None


def _looks_like_evaluation_table(row):
    """Detecta la tabla de ponderación de evaluación (Resultado de aprendizaje /
    Actividades evaluativas / Porcentaje...), que en algunos microcurrículos
    tiene el mismo número de columnas que la tabla "DESARROLLO DEL CURSO" y
    seguiría a esta sin encabezado propio detectable, para no arrastrarle por
    error el índice de columna de contenidos."""
    joined = " ".join(
        _normalize_cell_text(cell).replace("\n", " ") for cell in row if cell
    )
    return "actividad" in joined and "evaluativ" in joined


def _split_cell_into_topics(cell_text):
    """Divide el texto de una celda en temas individuales usando los puntos
    como separador de oración, cuando existen. Si la celda no trae puntos
    (algunos microcurrículos no los usan), se conserva como un único tema en
    vez de partirla arbitrariamente."""
    cleaned = " ".join(cell_text.split())
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.\!\?])\s+(?=[A-ZÁÉÍÓÚÑ0-9])", cleaned)
    return [part.strip() for part in parts if len(part.strip()) > 2]


def extract_topics_from_tables(pdf_path):
    """Extrae los temas/contenidos oficiales leyendo directamente la columna
    "CONTENIDO"/"EJES O LÍNEAS TEMÁTICAS" de la tabla "DESARROLLO DEL CURSO"
    del PDF, en vez de derivarlos del texto plano ya aplanado.

    Esto evita que los "indicadores de logro"/"resultados de aprendizaje"
    (columnas distintas de la misma fila) se mezclen con los contenidos
    temáticos reales de la asignatura.

    Devuelve una lista de temas sin duplicados, en orden de aparición, o una
    lista vacía si el PDF no tiene una tabla con esa columna (p. ej. PDFs
    escaneados sin texto/tabla real, donde se usa el flujo con OCR).
    """
    topics = []
    seen = set()

    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return topics

    # Algunas tablas "DESARROLLO DEL CURSO" continúan en la página siguiente
    # sin repetir la fila de encabezado de columnas. Arrastramos el índice de
    # columna de contenidos detectado a la última tabla que sí lo mostró,
    # hasta toparnos con una tabla que claramente sea otra cosa (p. ej. la
    # tabla de ponderación de evaluación).
    active_content_column = None

    try:
        for page in doc:
            try:
                found_tables = page.find_tables()
            except Exception:
                continue

            for table in found_tables.tables:
                try:
                    rows = table.extract()
                except Exception:
                    continue
                if not rows:
                    continue

                if any(_looks_like_evaluation_table(row) for row in rows[:2]):
                    active_content_column = None
                    continue

                header_row_index = None
                content_column = None
                for row_index, row in enumerate(rows[:MAX_HEADER_ROW_SEARCH]):
                    column = _find_content_column_in_row(row)
                    if column is not None:
                        header_row_index = row_index
                        content_column = column
                        break

                if content_column is not None:
                    active_content_column = content_column
                    data_rows = rows[header_row_index + 1:]
                elif active_content_column is not None:
                    content_column = active_content_column
                    data_rows = rows
                else:
                    continue

                for row in data_rows:
                    if content_column >= len(row):
                        continue
                    cell = row[content_column]
                    if not cell:
                        continue
                    for topic in _split_cell_into_topics(cell):
                        if topic in seen:
                            continue
                        seen.add(topic)
                        topics.append(topic)
    finally:
        doc.close()

    return topics


def extract_subject_from_source(source_name):
    parts = source_name.split("/")
    if parts and parts[0].lower() == "microcurriculos":
        # Devuelve el nombre del archivo (último elemento) como nombre de asignatura,
        # independientemente de si hay subcarpetas de semestre intermedias.
        return parts[-1] if len(parts) > 1 else "microcurriculos"
    if len(parts) > 1:
        return parts[0]
    return os.path.splitext(os.path.basename(source_name))[0]


def load_index_state():
    if os.path.exists(INDEX_STATE_PATH):
        with open(INDEX_STATE_PATH, "rb") as file:
            return pickle.load(file)
    return {}


def save_index_state(state):
    with open(INDEX_STATE_PATH, "wb") as file:
        pickle.dump(state, file)


def migrate_index_state(index_state):
    migrated = False
    for source_name, entry in list(index_state.items()):
        if isinstance(entry, str):
            index_state[source_name] = {"hash": entry, "has_temario": None}
            migrated = True
    return migrated


def compute_text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ensure_corpus_shape(corpus):
    defaults = {
        "originals": [],
        "lemmatized": [],
        "ids": [],
        "sources": [],
        "subjects": [],
        "sections": [],
    }
    for key, default in defaults.items():
        if key not in corpus:
            corpus[key] = list(default)
    if len(corpus["sections"]) < len(corpus["ids"]):
        corpus["sections"].extend([""] * (len(corpus["ids"]) - len(corpus["sections"])))
    return corpus


def remove_source_from_index(collection, corpus, source_name):
    try:
        stored = collection.get(where={"source": source_name})
        ids_to_delete = stored.get("ids", [])
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
    except Exception as exc:
        print(f"No se pudo eliminar índice previo de {source_name}: {exc}")

    corpus = ensure_corpus_shape(corpus)
    keep_indices = [index for index, source in enumerate(corpus["sources"]) if source != source_name]
    filtered = {}
    for key in ["originals", "lemmatized", "ids", "sources", "subjects", "sections"]:
        filtered[key] = [corpus[key][index] for index in keep_indices]
    return filtered


def normalize_index_entry(entry):
    if isinstance(entry, str):
        return {"hash": entry, "has_temario": None}
    if isinstance(entry, dict):
        return entry
    return {}


def source_is_indexed(collection, source_name, index_entry):
    stored_hash = index_entry.get("hash")
    if not stored_hash:
        return False

    try:
        stored = collection.get(where={"source": source_name}, include=["metadatas"])
        chunk_ids = stored.get("ids") or []
        metadatas = stored.get("metadatas") or []
    except Exception:
        return False

    if not chunk_ids:
        return False

    if index_entry.get("has_temario"):
        meta_ids = {meta.get("id") for meta in metadatas if meta}
        return f"{source_name}_temario" in meta_ids

    return True


def needs_reindex_for_source(collection, source_name, text_hash, index_state, text, subject_name, pdf_path=None):
    index_entry = normalize_index_entry(index_state.get(source_name))
    if index_entry.get("hash") != text_hash:
        return True

    # Re-indexar si el extractor mejoró: puede haber cambiado el contenido del
    # temario ya extraído (no solo su presencia/ausencia), como ocurrió al
    # pasar de heurísticas de texto plano a lectura directa de la tabla.
    stored_version = index_entry.get("extractor_version", 0)
    if stored_version < EXTRACTOR_VERSION:
        return True

    if source_is_indexed(collection, source_name, index_entry):
        return False

    # Compatibilidad: entradas antiguas sin metadata de temario
    if index_entry.get("has_temario") is None:
        table_topics = extract_topics_from_tables(pdf_path) if pdf_path else []
        syllabus = extract_syllabus(text, subject_name, table_topics=table_topics)
        index_entry["has_temario"] = bool(syllabus)
        if source_is_indexed(collection, source_name, index_entry):
            index_state[source_name] = {**index_entry, "hash": text_hash, "extractor_version": EXTRACTOR_VERSION}
            return False

    return True


def lemmatize_chunk(nlp, chunk):
    doc = nlp(chunk)
    return " ".join([token.lemma_ for token in doc if not token.is_stop])


def index_document_chunks(collection, corpus, nlp, source_name, subject_name, text, pdf_path=None):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
    chunks = text_splitter.split_text(text)
    table_topics = extract_topics_from_tables(pdf_path) if pdf_path else []
    syllabus = extract_syllabus(text, subject_name, table_topics=table_topics)

    entries = [(index, chunk, "") for index, chunk in enumerate(chunks)]
    if syllabus:
        entries.append(("temario", syllabus, SYLLABUS_SECTION))

    documents_to_add = []
    for index, chunk, section in entries:
        if index == "temario":
            chunk_id = f"{source_name}_temario"
        else:
            chunk_id = f"{source_name}_{index}"

        metadata = {
            "source": source_name,
            "subject": subject_name,
            "id": chunk_id,
            "section": section,
        }
        documents_to_add.append(Document(page_content=chunk, metadata=metadata))

        corpus["originals"].append(chunk)
        corpus["lemmatized"].append(lemmatize_chunk(nlp, chunk))
        corpus["ids"].append(chunk_id)
        corpus["sources"].append(source_name)
        corpus["subjects"].append(subject_name)
        corpus["sections"].append(section)

    if documents_to_add:
        chunk_ids = [doc.metadata["id"] for doc in documents_to_add]
        collection.add_documents(documents_to_add, ids=chunk_ids)

    return bool(syllabus)


def process_pdfs():
    """ Procesa los PDFs, extrae texto si no existe y almacena en ChromaDB. """

    nlp = get_nlp_model()
    collection = get_chroma_connection()
    index_state = load_index_state()
    state_migrated = migrate_index_state(index_state)

    if os.path.exists(BM25_CORPUS_PATH):
        with open(BM25_CORPUS_PATH, "rb") as file:
            existing_corpus = pickle.load(file)
    else:
        existing_corpus = {
            "originals": [],
            "lemmatized": [],
            "ids": [],
            "sources": [],
            "subjects": [],
            "sections": [],
        }

    existing_corpus = ensure_corpus_shape(existing_corpus)
    if "subjects" not in existing_corpus or not existing_corpus["subjects"]:
        existing_corpus["subjects"] = [
            extract_subject_from_source(source) for source in existing_corpus["sources"]
        ]

    initial_len = len(existing_corpus["ids"])
    corpus_changed = False

    for root, _, files in os.walk(PDF_FOLDER):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(root, file)
            relative_pdf_path = os.path.relpath(pdf_path, PDF_FOLDER)
            source_name = os.path.splitext(relative_pdf_path)[0].replace("\\", "/")
            subject_name = extract_subject_from_source(source_name)

            text_relative_path = os.path.splitext(relative_pdf_path)[0] + ".txt"
            text_file = os.path.join(TEXT_FOLDER, text_relative_path)
            os.makedirs(os.path.dirname(text_file), exist_ok=True)

            if not os.path.exists(text_file):
                print(f"Extrayendo texto del documento {pdf_path}")
                text = extract_text_from_pdf(pdf_path)
                with open(text_file, "w", encoding="utf-8") as file_handle:
                    file_handle.write(text)
            else:
                with open(text_file, "r", encoding="utf-8") as file_handle:
                    text = file_handle.read()

            text_hash = compute_text_hash(text)
            if not needs_reindex_for_source(
                collection, source_name, text_hash, index_state, text, subject_name, pdf_path=pdf_path
            ):
                entry = normalize_index_entry(index_state.get(source_name))
                if entry.get("has_temario") is None:
                    table_topics = extract_topics_from_tables(pdf_path)
                    index_state[source_name] = {
                        "hash": text_hash,
                        "has_temario": bool(extract_syllabus(text, subject_name, table_topics=table_topics)),
                    }
                    state_migrated = True
                continue

            print(f"Indexando documento: {source_name}")
            existing_corpus = remove_source_from_index(collection, existing_corpus, source_name)
            has_temario = index_document_chunks(
                collection, existing_corpus, nlp, source_name, subject_name, text, pdf_path=pdf_path
            )
            index_state[source_name] = {
                "hash": text_hash,
                "has_temario": has_temario,
                "extractor_version": EXTRACTOR_VERSION,
            }
            corpus_changed = True

    if corpus_changed or state_migrated:
        save_index_state(index_state)

    if corpus_changed:
        with open(BM25_CORPUS_PATH, "wb") as file:
            pickle.dump(existing_corpus, file)
        try:
            from core.query_processor import invalidate_search_cache
            invalidate_search_cache()
        except ImportError:
            pass

    if len(existing_corpus["ids"]) > initial_len or corpus_changed:
        print("Procesamiento de documentos finalizado.")
    elif os.path.exists(DB_DIR) and os.listdir(DB_DIR):
        print("Se encontró una base de datos existente")
    else:
        print("Procesamiento de documentos finalizado. Base de datos creada.")
