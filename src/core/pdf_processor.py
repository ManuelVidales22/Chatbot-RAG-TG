import os
import re
import hashlib
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


def needs_reindex_for_source(collection, source_name, text_hash, index_state, text, subject_name):
    index_entry = normalize_index_entry(index_state.get(source_name))
    if index_entry.get("hash") != text_hash:
        return True

    # Re-indexar si el extractor mejoró y el documento no tenía temario extraído
    stored_version = index_entry.get("extractor_version", 0)
    if stored_version < EXTRACTOR_VERSION and not index_entry.get("has_temario"):
        return True

    if source_is_indexed(collection, source_name, index_entry):
        return False

    # Compatibilidad: entradas antiguas sin metadata de temario
    if index_entry.get("has_temario") is None:
        syllabus = extract_syllabus(text, subject_name)
        index_entry["has_temario"] = bool(syllabus)
        if source_is_indexed(collection, source_name, index_entry):
            index_state[source_name] = {**index_entry, "hash": text_hash, "extractor_version": EXTRACTOR_VERSION}
            return False

    return True


def lemmatize_chunk(nlp, chunk):
    doc = nlp(chunk)
    return " ".join([token.lemma_ for token in doc if not token.is_stop])


def index_document_chunks(collection, corpus, nlp, source_name, subject_name, text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
    chunks = text_splitter.split_text(text)
    syllabus = extract_syllabus(text, subject_name)

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
                collection, source_name, text_hash, index_state, text, subject_name
            ):
                entry = normalize_index_entry(index_state.get(source_name))
                if entry.get("has_temario") is None:
                    index_state[source_name] = {
                        "hash": text_hash,
                        "has_temario": bool(extract_syllabus(text, subject_name)),
                    }
                    state_migrated = True
                continue

            print(f"Indexando documento: {source_name}")
            existing_corpus = remove_source_from_index(collection, existing_corpus, source_name)
            has_temario = index_document_chunks(
                collection, existing_corpus, nlp, source_name, subject_name, text
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
