# ScamSigurado

ScamSigurado is a scam detection web application built with Flask, Tailwind CSS (via CDN), and JavaScript. It uses a multimodal approach to analyze both text and image content in uploaded screenshots to detect Filipino-targeted online scams.

---

## 📁 Project Structure

```

ScamSigurado/
├── app.py                     # Main Flask application
├── venv/                      # Python virtual environment
├── templates/
│   └── index.html             # Main frontend page using Jinja2
├── static/
│   └── custom.js              # JavaScript for frontend behavior
├── models/                    # Folder for ML/DL model files
├── uploads/                   # Folder for temporary uploads
├── archive/                   # Folder for storing screenshots or saved data
├── requirements.txt           # Python dependencies list
└── README.md                  # Project setup and info

````

---

## ⚙️ Requirements

- Python 3.8+
- `virtualenv` or `venv` for managing dependencies
- Tesseract OCR (installed separately)

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Eronixy/ScamSigurado.git
cd ScamSigurado
````

### 2. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If you don't have `requirements.txt`, you can create one with:
>
> ```bash
> pip freeze > requirements.txt
> ```

### 4. Install Tesseract OCR

* **Linux (Debian/Ubuntu):**

  ```bash
  sudo apt install tesseract-ocr
  ```

* **macOS (with Homebrew):**

  ```bash
  brew install tesseract
  ```

* **Windows:**

  1. Download the installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
  2. Install and add the path to your system environment variables PATH.
  3. Example path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

---

### 5. Run the Flask app

```bash
python app.py
```

Then open your browser and go to:
👉 `http://127.0.0.1:5000/`

---

## 🧠 Authors

* Irron Jovic Jun V. Brosoto
* Jezrielle Anne G. Padlan
* Julia Kyla C. Rustia
* Catherine C. Tabigne

---

## 📄 License

This project is for academic and research purposes only. Commercial use is not permitted without prior consent.

