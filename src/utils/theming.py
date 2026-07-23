import os
import streamlit as st

CSS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "css", "theme.css")


def apply_theme():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def scroll_to_bottom_button():
    st.components.v1.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            if (doc.getElementById("mb-scroll-btn")) {
                return;
            }

            const btn = doc.createElement("button");
            btn.id = "mb-scroll-btn";
            btn.className = "mb-scroll-btn";
            btn.innerHTML = "&#8595;";
            btn.title = "Ir al último mensaje";
            doc.body.appendChild(btn);

            function getScrollContainer() {
                return (
                    doc.querySelector('[data-testid="stAppScrollToBottomContainer"]') ||
                    doc.querySelector('[data-testid="stMain"]') ||
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

            btn.addEventListener("click", function () {
                const el = getScrollContainer();
                if (el) {
                    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
                }
            });

            const container = getScrollContainer();
            if (container) {
                container.addEventListener("scroll", updateVisibility);
            }
            doc.defaultView.addEventListener("resize", updateVisibility);

            updateVisibility();
            setInterval(updateVisibility, 800);
        })();
        </script>
        """,
        height=0,
    )
