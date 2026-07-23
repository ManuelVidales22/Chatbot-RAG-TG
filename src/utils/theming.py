import base64
import os
import streamlit as st

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
CSS_PATH = os.path.join(ASSETS_DIR, "css", "theme.css")
CLEAN_ICON_PATH = os.path.join(ASSETS_DIR, "icons", "clean_white.png")


def _data_uri(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def apply_theme():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    clean_icon_uri = _data_uri(CLEAN_ICON_PATH)
    st.markdown(
        f"""
        <style>
        .st-key-clear_chat_btn button {{
            background-image: url("{clean_icon_uri}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: 20px 20px;
        }}
        .st-key-clear_chat_btn button [data-testid="stMarkdownContainer"] p {{
            font-size: 0;
            visibility: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def scroll_to_bottom_button():
    """
    st.components.v1.html crea un iframe nuevo en cada rerun de Streamlit; el iframe
    anterior se destruye junto con cualquier setInterval/listener definido dentro de él.
    Por eso la lógica de visibilidad se inyecta como <script> en el documento padre: así
    corre en el contexto persistente de la página real y sobrevive a los reruns.
    """
    st.components.v1.html(
        """
        <script>
        (function () {
            const parentDoc = window.parent.document;
            if (parentDoc.getElementById("mb-scroll-script")) {
                return;
            }

            const script = parentDoc.createElement("script");
            script.id = "mb-scroll-script";
            script.textContent = `
                (function () {
                    const doc = document;
                    if (doc.getElementById("mb-scroll-btn")) { return; }

                    const btn = doc.createElement("button");
                    btn.id = "mb-scroll-btn";
                    btn.className = "mb-scroll-btn";
                    btn.innerHTML = "&#8595;";
                    btn.title = "Ir al último mensaje";
                    doc.body.appendChild(btn);

                    function getScrollContainer() {
                        return (
                            doc.querySelector('[data-testid="stAppScrollToBottomContainer"]') ||
                            doc.scrollingElement
                        );
                    }

                    function isNearBottom(el) {
                        if (!el) return true;
                        return el.scrollHeight - el.scrollTop - el.clientHeight < 120;
                    }

                    function updateVisibility() {
                        const el = getScrollContainer();
                        if (isNearBottom(el)) {
                            btn.classList.remove("mb-visible");
                        } else {
                            btn.classList.add("mb-visible");
                        }
                    }

                    function updatePosition() {
                        const el = getScrollContainer();
                        if (!el) { return; }
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0) {
                            btn.style.left = (rect.left + rect.width / 2) + "px";
                        }
                    }

                    btn.addEventListener("click", function () {
                        const el = getScrollContainer();
                        if (el) {
                            el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
                        }
                    });

                    setInterval(function () {
                        updateVisibility();
                        updatePosition();
                    }, 500);
                })();
            `;
            parentDoc.body.appendChild(script);
        })();
        </script>
        """,
        height=0,
    )
