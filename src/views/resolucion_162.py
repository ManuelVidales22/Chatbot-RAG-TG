import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Resolución 162 de 2021")
st.markdown("""
## 🧾 Resolución No. 162 de 2021  
### Reglamentación del Examen de Clasificación en Idioma Extranjero  
### Universidad del Valle

📅 **Fecha de emisión:** 02 de septiembre de 2021  
🏛️ **Emitida por:** Consejo Académico – Universidad del Valle  
📘 **Objetivo:** Establecer las condiciones para el examen de clasificación en lengua extranjera y sus homologaciones en los programas de pregrado, fomentando la internacionalización del currículo y el desarrollo de una segunda lengua.

---

### 🧪 Examen de Clasificación

- Aplicado por la **Escuela de Ciencias del Lenguaje** a los estudiantes de primer semestre.  
- Evalúa el dominio de una lengua extranjera según el **Marco Común Europeo de Referencia (MCER)**, ubicando a los estudiantes en niveles de **A1 a B1**.  
- Se establecen tablas de equivalencia entre:
  - Puntaje de la prueba (0–120)  
  - Curso asignado (e.g., "Inglés con Fines Generales y Académicos I-IV")  
  - Nivel MCER esperado  
- Un puntaje de **106 a 120** exime al estudiante por demostrar **nivel B1 consolidado**.  
- También se contemplan pruebas de **francés** y **portugués**.

---

### 📌 Requisitos de Suficiencia (según Resolución 136 de 2017)

- **Programas profesionales:** Nivel **B1** en lengua extranjera  
- **Programas tecnológicos:** Nivel **A2**  
- **Español como segunda lengua:**
  - Nivel **B2** para estudiantes extranjeros  
  - Nivel **B1** para estudiantes indígenas, afrocolombianos de lenguas criollas, sordos y sordociegos  
  - *(Nota: esto no exime del requisito de lengua extranjera del programa)*

---

### 📚 Oferta de Cursos y Cumplimiento del Requisito

- Según el puntaje en el examen, la Escuela de Ciencias del Lenguaje asigna los cursos correspondientes.  
- La **aprobación de los cursos equivale a cumplir el requisito de suficiencia** para grado.  
- Estudiantes por debajo de A1 pueden cursar un **nivelatorio introductorio**.

---

### 🔄 Homologaciones

#### ✅ Válidas por hasta 3 años

1. **Pruebas Internacionales**  
   - Certificaciones oficiales que acrediten el nivel exigido.

2. **Estudios Externos en Lengua Extranjera**  
   - Cursos o estudios realizados en instituciones de educación superior (nacionales o extranjeras).

3. **Cursos Internos**  
   - Cursos previamente aprobados dentro de la universidad, válidos si fueron cursados en los últimos tres años.  
   - Aplica a casos de reingreso, traslado o reformas curriculares.

4. **Estudios en Lengua Extranjera (media o superior)**  
   - Mínimo un año cursado en inglés, francés o portugués en los últimos tres años.

---

### 🚫 No homologables automáticamente

- Antiguos cursos como **“Lectura de textos académicos en inglés”**  
  - No equivalen directamente a los nuevos cursos de “Inglés con Fines Generales y Académicos” debido a su enfoque limitado en lectura.  
- Homologación de cursos como:
  - “Lectura de textos contables”  
  - “Business English”  
  Requieren evaluación de pertinencia y cobertura de habilidades.

---

### 🕓 Vigencia

- La resolución entra en vigencia desde su aprobación el **2 de septiembre de 2021**.  
- **Deroga todas las disposiciones anteriores** que sean contrarias.

---

💡 **En resumen:**  
La Resolución 162 de 2021 establece el sistema oficial para clasificar, ubicar y homologar el dominio de una lengua extranjera en estudiantes de pregrado, reforzando el enfoque institucional en competencias globales y asegurando criterios claros para el cumplimiento del requisito de grado en idiomas.

""")

# Documento embebido (PDF)
st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1RFMqw8CD5T46sDbFreTMDAjxpzJfvxn9/preview"

embed_pdf(pdf_url)
