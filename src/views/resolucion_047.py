import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Resolución 047 de 2020")
st.markdown("""
## 🧾 Resolución No. 047 de 2020  
### Programa de Ingeniería de Sistemas – Universidad del Valle

📅 **Fecha de emisión:** 16 de abril de 2020  
🏛️ **Emitida por:** Consejo Académico – Universidad del Valle  
📘 **Objetivo:** Modificar la estructura curricular del programa, reemplazando la Resolución No. 048 de 2010.

---

### 🧠 Definición del Programa

- Duración: **10 semestres**  
- Modalidad: **Presencial**  
- Título otorgado: **Ingeniero de Sistemas**  
- Total de créditos: **154**  
- Oferta: Sedes **Cali** y **Tuluá**, con cupos definidos

---

### 🎯 Objetivos del Programa

- **General:**  
  Formar profesionales capaces de solucionar problemas reales mediante la computación, con formación científica, tecnológica y personal sólida, y capacidad de actualización global.

- **Específicos:**  
  - Formación en ciencias pertinentes.  
  - Aplicación de métodos y herramientas de la ingeniería.  
  - Análisis de problemas y desarrollo de soluciones TIC sostenibles.  
  - Adaptación al cambio tecnológico.  
  - Comunicación efectiva.  
  - Compromiso social.

---

### 👨‍🎓 Perfil de Egreso

El egresado será capaz de:

- Desarrollar proyectos y soluciones considerando aspectos éticos, ambientales y sociales.
- Aprender de forma autónoma y continua.
- Desempeñarse en:
  - Desarrollo de software.  
  - Diseño de interacción humano-computador.  
  - Investigación aplicada.  
  - Análisis y gestión de datos.  
  - Gestión de infraestructura TIC.

---

### 💼 Perfil Ocupacional

El Ingeniero de Sistemas podrá ocupar roles como:

- Director de sistemas  
- Ingeniero de desarrollo  
- Arquitecto de software  
- Gerente de infraestructura informática  
- Diseñador UI/UX  
- Entre otros cargos relacionados con TIC

---

### 🧱 Estructura Curricular

Organizada en **dos ciclos**:

- **Ciclo Básico:** 64 créditos  
- **Ciclo Profesional:** 90 créditos

**Componentes de Formación General (FG):**  
Representan el **25.5%** del total de créditos.  
Incluyen asignaturas en:

- Formación social y ciudadana  
- Lenguaje y comunicación  
- Estilos de vida saludable  
- Formación artística y humanística  
- Formación científico-tecnológica

> Además, se presenta una tabla con asignaturas, tipo (básicas, profesional, electivas) y créditos correspondientes.

---

### 📌 Requisitos Adicionales

- **Trabajo de Grado:** Obligatorio para optar al título.  
- **Lengua Extranjera:** Acreditar nivel **B1 de inglés** (MCER) para poder matricular Trabajo de Grado I.

---

### ⏳ Transición y Vigencia

- Se establece un plan de transición para estudiantes activos.
- Define plazos para estudiantes no activos.
- La resolución entra en vigencia tras su aprobación por el **Ministerio de Educación Nacional**.

---

💡 **En resumen:**  
La Resolución 047 de 2020 actualiza y formaliza el plan de estudios del programa de Ingeniería de Sistemas, definiendo claramente sus objetivos, perfiles, estructura académica, requisitos de grado y componentes de formación integral, alineados con las necesidades profesionales contemporáneas.

""")

# Documento embebido (PDF)
st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1pKF4yN1YCJYRg3Qlfnnati_UrlCCdi8e/preview"

embed_pdf(pdf_url)
