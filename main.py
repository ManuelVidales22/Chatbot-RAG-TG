import streamlit as st
from langchain_openai import ChatOpenAI
import os 

llm = ChatOpenAI(model="o1-mini", temperature=1, api_key = os.getenv("API_KEY"))

st.title("MauroBot Univalle")

#Mensaje del sistemas que le da identidad al chatbot, pero no funciona con modelos mini
#messages = [("system", "Te llamas MauroBot y eres un chatbot de la Universidad del Valle sede Tulua que atiende preguntas de estudiantes del programa de Ingenieria de Sistemas")]

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

context = "Te llamas MauroBot y eres un chatbot de la Universidad del Valle sede Tulua que atiende preguntas de estudiantes del programa de Ingenieria de Sistemas. /n Te vas a limitar a solo responder preguntas relacionadas con la Universidad del Valle y vas a interpretar que siempre que alguien te haga una consulta va a ser relacionada con la Universidad del Valle y/o el programa de Ingeniria de Sistemas mas especificamente. /n Cuando un usuario pregunte algo que no esta relacionado a documentos, normativa, funcionamiento o algo parecido de la Universidad del Valle vas a responderle que no estas programado para esa funcion, (se flexible con saludos, agradecimientos y mensajes parecidos). /n"

if prompt := st.chat_input("Escribe tu pregunta"):

    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
    messages.append(["human", prompt])

    messages.insert(0, {"role": "user", "content": context})

    response = llm.invoke(messages).content

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})