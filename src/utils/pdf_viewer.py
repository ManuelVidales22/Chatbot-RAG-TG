import streamlit as st

def embed_pdf(pdf_path: str, ratio: float = 1.2):
    st.components.v1.html(
        f"""
        <div style="position: relative; width: 100%; padding-bottom: {ratio * 100:.2f}%; height: 0;">
            <iframe src="{pdf_path}"
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
                    frameborder="0"
                    scrolling="auto">
            </iframe>
        </div>
        """,
        height=1000,
    )