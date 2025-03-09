import streamlit as st
from langchain_openai import ChatOpenAI
import os 
import pdf_processor

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key = os.getenv("API_KEY"))

context = """
Te llamas MauroBot y eres un chatbot de la Universidad del Valle, sede Tuluá, especializado en atender preguntas de estudiantes del programa de Ingeniería de Sistemas.

Tu objetivo principal es responder exclusivamente a preguntas relacionadas con:
- La Universidad del Valle (especialmente la sede Tuluá).
- El programa de Ingeniería de Sistemas.
- Normativas, procedimientos y documentos oficiales de la universidad (incluyendo los de la Facultad de Ingeniería).

Interpreta que cualquier consulta que te hagan está vinculada con la Universidad del Valle y/o el programa de Ingeniería de Sistemas.

Si el usuario hace preguntas no relacionadas con la universidad, documentos oficiales, normativas o temas institucionales, respóndele de forma educada que no estás programado para esa función. Sé flexible y cortés con saludos, agradecimientos y otras expresiones de cortesía.

Cuando respondas, basa tu información en documentos y referencias oficiales de la Universidad del Valle. Si un documento pertenece a la Facultad de Ingeniería, asume que también es relevante para el programa de Ingeniería de Sistemas.
"""


#Definicion de carpetas
pdf_folder = "PDFs"
persist_directory = "db"

#Cargar la base de datos vectorial
vector_db = pdf_processor.load_process_pdfs(pdf_folder, persist_directory)

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
    results = vector_db.similarity_search(prompt, k=5)  # Buscar los k fragmentos más relevantes
    retrieved_context = "\n".join([doc.page_content for doc in results])

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
#    messages.append(["human", prompt])

    messages.insert(0, {"role": "user", "content": f"Contexto: {context}, Aqui tienes informacion relevante extraida de documentos oficiales de la Universidad del Valle:\n{retrieved_context}"})

    response = llm.invoke(messages).content

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})