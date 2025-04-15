import os
import re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import spacy
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Configurar la ruta de Tesseract en Windows (ajustar si es necesario)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Cargar modelo de spaCy en español
nlp = spacy.load("es_core_news_sm")

# Configuración del embedding
embeddings = OpenAIEmbeddings(api_key=os.getenv("API_KEY"))

# Directorios
PDF_FOLDER = "PDFs"
TEXT_FOLDER = "texts"
SUMMARY_FOLDER = "summaries"
DB_DIR = "db"

# Crear directorios si no existen
os.makedirs(TEXT_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

def normalize_text(text):
    # Reemplazar caracteres invisibles (como \u2028, \u2029)
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


def summarize_text(text):
    """ Resume el texto usando spaCy, conservando el 60% de las oraciones más importantes. """
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    summary_size = max(1, int(len(sentences) * 0.6))  # 60% de las oraciones
    return " ".join(sentences[:summary_size])


def process_pdfs():
    """ Procesa los PDFs, extrae texto si no existe, resume si no existe, y almacena en ChromaDB solo los nuevos. """


    # Crear conexión con ChromaDB
    chroma_client = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    collection = chroma_client

    for file in os.listdir(PDF_FOLDER):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, file)
            base_name = os.path.splitext(file)[0]

            # Rutas de los archivos de texto y resumen
            text_file = os.path.join(TEXT_FOLDER, f"{base_name}.txt")
            summary_file = os.path.join(SUMMARY_FOLDER, f"{base_name}.txt")

            # Si el texto no ha sido extraído, extraerlo y guardarlo
            if not os.path.exists(text_file):
                print(f"Extrayendo texto del documento {pdf_path}")
                text = extract_text_from_pdf(pdf_path)
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(text)
            else:
                with open(text_file, "r", encoding="utf-8") as f:
                    text = f.read()

            # Si el resumen no ha sido generado, resumirlo y guardarlo
            if not os.path.exists(summary_file):
                print(f"Resumiendo el documento {pdf_path}")
                summary = summarize_text(text)
                with open(summary_file, "w", encoding="utf-8") as f:
                    f.write(summary)
            else:
                with open(summary_file, "r", encoding="utf-8") as f:
                    summary = f.read()

            # Dividir el resumen en fragmentos de tamaño 1000 con overlap de 200
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
            chunks = text_splitter.split_text(text)

            # Verificar qué fragmentos ya están en la base de datos
            existing_ids = {metadata["id"] for metadata in collection.get()["metadatas"]}

            # Almacenar solo los fragmentos nuevos en ChromaDB
            for i, chunk in enumerate(chunks):
                chunk_id = f"{base_name}_{i}"
                if chunk_id not in existing_ids:
                    collection.add_documents([Document(page_content=chunk, metadata={"source": base_name, "id": chunk_id})])

    # Si ya existe la base de datos, no procesar nuevamente
    if os.path.exists(DB_DIR) and os.listdir(DB_DIR):
        print("Se encontró una base de datos existente")
        return

    print("Procesamiento de documentos finalizado. Base de datos creada.")