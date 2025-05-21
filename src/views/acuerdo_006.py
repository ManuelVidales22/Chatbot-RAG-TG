import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Acuerdo 006 de 2023")
st.markdown("""
## Acuerdo No. 006 del Consejo Superior de la Universidad del Valle

📅 **Fecha:** 28 de junio de 2023  
📘 **Modifica:** Capítulo VIII del Acuerdo 009 de 1997 (Reglamento Estudiantil de Pregrado)

---

Este documento tiene como objetivo **actualizar las disposiciones sobre el bajo rendimiento académico** en la Universidad del Valle, alineándose con las dinámicas institucionales y las necesidades de la comunidad académica.

Se fundamenta en el principio de **autonomía universitaria**, la **Ley 30 de 1992**, y los lineamientos de **modernización académica** de la universidad.

### 🛠️ Principales modificaciones:

- **Definición de bajo rendimiento académico**  
  Se actualizan las situaciones que constituyen bajo rendimiento.  
  *(Art. 59°)*

- **Notificación y acompañamiento**  
  Se establece el procedimiento de notificación al estudiante y la implementación de estrategias de acompañamiento por parte de la universidad.  
  *(Art. 60° y 61°)*

- **Condiciones para continuar estudios**  
  Se definen requisitos como el promedio, avance en el programa y participación en programas de acompañamiento para los estudiantes reincidentes.  
  *(Art. 62° y 63°)*

- **Reingreso y restricciones**  
  Se fijan condiciones y plazos para el reingreso tras el retiro por bajo rendimiento, con límite de intentos y excepciones por fuerza mayor.  
  *(Parágrafos del Art. 63°)*

- **Acumulación de bajos rendimientos**  
  Se mantiene el carácter acumulativo, con excepción para quienes reingresan tras tres o más bajos rendimientos y pasan al menos tres periodos académicos fuera.  
  *(Art. 64°)*

- **Rol de la Dirección de Desarrollo Estudiantil y Éxito Académico**  
  Será responsable de coordinar la prevención, acompañamiento y seguimiento a estudiantes con bajo rendimiento.  
  *(Art. 2° del Acuerdo 006)*

- **Facultades al Consejo Académico**  
  Se le autoriza a reglamentar una estrategia integral de acompañamiento y retención estudiantil.  
  *(Art. 3° del Acuerdo 006)*

---

📌 **Entrada en vigencia:** Primer semestre de 2024  
🔒 **Lo no modificado:** Las demás disposiciones del Acuerdo 009 de 1997 siguen vigentes.

""")

# Documento embebido (PDF)
st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/1k1SiW-ukKD9jUapTJf75Y8C2vRfyZyJ9/preview"

embed_pdf(pdf_url)