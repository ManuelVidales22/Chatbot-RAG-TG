import streamlit as st
from langchain_openai import ChatOpenAI
import os 
import pdf_processor

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key = os.getenv("API_KEY"))
context = "Te llamas MauroBot y eres un chatbot de la Universidad del Valle sede Tulua que atiende preguntas de estudiantes del programa de Ingenieria de Sistemas. \n Te vas a limitar a solo responder preguntas relacionadas con la Universidad del Valle y vas a interpretar que siempre que alguien te haga una consulta va a ser relacionada con la Universidad del Valle y/o el programa de Ingeniria de Sistemas mas especificamente. \n Cuando un usuario pregunte algo que no esta relacionado a documentos, normativa, funcionamiento o algo parecido de la Universidad del Valle vas a responderle que no estas programado para esa funcion, (se flexible con saludos, agradecimientos y mensajes parecidos). \n Responde en base a informacion de documentos oficiales de la Universidad del Valle, los documentos que sean de la Facultad de Ingenieria tambien aplica para el Programa de Ingeneiria de Sistemas."

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
    results = vector_db.similarity_search(prompt, k=4)  # Buscar los 3 fragmentos más relevantes
    retrieved_context = "\n".join([doc.page_content for doc in results])

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
#    messages.append(["human", prompt])

    messages.insert(0, {"role": "user", "content": f"Contexto: {context}, Aqui tienes informacion relevante extraida de documentos oficiales de la Universidad del Valle:\n{retrieved_context}"})

    response = llm.invoke(messages).content

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})