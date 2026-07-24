import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from utils.theming import apply_theme
from utils.sidebar_extras import render_new_chat_button, render_chats_section
from utils.chat_history import init_chat_state

st.set_page_config(
    page_title="MauroBot Univalle",
    page_icon="assets/icons/UVNoLetters.png"
)

apply_theme()
init_chat_state()

with st.container(key="help_btn"):
    if st.button("❔", key="help_btn_inner"):
        st.toast("Manual de usuario próximamente.")

# --- Páginas ---
page_maurobot = st.Page("src/views/maurobot.py", title="MauroBot", icon="🤖")

page_acuerdo006 = st.Page("src/views/acuerdo_006.py", title="Acuerdo 006", icon="📄")
page_acuerdo009 = st.Page("src/views/acuerdo_009.py", title="Acuerdo 009", icon="📄")
page_resolucion047 = st.Page("src/views/resolucion_047.py", title="Resolución 047", icon="📄")
page_resolucion106 = st.Page("src/views/resolucion_106.py", title="Resolución 106", icon="📄")
page_pep047 = st.Page("src/views/pep_047.py", title="PEP 047", icon="📚")
page_resolucion048 = st.Page("src/views/resolucion_048.py", title="Resolución 048", icon="📄")
page_pep048 = st.Page("src/views/pep_048.py", title="PEP 048", icon="📚")
page_resolucion074 = st.Page("src/views/resolucion_074.py", title="Resolución 074", icon="📄")
page_resolucion162 = st.Page("src/views/resolucion_162.py", title="Resolución 162", icon="📄")
page_resolucion136 = st.Page("src/views/resolucion_136.py", title="Resolución 136", icon="📄")
page_equivalencias = st.Page("src/views/equivalencias_plan_transicion.py", title="Plan Transicion", icon="🔄")

page_faq = st.Page("src/views/faq.py", title="FAQ", icon="❓")

page_calendario = st.Page("src/views/calendario_academico.py", title="Calendario Académico", icon="📅")

# --- Navegación ---
navigation = st.navigation(
    {
        "Asistente IA": [page_maurobot],
        "Calendario Academico": [page_calendario],
        "Documentos": [page_acuerdo009, page_acuerdo006, page_resolucion047, page_resolucion106, page_pep047, page_resolucion048, page_pep048, page_resolucion074, page_resolucion162, page_resolucion136, page_equivalencias],
        "Preguntas Frecuentes": [page_faq],
    },
    position="hidden",
)

with st.sidebar:
    render_new_chat_button(page_maurobot)

    st.markdown('<div class="uv-nav-heading">Calendario Academico</div>', unsafe_allow_html=True)
    st.page_link(page_calendario, icon=page_calendario.icon)

    st.markdown('<div class="uv-nav-heading">Documentos administrativos</div>', unsafe_allow_html=True)
    with st.container(height=220, key="docs_scroll"):
        for doc_page in [
            page_acuerdo009, page_acuerdo006, page_resolucion047, page_resolucion106,
            page_pep047, page_resolucion048, page_pep048, page_resolucion074,
            page_resolucion162, page_resolucion136, page_equivalencias,
        ]:
            st.page_link(doc_page, icon=doc_page.icon)

    st.markdown('<div class="uv-nav-heading">Preguntas Frecuentes</div>', unsafe_allow_html=True)
    st.page_link(page_faq, icon=page_faq.icon)

navigation.run()

# Se renderiza después de correr la página para reflejar los mensajes
# sincronizados durante la ejecución (p. ej. el título autogenerado).
with st.sidebar:
    render_chats_section(page_maurobot)