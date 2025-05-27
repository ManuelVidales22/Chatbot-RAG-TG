import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Resolución 074 de 2015")
st.markdown("""
## 🧾 Resolución No. 074 de 2015  
### Modalidades de Trabajo de Grado – Facultad de Ingeniería  
### Universidad del Valle

📅 **Fecha de emisión:** 14 de mayo de 2015  
🏛️ **Emitida por:** Consejo Académico – Universidad del Valle  
📘 **Objetivo:** Aprobar y definir las diferentes modalidades de trabajo de grado para los estudiantes de la Facultad de Ingeniería.

---

### ⚖️ Marco Regulatorio

- Basada en el **Acuerdo 009 de 1997**, que exige la presentación de un trabajo de grado para optar al título de pregrado.
- Responde a la necesidad de reglamentar y actualizar los procesos académicos relacionados con el trabajo de grado en la Facultad de Ingeniería.

---

### 🧩 Definición de Trabajo de Grado

El trabajo de grado se entiende como una aplicación teórica o teórico-práctica de los conocimientos y habilidades adquiridas en la formación profesional, orientado al análisis y solución de un problema propio del área de estudio.

---

### 📌 Modalidades Aprobadas

1. **Trabajo Profesional**  
   Desarrollo sistemático para solucionar un problema específico del campo profesional.

2. **Trabajo de Revisión Crítica**  
   Análisis ordenado de la evolución y estado actual de una tecnología o tema profesional.

3. **Trabajo de Investigación e Innovación**  
   Estudio exploratorio, descriptivo, experimental o analítico, guiado por metodología científica, preferiblemente en vinculación con un grupo de investigación.

4. **Trabajo de Grado en la Industria/Empresa**  
   Desarrollo de tareas específicas en una organización, aplicando conocimientos a problemas reales.

5. **Creación de Empresa**  
   Desarrollo estructurado de una iniciativa empresarial, incluyendo estudio de factibilidad y plan de negocios.

6. **Trabajo Práctico Social**  
   Proyecto de ingeniería con impacto social explícito, que beneficie a una comunidad o sector vulnerable.

7. **Producción Científica**  
   Elaboración de un artículo científico como parte de un proyecto de investigación, aceptado para publicación en una revista indexada.

8. **Profundización Especializada**  
   Aprobación de dos asignaturas de posgrado (maestría o doctorado), sin necesidad de anteproyecto.

---

### 📝 Requisitos Generales y Específicos

- Todas las modalidades (excepto **Producción Científica** y **Profundización Especializada**) deben:
  - Presentar un **informe escrito**.
  - Realizar una **sustentación pública** ante jurados.

- En el caso de **Profundización Especializada**:
  - Las asignaturas deben seleccionarse con aval académico.  
  - No generan costo adicional para estudiantes de pregrado.  
  - Los créditos pueden ser homologados si el estudiante continúa en el programa de posgrado.

---

💡 **En resumen:**  
La Resolución 074 de 2015 formaliza las modalidades de trabajo de grado disponibles para estudiantes de la Facultad de Ingeniería. Establece criterios y lineamientos para cada una, permitiendo que el proceso se adapte a distintas trayectorias académicas y profesionales, garantizando al mismo tiempo calidad, pertinencia y coherencia institucional.

 """)

st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1btn7RiQ6VfDPqg0bepDeYAyXcCwIY9tg/preview"
embed_pdf(pdf_url)