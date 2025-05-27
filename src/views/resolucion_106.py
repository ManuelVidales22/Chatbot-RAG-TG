import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Resolución 106 de 2021")
st.markdown("""
## 🧾 Resolución No. 106 de 2021  
### Corrección de nombres en la Estructura Curricular  
### Ingeniería de Sistemas – Universidad del Valle

📅 **Fecha de emisión:** 17 de junio de 2021  
🏛️ **Emitida por:** Consejo Académico – Universidad del Valle  
📘 **Objetivo:** Corregir errores de forma en los nombres de asignaturas incluidos en la Resolución No. 047 de 2020.

---

### ⚠️ Contexto

La Resolución 047 de 2020 modificó el currículo del Programa de Ingeniería de Sistemas. Sin embargo, en su Artículo 5° (Estructura Curricular), se incluyeron varios nombres de asignaturas de manera incorrecta.

---

### 🛠️ Correcciones Realizadas

Los siguientes nombres de asignaturas fueron corregidos:

| Nombre incorrecto                        | Nombre corregido                                     |
|------------------------------------------|-------------------------------------------------------|
| Cálculo I                                | Cálculo monovariable                                  |
| Cálculo II                               | Cálculo multivariable                                 |
| Análisis económico de inversiones        | Ingeniería económica                                  |
| Introducción a la gestión ambiental      | Impactos ambientales                                  |
| Introducción a la ciencias de los datos  | Introducción a la ciencia de los datos                |
| Lectura crítica                          | Comprensión y producción de textos académicos generales |

---

### 🕓 Vigencia

Esta resolución entra en vigencia a partir de su aprobación por el Consejo Académico, es decir, el **17 de junio de 2021**.

---

💡 **En resumen:**  
La Resolución No. 106 de 2021 corrige errores formales en la denominación de asignaturas dentro del plan de estudios de Ingeniería de Sistemas, garantizando coherencia y precisión en los documentos oficiales del programa.

 """)

st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1uTp1TiAk0ksY1A8qoWeBG7gpcvi3OJob/preview"
embed_pdf(pdf_url)