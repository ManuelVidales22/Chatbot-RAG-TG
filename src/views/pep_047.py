import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Proyecto Educativo del Programa res 047")
st.markdown("""
## Proyecto Educativo del Programa (PEP)  
### Ingeniería de Sistemas – Universidad del Valle

📅 **Actualizado:** Abril de 2024  
🏫 **Programa:** Ingeniería de Sistemas  
📘 **Propósito:** Establece la identidad del programa y orienta sus acciones formativas, en coherencia con el marco misional de la Universidad del Valle.

---

### 🧭 Características Generales del Programa
- Información institucional y reseña histórica.
- Justificación del programa y fundamentos teóricos.
- Oportunidades en áreas:
  - **Co-curriculares**.
  - **Prácticas y pasantías**.
  - **Actividades extracurriculares**.
  - **Proyección académica**.

### 🎯 Propósito y Pertinencia
- **Misión, visión y objetivos** del programa.
- **Perfil de egreso** y **perfil ocupacional**.
- **Prospectiva futura**, con énfasis en gestión y análisis inteligente de datos.

### 🧩 Organización y Estrategia Curricular
- Lineamientos institucionales del currículo.
- **Estructura del plan de estudios**:
  - Malla curricular.
  - Ciclos básico y profesional.
- Integración curricular:
  - Vertical y horizontal.
  - Enfoque interdisciplinario.
- Estrategias pedagógicas y metodológicas:
  - Aprendizaje basado en proyectos.
  - Aula invertida.
  - Aprendizaje colaborativo.
- Evaluación:
  - Formativa.
  - Social.

### 🌍 Articulación con el Medio
- Prácticas y pasantías profesionales.
- Investigación:
  - Proyectos de cooperación.
  - Convenios nacionales e internacionales.
- Movilidad académica:
  - Programas como **CINDA** y **SÍGUEME**.
- Relación con egresados.

---

### 🏛️ Estructura Administrativa y Académica
- Listado de miembros del:
  - Consejo Superior.
  - Consejo Académico.
- Personal directivo y comités relevantes:
  - Facultad de Ingeniería.
  - Escuela de Ingeniería de Sistemas y Computación.

---

💡 **En resumen:**  
El PEP es un documento dinámico que articula la historicidad, los enfoques disciplinares y pedagógicos, la vinculación con el entorno y los objetivos formativos. Todo ello con el fin de formar profesionales íntegros, competentes y comprometidos con el desarrollo regional y la construcción de una sociedad más justa.
 """)

st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1ctUVeBLxOvkkFFL5JCMGGyZLWlvmpMKA/preview"
embed_pdf(pdf_url)