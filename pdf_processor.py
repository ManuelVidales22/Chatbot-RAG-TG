import os
import re
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

# Configurar la ruta de Tesseract en Windows
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

_NLP_MODEL = None
_EMBEDDINGS_INSTANCE = None
_CHROMA_CONNECTION = None

# Directorios
PDF_FOLDER = "pdfs"
TEXT_FOLDER = "texts"
DB_DIR = "db"
BM25_CORPUS_PATH = "bm25_corpus.pkl"

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


def process_pdfs():
    """ Procesa los PDFs, extrae texto si no existe y almacena en ChromaDB solo los nuevos. """

    nlp = get_nlp_model()

    # Crear conexión con ChromaDB
    collection = get_chroma_connection()

    for file in os.listdir(PDF_FOLDER):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, file)
            base_name = os.path.splitext(file)[0]

            # Ruta de los archivos de texto
            text_file = os.path.join(TEXT_FOLDER, f"{base_name}.txt")

            # Si el texto no ha sido extraído, extraerlo y guardarlo
            if not os.path.exists(text_file):
                print(f"Extrayendo texto del documento {pdf_path}")
                text = extract_text_from_pdf(pdf_path)
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(text)
            else:
                with open(text_file, "r", encoding="utf-8") as f:
                    text = f.read()

            # Dividir el texto en fragmentos
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
            chunks = text_splitter.split_text(text)

            # Verificar qué fragmentos ya están en la base de datos
            existing_ids = {metadata["id"] for metadata in collection.get()["metadatas"]}

            if os.path.exists(BM25_CORPUS_PATH):
                with open(BM25_CORPUS_PATH, "rb") as f:
                    existing_corpus = pickle.load(f)
            else:
                existing_corpus = {
                    "originals": [],
                    "lemmatized": [],
                    "ids": [],
                    "sources": []
                }

            existing_ids_set = set(existing_corpus["ids"])
            initial_len = len(existing_corpus["ids"])

            # Almacenar solo los fragmentos nuevos en ChromaDB y crear el corpus para BM25
            for i, chunk in enumerate(chunks):
                chunk_id = f"{base_name}_{i}"
                if chunk_id not in existing_ids and chunk_id not in existing_ids_set:
                    collection.add_documents([Document(page_content=chunk, metadata={"source": base_name, "id": chunk_id})])

                    # Lematizar para BM25
                    doc = nlp(chunk)
                    lemmatized = " ".join([token.lemma_ for token in doc if not token.is_stop])
                    
                    existing_corpus["originals"].append(chunk)
                    existing_corpus["lemmatized"].append(lemmatized)
                    existing_corpus["ids"].append(chunk_id)
                    existing_corpus["sources"].append(base_name)


            if len(existing_corpus["ids"]) > initial_len:
                with open(BM25_CORPUS_PATH, "wb") as f:
                    pickle.dump(existing_corpus, f)

    # Si ya existe la base de datos, no procesar nuevamente
    if os.path.exists(DB_DIR) and os.listdir(DB_DIR):
        print("Se encontró una base de datos existente")
        return

    print("Procesamiento de documentos finalizado. Base de datos creada.")