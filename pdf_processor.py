import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

#Configuracion del embedding
embeddings = OpenAIEmbeddings(api_key=os.getenv("API_KEY"))

#Cargar los pdf y almacernar los embeddings en Chroma si no existe la base de datos
def load_process_pdfs(pdf_folder, persist_directory="db"):

    #Si la base de datos ya existe, se carga sin procesar los documentos
    if os.path.exists(persist_directory):
        print("Se encontro una base de datos existente, cargando...")
        return Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    
    print("Procesando los documentos...")

    documents = []

     #Cargar los pdfs
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, file)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())

    #Dividir los documentos en fragmentos de texto
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_documents(documents)

    #Crear la base de datos vectorial con Chroma
    vector_db = Chroma.from_documents(chunks, embeddings, persist_directory=persist_directory)
    vector_db.persist()

    print("Procesamiento de documentos finalizado, base de datos creada")

    return vector_db