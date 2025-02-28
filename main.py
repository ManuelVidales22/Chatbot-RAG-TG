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

if prompt := st.chat_input("Escribe tu pregunta"):

    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
    messages.append(["human", prompt])

    response = llm.invoke(messages).content

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})