import streamlit as st
from utils.pdf_viewer import embed_pdf

st.title("Calendario Académico 2026-2")
st.markdown("""
## Resolución No. 082 del Consejo Académico de la Universidad del Valle

📅 **Fecha:** 7 de mayo de 2026
🌎 **Aplica a:** Programas académicos de Pregrado del Sistema de Regionalización
🎓 **Período:** Segundo período académico de 2026 (Agosto - Diciembre 2026)

---

### 🧾 Matrícula para admitidos a primer semestre
- Matrícula de asignaturas electivas vía web o en la Dirección del Programa Académico: **11 de agosto**

### 🔁 Matrícula para admitidos por transferencia
- Matrícula académica con la asesoría del director de Programa Académico: **11 de agosto**

### 🧮 Matrícula para estudiantes antiguos
- Matrícula financiera sin recargo: **06 de agosto**
- Matrícula financiera con recargo: **10 de agosto**
- Verificación de deudas en las dependencias: **del 3 al 13 de agosto**
- Matrícula académica: **12, 13 y 14 de agosto**
- Solicitud vía web para cursar asignaturas en otra sede: **12, 13 y 14 de agosto**

### 📚 Desarrollo del semestre
- Inicio de clases: **24 de agosto**
- Inscripción para validaciones en las Direcciones de Programa Académico: **del 24 al 28 de agosto**
- Reporte de calificaciones de validación al Área de Registro Académico: **hasta el 11 de septiembre**
- Adición y cancelación de asignaturas: **14 y 15 de septiembre**
- Cancelación de asignaturas: **8 y 9 de octubre**
- Fecha límite para cancelar semestre: **hasta el 30 de octubre**
- Finalización de clases: **11 de diciembre**
- Exámenes finales: **hasta el 18 de diciembre**
- Finalización del período: **18 de diciembre**

### 📝 Habilitaciones y registro de calificaciones
- Habilitaciones: **hasta el 24 de diciembre**
- Registro de calificaciones: **del 11 de diciembre de 2026 hasta el 14 de enero de 2027**
- Registro de calificaciones en SRA relacionadas con Trabajos de Grado, Pasantías, Prácticas y Convenios: **18 y 19 de febrero de 2027**

---

📌 Resolución firmada en Santiago de Cali por **Guillermo Murillo Vargas** (Rector) y **Rosa Emilia Bermúdez Rico** (Secretaria General).

""")

# Documento embebido (PDF)
st.markdown("### Ver documento:")

pdf_url = "https://drive.google.com/file/d/11Ow1f-lI_hIWDFrvyTbXtD_z77B2vK4V/preview"

embed_pdf(pdf_url)
