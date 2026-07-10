# 🧠 CodeExplain — Plain-English Code Tutor

> An AI-powered educational web application that transforms complex source code into beginner-friendly explanations, interactive quizzes, and structured learning guidance using Google's Gemini AI.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red)
![Gemini](https://img.shields.io/badge/Google-Gemini_AI-orange)
![License](https://img.shields.io/badge/License-Educational-green)

---

# ✨ Features

## 📖 AI Code Explanation

- Plain-English Summary
- Line-by-Line Explanation
- Time Complexity Analysis
- Space Complexity Analysis
- Suggested Improvements

---

## 🎓 Learning Assistant

After every explanation the AI also generates:

- 📚 Concepts Used
- 📖 Prerequisites
- 🎯 Difficulty Level
- 💼 Interview Questions
- ➡ Recommended Next Topic

---

## 🧠 Quiz Generator

Generate an AI-powered multiple-choice quiz based on the uploaded code.

Features include:

- Interactive MCQs
- Instant scoring
- Correct answer feedback
- Beginner-friendly explanations

---

## 📂 File Upload

Upload source code directly.

Supported languages:

- Python
- Java
- C
- C++
- JavaScript

Automatic language detection is performed based on the uploaded file.

---

## 🕘 Session History

- Save previous explanations
- Save quizzes
- Restore previous sessions instantly
- Delete individual history
- Clear history

(No database required — current session only.)

---

## 📤 Export

Export explanations as:

- PDF
- Markdown

---

## 🛡 Production Features

- Robust Gemini API error handling
- Upload validation
- Duplicate request prevention
- Duplicate history prevention
- Friendly user messages
- Session cleanup
- Processing lock during AI requests

---

# 🛠 Tech Stack

- Python 3.12
- Streamlit
- Google Gemini API
- python-dotenv
- ReportLab
- Markdown
- Pygments

---

# 📁 Project Structure

```
CodeExplain-Plain-English-Code-Tutor/

│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── assets/
│
├── features/
│   ├── explain.py
│   ├── quiz.py
│   └── learning.py
│
├── services/
│   ├── gemini_service.py
│   └── prompts.py
│
└── utils/
    ├── file_handler.py
    ├── helpers.py
    └── history_manager.py
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/bhanusiingh/CodeExplain-Plain-English-Code-Tutor.git

cd CodeExplain-Plain-English-Code-Tutor
```

Create a virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create `.env`

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Run

```bash
streamlit run app.py
```

---

# 📸 Screenshots

> Screenshots will be updated after the upcoming Phase 2 UI redesign.

---

# 🗺 Roadmap

## ✅ Phase 1 (Completed)

- AI Code Explanation
- Quiz Generator
- Learning Assistant
- File Upload
- Session History
- PDF Export
- Markdown Export
- Production Ready

## 🚀 Phase 2 (Planned)

- Modern UI Redesign
- Inline File Upload
- Analysis / Quiz View Switching
- Google Authentication
- Cloud History
- Responsive Design
- Enhanced Animations
- Improved Theme System

---

# 👨‍💻 Author

**Bhanu Pratap Singh**

Built using **Python**, **Streamlit**, and **Google Gemini AI** as an educational project focused on helping beginners understand programming through AI-assisted explanations.

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
