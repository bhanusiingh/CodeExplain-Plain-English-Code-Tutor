# CodeExplain — Plain-English Code Tutor 🧑‍🏫

> An AI-powered Streamlit application that explains source code in simple English using Google's Gemini API.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📖 **Plain-English Summary** | Understand what the code does at a glance |
| 🔍 **Line-by-Line Explanation** | Every line explained in beginner-friendly language |
| ⏱️ **Time Complexity** | Big-O analysis of algorithms |
| 💾 **Space Complexity** | Memory usage analysis |
| 💡 **Suggested Improvements** | Actionable tips to write better code |
| 🧠 **Quiz Generator** | Test your understanding of the submitted code |

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **Streamlit** — UI framework
- **Google Gemini API** — AI backbone
- **python-dotenv** — Environment variable management
- **Pygments** — Syntax highlighting
- **Markdown** — Formatted output rendering
- **ReportLab** — PDF export *(coming soon)*

---

## 📁 Project Structure

```
CodeExplain-Plain-English-Code-Tutor/
│
├── app.py                  # Streamlit entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── README.md
│
├── assets/                 # Logo, banner images
│
├── services/
│   ├── gemini_service.py   # Gemini API client
│   └── prompts.py          # Prompt templates
│
├── features/
│   ├── explain.py          # Code explanation feature
│   ├── complexity.py       # Complexity analysis
│   ├── quiz.py             # Quiz generation
│   └── suggestions.py      # Improvement suggestions
│
└── utils/
    ├── helpers.py          # General utilities
    └── file_handler.py     # File upload handling
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bhanusiingh/CodeExplain-Plain-English-Code-Tutor.git
cd CodeExplain-Plain-English-Code-Tutor
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
# Copy the example file
cp .env.example .env

# Open .env and add your Gemini API key
GEMINI_API_KEY=your_actual_key_here
```

Get your free API key at: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 5. Run the application

```bash
streamlit run app.py
```

---

## 🔐 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key | ✅ Yes |

---

## 📸 Screenshots

*Coming soon after UI module is complete.*

---

## 📄 License

This project is built for educational purposes as a college project.

---

## 👤 Author

Built with ❤️ using Google Gemini and Streamlit.
