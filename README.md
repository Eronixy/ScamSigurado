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
├── archive/                   # Folder for storing screenshots or saved data
└── README.md                  # Project setup and info

````

---

## ⚙️ Requirements

- Python 3.8+
- `virtualenv` or `venv` for managing dependencies

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

### 3. Install Flask

```bash
pip install Flask
```

### 4. Run the Flask app

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
