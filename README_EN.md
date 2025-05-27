
# 📘 MauroBot Univalle

> 🇪🇸 [Leer esto en español](README.md)

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
git clone https://github.com/your-username/maurobot-univalle.git
cd maurobot-univalle
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
