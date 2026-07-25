import streamlit as st
import utils.chat_history as chat_history


def render_new_chat_button(chat_page):
    with st.container(key="new_chat_btn"):
        if st.button("＋ Nuevo Chat", use_container_width=True):
            chat_history.start_new_chat()
            st.switch_page(chat_page)


def render_chats_section(chat_page):
    st.markdown('<div class="uv-chats-heading">Chats</div>', unsafe_allow_html=True)

    chats = chat_history.get_ordered_chats()

    if not chats:
        st.markdown(
            '<div class="uv-chats-empty">Aún no tienes conversaciones guardadas.</div>',
            unsafe_allow_html=True,
        )
        return

    # st.popover no acepta "key": Streamlit rastrea si está abierto por su
    # POSICIÓN en la lista (estado de React), no por el chat que contiene. Al
    # fijar un chat, el popover no se cierra (comportamiento documentado de
    # Streamlit al interactuar con algo adentro). Al borrar un chat, la
    # posición se corre y el popover "abierto" queda pegado a esa posición,
    # ahora ocupada por otro chat. Ninguno de los dos es corregible con
    # parámetros de st.popover, así que el menú se maneja a mano con
    # session_state (control total sobre cuándo abre/cierra), en vez de
    # st.popover — mismo ícono "⋮", mismas opciones.
    if "open_chat_menu_id" not in st.session_state:
        st.session_state.open_chat_menu_id = None

    for chat_id, chat in chats:
        icon = "📌" if chat["pinned"] else "💬"
        is_active = chat_id == st.session_state.current_chat_id
        is_menu_open = st.session_state.open_chat_menu_id == chat_id

        # st.markdown('<div>...') + st.markdown('</div>') NO envuelve realmente
        # los elementos de Streamlit entre medio (React los renderiza como
        # hermanos, no como hijos), así que "position: relative" ahí no ancla
        # nada. Se usa un st.container(key=...) real, que sí es un padre
        # genuino en el DOM.
        with st.container(key=f"chat_row_{chat_id}"):
            col_main, col_menu = st.columns([5, 1])

            with col_main:
                label = f"{icon} {chat['title']}"
                if st.button(label, key=f"chat_select_{chat_id}", use_container_width=True,
                             type="secondary" if not is_active else "primary"):
                    chat_history.switch_chat(chat_id)
                    st.switch_page(chat_page)

            with col_menu:
                if st.button("⋮", key=f"chat_menu_btn_{chat_id}", use_container_width=True):
                    st.session_state.open_chat_menu_id = None if is_menu_open else chat_id
                    st.rerun()

            if is_menu_open:
                with st.container(key=f"chat_menu_box_{chat_id}"):
                    pin_label = "📌 Desfijar" if chat["pinned"] else "📌 Fijar"
                    if st.button(pin_label, key=f"chat_pin_{chat_id}", use_container_width=True):
                        chat_history.toggle_pin(chat_id)
                        st.session_state.open_chat_menu_id = None
                        st.rerun()
                    if st.button("🗑️ Eliminar", key=f"chat_delete_{chat_id}", use_container_width=True):
                        chat_history.delete_chat(chat_id)
                        st.session_state.open_chat_menu_id = None
                        st.rerun()
