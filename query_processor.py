import spacy
import os
from langchain_openai import ChatOpenAI
from rank_bm25 import BM25Okapi
from collections import Counter
from langchain.schema import Document

# Cargar modelo de spaCy para español
nlp = spacy.load("es_core_news_sm")

# Función para limpiar y lematizar la consulta
def clean_text(query):
    doc = nlp(query)
    clean_words = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(clean_words)

# Expansión de consulta
def expand_query(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("API_KEY"))
    prompt = f"Expande esta consulta agregando sinónimos y términos relacionados: {query}"
    return llm.invoke(prompt).content

# Ponderar palabras clave en la consulta
def weight_keywords(query):
    words = query.split()
    word_count = Counter(words)
    weighted_query = " ".join([word * (word_count[word] + 1) for word in words])
    return weighted_query

# Función para realizar la búsqueda híbrida en ChromaDB + BM25
def hybrid_search(query, vector_db):
    # Paso 1: Procesar la consulta
    cleaned_query = clean_text(query)
    expanded_query = expand_query(cleaned_query)
    
    # Paso 2: Búsqueda en ChromaDB (Embeddings)
    embedding_results = vector_db.similarity_search(expanded_query, k=15)
    
    # Paso 3: Búsqueda con BM25
    document_texts = [doc.page_content for doc in embedding_results]  # Extraer texto
    tokenized_docs = [doc.split() for doc in document_texts]
    bm25 = BM25Okapi(tokenized_docs)
    bm25_results = bm25.get_top_n(expanded_query.split(), document_texts, n=10)
    
    # Convertir resultados de BM25 a objetos Document
    bm25_results = [Document(page_content=text) for text in bm25_results]

    # Paso 4: Fusionar resultados sin duplicados
    # Crear un diccionario para eliminar duplicados basándose en el contenido del documento
    unique_documents = {doc.page_content: doc for doc in embedding_results + bm25_results}
    final_documents = list(unique_documents.values())  # Convertir de nuevo a lista

    
    return final_documents
