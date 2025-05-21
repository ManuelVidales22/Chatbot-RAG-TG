import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Proyecto Educativo del Programa res 048")
st.markdown("""
## Proyecto Educativo del Programa (PEP)  
### Ingeniería de Sistemas – Universidad del Valle

📅 **Versión:** Octubre de 2009  
🏫 **Programa:** Ingeniería de Sistemas  
📘 **Propósito:** Establecer el marco fundamental para la formación profesional en Ingeniería de Sistemas, en coherencia con los principios institucionales.

---

### 🎯 Misión y Objetivos del Programa
- **Misión:** Formar profesionales integrales, creativos, éticos y agentes de cambio.
- **Objetivos:**
  - Abordar la transformación computacional de la información.
  - Resolver problemas reales.
  - Comprender fundamentos teóricos.
  - Mantenerse actualizados tecnológicamente.

### 👤 Perfil del Aspirante y del Profesional
- **Aspirante:**  
  - Habilidades en matemáticas y ciencias básicas.
  - Interés en la tecnología y el pensamiento lógico.
- **Egresado:**  
  - Capacidad para diagnosticar, diseñar, evaluar, auditar y mantener sistemas.
  - Énfasis en:
    - Tecnologías informáticas.
    - Desarrollo de software.
    - Redes y telecomunicaciones.
    - Bases de datos.
    - Internet.

### 📚 Lineamientos Curriculares
- **Ambiente de aprendizaje:** Integra docencia, investigación y proyección social.
- **Docencia:** El profesor como guía del proceso formativo.
- **Investigación:** Fomento de habilidades investigativas.
- **Proyección social:** Articulación con el entorno.
- **Internacionalización:** Inserción en redes académicas globales.

### 🚀 Metas de Desarrollo
- Crear ambientes adecuados de aprendizaje.
- Integrar funciones sustantivas: docencia, investigación y proyección social.
- Consolidar liderazgo local, regional, nacional e internacional.

### 🧮 Sistema de Créditos
- **Total de créditos:** 159  
- Distribución:
  - Asignaturas básicas obligatorias.
  - Asignaturas profesionales obligatorias.
  - Electivas profesionales.
  - Electivas complementarias.

### 🛠️ Gestión del Programa
- **Aseguramiento de la calidad:** Autoevaluación periódica.
- **Planeación y evaluación:** Políticas para la mejora continua.
- **Soporte institucional:** Directrices para la gestión académica.
- **Actualización del PEP:** Mecanismos de revisión, discusión y difusión.

---

💡 **En resumen:**  
Este documento funciona como una hoja de ruta que define la identidad del programa, sus propósitos formativos, la estructura curricular y las estrategias de gestión, con el objetivo de garantizar una formación de alta calidad, pertinente y alineada con las necesidades de la sociedad.

 """)

st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/15NqDdOPY12cqqEK8q8V7UTm1FUs0kf-y/preview"
embed_pdf(pdf_url)