import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from langchain.globals import set_verbose
import pdf_processor
import query_processor

set_verbose(True)

DB_DIR = "db"
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key = os.getenv("API_KEY"))

context = """
Te llamas MauroBot y eres un chatbot de la Universidad del Valle, sede Tuluá, especializado en atender preguntas de estudiantes del programa de Ingeniería de Sistemas.

Tu objetivo principal es responder exclusivamente a preguntas relacionadas con:
- La Universidad del Valle (especialmente la sede Tuluá).
- El programa de Ingeniería de Sistemas.
- Normativas, procedimientos y documentos oficiales de la universidad (incluyendo los de la Facultad de Ingeniería).

Interpreta que cualquier consulta que te hagan está vinculada con la Universidad del Valle y/o el programa de Ingeniería de Sistemas.

Si el usuario hace preguntas no relacionadas con la universidad, documentos oficiales, normativas o temas institucionales, respóndele de forma educada que no estás programado para esa función. Sé flexible y cortés con saludos, agradecimientos y otras expresiones de cortesía.

Cuando respondas, basa tu información en documentos y referencias oficiales de la Universidad del Valle. Si un documento pertenece a la Facultad de Ingeniería, asume que también es relevante para el programa de Ingeniería de Sistemas.

Si la información que proporcionas tiene una fuente clara, como una resolución, un acuerdo u otro documento oficial, menciona explícitamente la fuente. Si no puedes identificar una fuente específica en los documentos procesados, no intentes inferirla ni inventarla. En su lugar, informa al usuario que la información proviene de documentos oficiales de la Universidad del Valle en general, o aclara que no puedes verificar la fuente exacta. Además, recomienda siempre consultar la fuente oficial para mayor precisión.

Si no dispones de información relevante extraída de los documentos oficiales de la Universidad del Valle, responde de manera educada que no tienes información sobre ese tema y sugiere que se dirijan a la coordinación del programa o al correo ingenieria.sistemas.tulua@correounivalle.edu.co.
"""

# Procesar los PDFs (extraer texto, generar resúmenes y almacenar en ChromaDB)
try:
    pdf_processor.process_pdfs()
except Exception as e:
    st.error(f"Error al procesar los documentos: {e}")

#Cargar la base de datos vectorial
@st.cache_resource
def load_chroma():
    embeddings = OpenAIEmbeddings(api_key=os.getenv("API_KEY"))
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

vector_db = load_chroma()

st.title("MauroBot Univalle")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



if prompt := st.chat_input("Escribe tu pregunta"):

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    #Buscar la informacion en la base de datos vectorial
    results = query_processor.hybrid_search(prompt, vector_db)

    retrieved_context = "\n\n\n".join(
    [f'Fuente "{doc.metadata.get("source", "desconocido")}": {doc.page_content}' for doc in results]
    )
    
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]

    messages.insert(0, {"role": "user", "content": f"Contexto: {context}, Aqui tienes informacion relevante extraida de documentos oficiales de la Universidad del Valle:\n{retrieved_context}"})
 
    response = llm.invoke(messages).content

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})