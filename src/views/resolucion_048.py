import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Resolución 048 de 2010")
st.markdown("""
## 🧾 Resolución No. 048 de 2010  
### Programa de Ingeniería de Sistemas – Universidad del Valle

📅 **Fecha de emisión:** 29 de abril de 2010  
🏛️ **Emitida por:** Consejo Académico – Universidad del Valle  
📘 **Objetivo:** Modificar el currículo del programa de Ingeniería de Sistemas, actualizando la Resolución No. 070 de 2002.

---

### 🧠 Actualización del Programa

- Se actualiza el número de créditos y el nombre de algunas asignaturas.
- Título otorgado: **Ingeniero/a de Sistemas**.

---

### 🎯 Objetivos del Programa

- **General:**  
  Formar profesionales en Ingeniería de Sistemas y Computación capaces de resolver problemas reales, con sólidos conocimientos teóricos y capacidad de mantenerse actualizados.

- **Específicos:**  
  - Conocimiento en Ciencias de la Computación.  
  - Habilidades en análisis, diseño e implementación de sistemas.  
  - Fortalecimiento de competencias personales como comunicación, trabajo en equipo y aprendizaje autónomo.

---

### 👨‍🎓 Perfil del Egresado

Se busca formar un **ingeniero emprendedor**, con:

- Sólido conocimiento en ciencias y tecnologías de la computación.
- Participación en proyectos de desarrollo de software de calidad internacional.
- Competencias en:
  - Diseño, especificación, implementación y evaluación de sistemas basados en computador.
  - Manejo de información.
  - Interacción humano-computador.
  - Seguridad informática.
  - Metodologías de desarrollo de software.

---

### 🧱 Estructura Curricular

- **Total de créditos:** 159  
- Distribución:

  - **Asignaturas Básicas Obligatorias (AB):** 63 créditos (40%)  
  - **Asignaturas Profesionales Obligatorias (AP):** 74 créditos (47%)  
  - **Asignaturas Electivas Complementarias (AEC):** 10 créditos (6%)  
  - **Asignaturas Electivas Profesionales (AEP):** 12 créditos (7%)

> El plan incluye asignaturas en ciencias básicas, programación, arquitectura de computadores, algoritmos, ingeniería de software, redes, inteligencia artificial, gestión de información, entre otras.

---

### 📌 Requisitos Específicos

- **Prerrequisitos:** Establecidos por las unidades académicas.  
- **Electivas Complementarias:**  
  - Cursar mínimo cuatro.  
  - Incluir temáticas como problemas colombianos, salud y cultura física.  
- **Formación Transversal:**  
  - Examen de clasificación en español.  
  - Formación en Constitución Política y Ética.  
- **Idioma Inglés:**  
  - Acreditar comprensión avanzada como requisito de grado.  
- **Electivas Profesionales:**  
  - Cursar cuatro asignaturas (3 créditos cada una).  
  - Dos deben pertenecer a una línea de énfasis.  
  - Pueden ser reemplazadas por prácticas profesionales.  
- **Trabajo de Grado:**  
  - Seminario de Trabajo de Grado (1 crédito).  
  - Trabajo de Grado I (2 créditos).  
  - Trabajo de Grado II (7 créditos).

---

### ⏳ Vigencia y Aplicación

- Aplica a estudiantes nuevos desde 2010.  
- También para estudiantes actuales que deseen homologar.  
- Incluye un esquema secuencial del plan curricular.

---

💡 **En resumen:**  
Esta resolución establece el marco académico del programa de Ingeniería de Sistemas desde 2010, definiendo sus objetivos formativos, el perfil profesional del egresado, la organización curricular y los requisitos para obtener el título, con énfasis en una formación sólida, flexible y adaptada a las exigencias del sector tecnológico.

""")

# Documento embebido (PDF)
st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/18_ra9Hk1O8xXfTyMejSGc0UlySR91Twf/preview"

embed_pdf(pdf_url)
