import uuid
import streamlit as st

DEFAULT_TITLE = "Nuevo chat"


def _new_chat_entry():
    return {"title": DEFAULT_TITLE, "messages": [], "pinned": False, "needs_new_title": False}


def init_chat_state():
    if "chats" not in st.session_state:
        st.session_state.chats = {}

    if (
        "current_chat_id" not in st.session_state
        or st.session_state.current_chat_id not in st.session_state.chats
    ):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = _new_chat_entry()
        st.session_state.current_chat_id = new_id

    st.session_state.messages = st.session_state.chats[st.session_state.current_chat_id]["messages"]


def _update_title_from_messages(chat_id):
    chat = st.session_state.chats[chat_id]
    if chat["title"] != DEFAULT_TITLE and not chat.get("needs_new_title"):
        return
    for msg in chat["messages"]:
        if msg["role"] == "user":
            title = msg["content"].strip().replace("\n", " ")
            chat["title"] = title[:40] + ("…" if len(title) > 40 else "")
            chat["needs_new_title"] = False
            break


def sync_current_messages():
    current_id = st.session_state.current_chat_id
    st.session_state.chats[current_id]["messages"] = st.session_state.messages
    _update_title_from_messages(current_id)


def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = _new_chat_entry()
    st.session_state.current_chat_id = new_id
    st.session_state.messages = st.session_state.chats[new_id]["messages"]


def switch_chat(chat_id):
    if chat_id in st.session_state.chats:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chats[chat_id]["messages"]


def toggle_pin(chat_id):
    if chat_id in st.session_state.chats:
        chat = st.session_state.chats[chat_id]
        chat["pinned"] = not chat["pinned"]


def delete_chat(chat_id):
    if chat_id not in st.session_state.chats:
        return
    was_current = st.session_state.current_chat_id == chat_id
    del st.session_state.chats[chat_id]

    if was_current:
        if st.session_state.chats:
            switch_chat(list(st.session_state.chats.keys())[-1])
        else:
            start_new_chat()


def clear_current_chat():
    """
    Vacía los mensajes del chat activo. Conserva su título y su lugar en 'Chats'
    hasta que llegue un mensaje nuevo, momento en el que el título se actualiza
    con esa nueva pregunta (needs_new_title).
    """
    current_id = st.session_state.current_chat_id
    chat = st.session_state.chats[current_id]
    chat["messages"] = []
    chat["needs_new_title"] = True
    st.session_state.messages = chat["messages"]


def get_ordered_chats():
    """Chats que ya tuvieron al menos un mensaje (título asignado), fijados primero."""
    items = [(cid, chat) for cid, chat in st.session_state.chats.items() if chat["title"] != DEFAULT_TITLE]
    items.sort(key=lambda item: not item[1]["pinned"])
    return items
