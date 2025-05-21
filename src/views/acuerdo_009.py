import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Acuerdo 009 de 1997")
st.markdown("""
## Acuerdo No. 009 del Consejo Superior de la Universidad del Valle

📅 **Fecha:** 13 de noviembre de 1997  
📘 **Modifica:** Acuerdo 002 de 1994  
🎓 **Objeto:** Regula las actividades académicas de los estudiantes de pregrado en la Universidad del Valle.

---

### 📝 Admisión y Matrícula
- Requisitos para ser admitido como estudiante de pregrado.
- Modalidades educativas y criterios de admisión.
- Proceso de matrícula y selección de asignaturas.

### ⚖️ Derechos y Deberes
- **Derechos:** Trato respetuoso, participación, acceso a recursos institucionales.
- **Deberes:** Cumplir normas, contribuir al proyecto institucional y mantener una conducta ética.

### 🗳️ Representación Estudiantil
- Funciones y estructura del Consejo Estudiantil.
- Participación activa en órganos colegiados universitarios.

### 📊 Evaluación Académica
- Tipos de evaluación: parciales, finales, habilitaciones, validaciones, clasificaciones y progresivas.
- Procedimientos, objetivos y escalas de calificación.

### 🧮 Calificaciones y Promedios
- Escala numérica y equivalencias no numéricas.
- Responsabilidades para asignación y modificación de notas.
- Cálculo de promedios académicos.

### 🧾 Matrícula
- Procedimientos para matrícula financiera y académica.
- Reglas para adición y cancelación de asignaturas.
- Consecuencias de la matrícula extemporánea.

### 🔁 Repeticiones, Bajos Rendimientos y Reingresos
- Reglas para repetir asignaturas.
- Manejo del bajo rendimiento académico.
- Procedimientos y requisitos de reingreso a la universidad.

### 🔄 Traslados y Transferencias
- Procedimientos para traslados internos entre programas.
- Requisitos para transferencias desde otras instituciones.

### 📑 Equivalencias Académicas
- Criterios para reconocimiento de estudios previos.
- Proceso para otorgar equivalencias.

### 📚 Cursos de Vacaciones
- Requisitos de inscripción.
- Evaluación del rendimiento académico.

### 🎓 Trabajos de Grado
- Modalidades, requisitos y plazos establecidos.
- Reconocimientos como **meritorio** o **laureado**.

### 🏅 Estímulos Académicos
- Reconocimientos al desempeño académico, cultural y deportivo.
- Exoneraciones de matrícula como incentivo.

### ⚖️ Régimen Disciplinario
- Clasificación de faltas: leves, graves y gravísimas.
- Sanciones, garantías del debido proceso y circunstancias atenuantes.

### 📄 Certificaciones
- Tipos de certificados disponibles.
- Procedimientos y tarifas para su expedición.

### 🏛️ Reglamentos Internos
- Facultades de las unidades académicas para establecer sus propios reglamentos complementarios.

---

📌 Este reglamento establece el marco general para la vida académica del estudiante de pregrado en la Universidad del Valle.

""")

# Documento embebido (PDF)
st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1k1SiW-ukKD9jUapTJf75Y8C2vRfyZyJ9/preview"

embed_pdf(pdf_url)
