import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Resolución 136 de 2017")
st.markdown("""
## 🧾 Resolución No. 136 de 2017  
### Reglamentación de la Creación y Reforma de Programas de Pregrado  
### Universidad del Valle

📅 **Fecha de emisión:** 22 de diciembre de 2017  
🏛️ **Emitida por:** Consejo Académico – Universidad del Valle  
📘 **Objetivo:** Establecer las condiciones para la creación y reforma de programas de pregrado, en concordancia con el Acuerdo No. 025 de 2015 del Consejo Superior.

---

### ⚖️ Principios Fundamentales

La reforma curricular se orienta bajo los siguientes principios:

- El estudiante como centro del proceso educativo.  
- Formación integral.  
- Autonomía personal.  
- Equilibrio entre lo científico, tecnológico, artístico y humanístico.  
- Flexibilidad académica y curricular.  
- Reconocimiento de la diversidad.

---

### 🧱 Estructura de Programas de Pregrado

Se definen tres tipos de programas:

- **Programas profesionales**  
- **Programas de licenciatura** (formación de educadores)  
- **Programas tecnológicos**

#### Componentes del programa:

- **Actividades Formativas:**
  - Asignaturas:
    - Básicas
    - Profesionales
    - Electivas Profesionales
    - Electivas Complementarias
  - Actividades Extracurriculares

- **Estructura en dos ciclos:**
  - **Ciclo Básico**
  - **Ciclo Profesional**
  - Con un componente transversal de **Formación General**

---

### 📚 Formación General

Diseñada para promover el desarrollo integral del estudiante, comprende los siguientes componentes:

- Formación social y ciudadana  
- Formación artística y humanística  
- Estilos de vida saludable  
- Lenguaje y comunicación  
- Formación científico-tecnológica

---

### 📊 Distribución de Créditos

| Componente                   | Porcentaje del total de créditos |
|-----------------------------|----------------------------------|
| Ciclo Básico                | 40% – 50%                        |
| Ciclo Profesional           | 50% – 60%                        |
| Formación General           | 20% – 25% (repartida en ambos ciclos) |
| Electivas Profesionales     | Mínimo 8%                        |

---

### 🗣️ Requisitos de Lengua

- **Español y Comunicación:**  
  - 4 créditos obligatorios

- **Lengua Extranjera (MCER):**
  - Nivel **B1** para estudiantes hispanohablantes (como requisito de grado)  
  - Nivel **B2** en español para estudiantes cuya lengua materna no es el español  
  - Nivel **A2** mínimo para programas tecnológicos o a distancia/virtual

---

### 🧭 Instancias Responsables

Participan en el diseño, aprobación y seguimiento:

- Comités de programa  
- Comités de currículo  
- Consejos de facultad  
- Vicerrectoría Académica  
- Otras instancias institucionales pertinentes

---

### 🕓 Implementación y Plazos

- Los cambios curriculares se aplicarán tras su aprobación por el **Ministerio de Educación Nacional**.  
- Todos los programas de pregrado deben ser actualizados dentro de los **dos años** siguientes a la expedición de esta resolución.

---

💡 **En resumen:**  
La Resolución 136 de 2017 establece lineamientos claros y unificados para la creación y reforma de programas de pregrado en la Universidad del Valle. Promueve una formación más integral, pertinente, flexible y centrada en el estudiante, articulando saberes y competencias desde una perspectiva moderna y transformadora.

""")

# Documento embebido (PDF)
st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1g2k4EEQ33bpUVrS1u3lPNKdwqn_Q4ymk/preview"

embed_pdf(pdf_url)
