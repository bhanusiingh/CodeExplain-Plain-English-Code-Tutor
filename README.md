# 🧠 CodeExplain — AI-Powered Plain-English Code Tutor

> An AI-powered educational web application that transforms complex source code into beginner-friendly explanations, interactive quizzes, and structured learning guidance using Google's Gemini AI.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red)
![Gemini](https://img.shields.io/badge/Google-Gemini_AI-orange)
![Firebase](https://img.shields.io/badge/Firebase-Authentication-yellow)
![Firestore](https://img.shields.io/badge/Firestore-Cloud_History-orange)
![License](https://img.shields.io/badge/License-Educational-green)

---

# ✨ Features

## 💻 Monaco Code Editor

- VS Code-like editing experience
- Syntax highlighting
- Auto indentation
- Bracket matching
- Auto-closing brackets
- Line numbers
- Code folding
- Word wrap
- Multi-language support

---

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

## 🧠 AI Quiz Generator

Generate AI-powered multiple-choice quizzes based on the uploaded code.

Features include:

- Interactive MCQs
- Instant scoring
- Correct answer feedback
- Beginner-friendly explanations

---

## 🔐 Authentication & Cloud Sync

- Secure Email & Password Authentication
- Firebase Authentication
- Persistent User Sessions
- Cloud History Synchronization
- Logout & Session Management

---

## 📂 File Upload

Upload source code directly.

Supported Languages:

- Python
- Java
- C
- C++
- JavaScript

Automatic language detection is performed based on the uploaded file.

---

## ☁ Cloud History

Every authenticated user gets their own persistent history.

Features include:

- Automatic Cloud Synchronization
- Restore Previous Sessions
- Cross-Device Access
- Delete Individual History
- Local Fallback when Cloud is Unavailable

---

## 📤 Export

Export explanations as:

- PDF
- Markdown

---

## 🎨 Modern User Interface

- Modern Workspace Layout
- Glassmorphism Login Screen
- Monaco Code Editor
- Interactive Analysis Cards
- Responsive Layout Improvements
- Processing Lock During AI Requests

---

## 🛡 Production Features

- Robust Gemini API Error Handling
- Upload Validation
- Duplicate Request Prevention
- Duplicate History Prevention
- Friendly User Messages
- Session Cleanup
- Firebase Authentication
- Firestore Cloud Storage

---

# 🌟 Highlights

- ✅ AI-powered code explanations using Google Gemini
- ✅ VS Code-like Monaco Editor
- ✅ Beginner-friendly learning experience
- ✅ Interactive quiz generation
- ✅ Firebase Authentication
- ✅ Persistent Cloud History
- ✅ PDF & Markdown Export
- ✅ Modern Glassmorphism Login UI
- ✅ Production-ready architecture

---

# 🛠 Tech Stack

- Python 3.12
- Streamlit
- Monaco Editor
- Google Gemini API
- Firebase Authentication
- Firebase Firestore
- Firebase Admin SDK
- python-dotenv
- ReportLab
- Markdown
- Pygments
- Requests

---

# 📁 Project Structure

```text
CodeExplain-Plain-English-Code-Tutor/

│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml.example
│
├── assets/
│   ├── banner.png
│   ├── login.png
│   └── logo.png
│
├── features/
│   ├── complexity.py
│   ├── explain.py
│   ├── learning.py
│   ├── quiz.py
│   ├── suggestions.py
│   └── __init__.py
│
├── services/
│   ├── auth_ui.py
│   ├── firebase_service.py
│   ├── gemini_service.py
│   ├── monaco_editor.py
│   ├── prompts.py
│   ├── __init__.py
│   └── monaco_component/
│       └── index.html
│
└── utils/
    ├── file_handler.py
    ├── helpers.py
    ├── history_manager.py
    └── __init__.py
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

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

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

Configure Firebase

Create:

```text
.streamlit/secrets.toml
```

using

```text
.streamlit/secrets.toml.example
```

and insert your Firebase credentials.

Run the application

```bash
streamlit run app.py
```

---

# 📸 Screenshots

> Screenshots will be updated after deployment.

Current UI includes:

- 🔐 Glassmorphism Login
- 💻 Monaco Code Editor
- 📖 AI Explanation Dashboard
- 🧠 Quiz Generator
- ☁ Cloud History

---

# 🗺 Roadmap

## ✅ Phase 1 (Completed)

- AI Code Explanation
- Learning Assistant
- Quiz Generator
- File Upload
- Session History
- PDF Export
- Markdown Export
- Production Features

---

## ✅ Phase 2 (Completed)

- Modern Workspace UI
- Monaco Code Editor
- Improved Analysis Cards
- Processing Lock
- Firebase Authentication
- Glassmorphism Login
- Persistent Cloud History
- Responsive Authentication UI
- Deployment

---

## 🚀 Phase 3 (Planned)

- Light / Dark Theme
- Responsive Workspace
- Codebase Refactoring
- Performance Optimization
- Deployment
- Final UI Polish

---

# ☁ Deployment

Designed for deployment using:

- Streamlit Community Cloud
- Firebase Authentication
- Firebase Firestore

---

# 👨‍💻 Author

**Bhanu Pratap Singh**

Built using **Python**, **Streamlit**, **Google Gemini AI**, **Firebase**, and **Monaco Editor** as an educational project focused on helping beginners understand programming through AI-assisted explanations.

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.