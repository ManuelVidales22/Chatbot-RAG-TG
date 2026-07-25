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


def fix_sidebar_menu_overflow():
    """
    stSidebarContent trae "overflow: overlay" (shorthand) desde Streamlit, y
    recorta la tarjeta flotante del menú "⋮". Ni un override CSS con
    !important ni un estilo inline con !important (ambos verificados) logran
    cambiar el estilo computado — es una rareza de este motor de Chromium con
    ese valor heredado específico, no un problema de cascada.

    En vez de pelear con overflow, se "congela" la posición de la tarjeta:
    se lee su posición real (correcta incluso recortada, porque el recorte
    es solo de pintado, no de layout) y se le pone position:fixed con esas
    mismas coordenadas — fixed no se recorta por overflow de un ancestro sin
    transform/filter, así que escapa el recorte quedando en el mismo lugar.
    """
    st.components.v1.html(
        """
        <script>
        (function () {
            const parentDoc = window.parent.document;
            if (parentDoc.getElementById("mb-menu-position-script")) {
                return;
            }

            const script = parentDoc.createElement("script");
            script.id = "mb-menu-position-script";
            script.textContent = `
                (function () {
                    function fix() {
                        const boxes = document.querySelectorAll('[class*="st-key-chat_menu_box_"]');
                        boxes.forEach(function (box) {
                            const cs = getComputedStyle(box);
                            if (cs.position !== "fixed") {
                                const rect = box.getBoundingClientRect();
                                box.style.setProperty("position", "fixed", "important");
                                box.style.setProperty("top", rect.top + "px", "important");
                                box.style.setProperty("left", rect.left + "px", "important");
                                box.style.setProperty("margin", "0", "important");
                            }

                            // Los botones (Fijar/Eliminar) traen un ancho en px calculado
                            // por Streamlit antes de que la tarjeta se redujera a 190px;
                            // igual que con "overflow", el override CSS no se refleja en
                            // el estilo computado, así que se fuerza aquí en cada tick.
                            const innerWidth = Math.max(0, box.clientWidth - 16);
                            box.querySelectorAll(
                                'button, [data-testid="stElementContainer"], [data-testid="stVerticalBlock"]'
                            ).forEach(function (child) {
                                child.style.setProperty("width", innerWidth + "px", "important");
                                child.style.setProperty("max-width", innerWidth + "px", "important");
                                child.style.setProperty("box-sizing", "border-box", "important");
                            });
                        });
                    }
                    fix();
                    setInterval(fix, 200);
                })();
            `;
            parentDoc.body.appendChild(script);
        })();
        </script>
        """,
        height=0,
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
