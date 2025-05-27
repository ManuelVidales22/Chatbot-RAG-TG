
# 📘 MauroBot Univalle

> 🇺🇸 [Read this in English](README_EN.md)

MauroBot es un chatbot construido con Streamlit y LangChain, diseñado para responder preguntas relacionadas con el programa de Ingeniería de Sistemas de la Universidad del Valle, Sede Tuluá. Utiliza procesamiento de lenguaje natural y recuperación de información basada en documentos oficiales de la universidad.

---

## 🚀 Requisitos

- Python 3.10
- Git
- pipenv (opcional) o virtualenv
- Tesseract OCR
- Navegador web moderno

---

## 📦 Instalación

### 1. Clona este repositorio

```bash
git clone https://github.com/tu-usuario/maurobot-univalle.git
cd maurobot-univalle
```

### 2. Crea un entorno virtual con alguna herramienta como pipenv o venv

####pipenv

```bash
pip install pipenv
pipenv install
pipenv shell
```

####venv

```bash
python -m venv .venv
source .venv/bin/activate      # En Linux/Mac
.venv\Scripts\activate         # En Windows
pip install -r requirements.txt
```

---

## 🔤 Configurar spaCy

1. Instala el modelo de español:

```bash
python -m spacy download es_core_news_sm
```

2. (Opcional) Verifica que esté instalado:

```bash
python -m spacy validate
```

---

## 📷 Instalar Tesseract OCR

### En Windows

- Descarga desde: https://github.com/tesseract-ocr/tesseract
- Instálalo y copia la ruta de instalación (por ejemplo: `C:\Program Files\Tesseract-OCR\tesseract.exe`)

```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### En Linux

```bash
sudo apt update && sudo apt install tesseract-ocr
```

### En MacOS

```bash
brew install tesseract
```

---

## 🔑 Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
API_KEY=tu_api_key_de_openai
```

---

## ▶️ Ejecutar la aplicación

Una vez instaladas las dependencias y configuradas las variables:

```bash
streamlit run main.py
```

La app se abrirá automáticamente en tu navegador (generalmente en http://localhost:8501).

---

## 📌 Notas adicionales

- Puedes cargar nuevos documentos en la carpeta `data/pdfs/`. Serán procesados automáticamente.
- La aplicación puede ejecutarse en Windows, Linux o Mac sin cambios en el código.




