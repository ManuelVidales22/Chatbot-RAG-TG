
# 📘 MauroBot Univalle

MauroBot is a chatbot built with Streamlit and LangChain, designed to answer questions related to the Systems Engineering program at Universidad del Valle, Tuluá campus. It uses natural language processing and information retrieval based on official university documents.

---

## 🚀 Requirements

- Python 3.10
- Git
- pipenv (optional) or virtualenv
- Tesseract OCR
- Modern web browser

---

## 📦 Installation

### 1. Clone this repository

```bash
git clone git@github.com:JuanArango30/Chatbot-RAG-TG.git
cd Chatbot-RAG-TG
```

### 2. Create a virtual environment using pipenv or venv

#### pipenv

```bash
pip install pipenv
pipenv install
pipenv shell
```

#### venv

```bash
python -m venv .venv
source .venv/bin/activate      # On Linux/Mac
.venv\Scripts\activate         # On Windows
pip install -r requirements.txt
```

---

## 🔤 Setup spaCy

1. Install the Spanish language model:

```bash
python -m spacy download es_core_news_sm
```

2. (Optional) Validate installation:

```bash
python -m spacy validate
```

---

## 📷 Install Tesseract OCR

### On Windows

- Download from: https://github.com/tesseract-ocr/tesseract
- Install it and copy the installation path (e.g.: `C:\Program Files\Tesseract-OCR\tesseract.exe`)

```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### On Linux

```bash
sudo apt update && sudo apt install tesseract-ocr
```

### On macOS

```bash
brew install tesseract
```

---

## 🔑 Set up environment variables

Create a `.env` file in the root directory of the project with the following content:

```env
API_KEY=your_openai_api_key
```

---

## ▶️ Run the application

Once dependencies are installed and variables are configured:

```bash
streamlit run main.py
```

The app will automatically open in your browser (usually at http://localhost:8501).

---

## 📌 Additional notes

- You can add new documents to the `data/pdfs/` folder. They will be processed automatically.
- The application can run on Windows, Linux, or macOS without code changes.



---




# 📘 MauroBot Univalle

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




