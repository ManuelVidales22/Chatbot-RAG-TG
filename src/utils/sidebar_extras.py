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

    for chat_id, chat in chats:
        row_class = "uv-chat-row pinned" if chat["pinned"] else "uv-chat-row"
        icon = "📌" if chat["pinned"] else "💬"
        is_active = chat_id == st.session_state.current_chat_id

        st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)
        col_main, col_menu = st.columns([5, 1])

        with col_main:
            label = f"{icon} {chat['title']}"
            if st.button(label, key=f"chat_select_{chat_id}", use_container_width=True,
                         type="secondary" if not is_active else "primary"):
                chat_history.switch_chat(chat_id)
                st.switch_page(chat_page)

        with col_menu:
            with st.popover("⋮", use_container_width=True):
                pin_label = "📌 Desfijar" if chat["pinned"] else "📌 Fijar"
                if st.button(pin_label, key=f"chat_pin_{chat_id}", use_container_width=True):
                    chat_history.toggle_pin(chat_id)
                    st.rerun()
                if st.button("🗑️ Eliminar", key=f"chat_delete_{chat_id}", use_container_width=True):
                    chat_history.delete_chat(chat_id)
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
