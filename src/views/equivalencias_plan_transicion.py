import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Equivalencias Plan de Transición")
st.markdown("""
## 📊 Comparación de Planes de Estudio  
### Ingeniería de Sistemas - Universidad del Valle

📘 **Documento:** Tabla comparativa entre dos planes de estudio  
📅 **Resoluciones:** Resolución 048 vs. Nueva Resolución  
🎓 **Estructura:** 10 semestres

---

### 🔍 Enfoque del Documento

El archivo presenta una tabla comparativa que permite visualizar la transición de un plan de estudios antiguo hacia uno actualizado. Su propósito es mostrar los cambios estructurales, temáticos y crediticios en el currículo del programa de Ingeniería de Sistemas.

---

### 📌 Cambios Principales Identificados

- **Asignaturas nuevas:** Se integran materias que no estaban contempladas anteriormente.  
- **Modificación de asignaturas:** Cambios en nombres, enfoques o contenidos temáticos.  
- **Ajustes en créditos:** Variación en la carga académica de asignaturas similares.  
- **Reorganización semestral:** Asignaturas movidas a otros semestres.  
- **Fusión o división:** Algunas materias se consolidan o se dividen según criterios académicos.

---

### 🧠 Componentes del Programa

- **Áreas centrales:** Matemáticas, programación, bases de datos, sistemas operativos, redes, desarrollo de software, inteligencia artificial.  
- **Formación integral:** Asignaturas orientadas al bienestar, la comunicación y la adaptación universitaria.  
- **Progresión académica:** Desde fundamentos básicos hasta temáticas avanzadas y trabajo de grado.

---

💡 **En resumen:**  
Este documento refleja la actualización y modernización del programa académico, evidenciando cómo evolucionan los contenidos, la distribución semestral y la carga crediticia para responder a los nuevos retos de la formación profesional.


 """)

st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1-PvlEwtjuLZZ080gVS-MpApz3adMMx63/preview"
embed_pdf(pdf_url)