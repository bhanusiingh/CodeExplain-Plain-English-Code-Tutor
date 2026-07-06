"""
app.py
------
CodeExplain: Plain-English Code Tutor
Entry point — Streamlit UI Shell (Module 1)

Includes: sidebar, language selector, code editor,
          explain/quiz buttons, output placeholders, footer.
No Gemini API calls in this module.
"""

import streamlit as st

# ── Page configuration (MUST be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="CodeExplain — Plain-English Code Tutor",
    page_icon="🧑‍🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global CSS ────────────────────────────────────────────────────────────────
def load_css() -> None:
    """Inject custom CSS for the modern dark-themed UI."""
    st.markdown(
        """
        <style>
        /* ── Google Font ──────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Root & Base ──────────────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Dark background for entire app */
        .stApp {
            background: linear-gradient(135deg, #0d1117 0%, #0f1923 50%, #0d1117 100%);
            color: #e6edf3;
        }

        /* Hide default Streamlit header/footer */
        #MainMenu, footer, header { visibility: hidden; }

        /* ── Sidebar ──────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
            border-right: 1px solid #21262d;
        }

        [data-testid="stSidebar"] * {
            color: #e6edf3 !important;
        }

        /* ── Hero Banner ──────────────────────────────────────────────────── */
        .hero-banner {
            background: linear-gradient(135deg, #1a2744 0%, #0f2d4a 40%, #1a1a3e 100%);
            border: 1px solid #30363d;
            border-radius: 16px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
        }

        .hero-banner::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(88, 166, 255, 0.08) 0%, transparent 70%);
            pointer-events: none;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #58a6ff 0%, #a371f7 50%, #79c0ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 0.4rem 0;
            line-height: 1.2;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #8b949e;
            font-weight: 400;
            margin: 0;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(88, 166, 255, 0.12);
            border: 1px solid rgba(88, 166, 255, 0.3);
            color: #58a6ff;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-bottom: 1rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        /* ── Section Labels ───────────────────────────────────────────────── */
        .section-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }

        /* ── Code Editor Container ────────────────────────────────────────── */
        .code-editor-wrapper {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 1rem;
            transition: border-color 0.2s ease;
        }

        .code-editor-wrapper:hover {
            border-color: #58a6ff;
        }

        .editor-topbar {
            background: #161b22;
            border-bottom: 1px solid #21262d;
            padding: 0.6rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }

        .dot-red   { background: #ff5f57; }
        .dot-yellow{ background: #ffbd2e; }
        .dot-green { background: #28c840; }

        .editor-filename {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #8b949e;
            margin-left: 0.5rem;
        }

        /* Style the textarea inside code editor */
        .code-editor-wrapper textarea {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.9rem !important;
            background: #0d1117 !important;
            color: #e6edf3 !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 1rem !important;
            line-height: 1.6 !important;
        }

        /* ── Buttons ──────────────────────────────────────────────────────── */
        .stButton > button {
            width: 100%;
            padding: 0.75rem 1.5rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.25s ease;
            letter-spacing: 0.02em;
        }

        /* Primary — Explain button */
        div[data-testid="column"]:nth-child(1) .stButton > button {
            background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(31, 111, 235, 0.35);
        }

        div[data-testid="column"]:nth-child(1) .stButton > button:hover {
            background: linear-gradient(135deg, #388bfd 0%, #58a6ff 100%);
            box-shadow: 0 6px 20px rgba(31, 111, 235, 0.5);
            transform: translateY(-2px);
        }

        /* Secondary — Quiz button */
        div[data-testid="column"]:nth-child(2) .stButton > button {
            background: linear-gradient(135deg, #6e40c9 0%, #a371f7 100%);
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(110, 64, 201, 0.35);
        }

        div[data-testid="column"]:nth-child(2) .stButton > button:hover {
            background: linear-gradient(135deg, #a371f7 0%, #d2a8ff 100%);
            box-shadow: 0 6px 20px rgba(110, 64, 201, 0.5);
            transform: translateY(-2px);
        }

        /* Clear button */
        div[data-testid="column"]:nth-child(3) .stButton > button {
            background: transparent;
            color: #8b949e;
            border: 1px solid #30363d !important;
        }

        div[data-testid="column"]:nth-child(3) .stButton > button:hover {
            background: #21262d;
            color: #e6edf3;
            border-color: #8b949e !important;
        }

        /* ── Selectbox ────────────────────────────────────────────────────── */
        [data-testid="stSelectbox"] > div > div {
            background: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
            color: #e6edf3 !important;
        }

        /* ── Info / Warning boxes ─────────────────────────────────────────── */
        .stAlert {
            border-radius: 10px !important;
            border: 1px solid #30363d !important;
        }

        /* ── Output placeholder card ──────────────────────────────────────── */
        .output-card {
            background: #161b22;
            border: 1px solid #21262d;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .output-card-title {
            font-size: 1rem;
            font-weight: 600;
            color: #58a6ff;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .output-placeholder {
            color: #484f58;
            font-style: italic;
            font-size: 0.9rem;
            text-align: center;
            padding: 2rem;
        }

        /* ── Sidebar Logo Block ───────────────────────────────────────────── */
        .sidebar-logo {
            background: linear-gradient(135deg, #1a2744, #1a1a3e);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .sidebar-logo-icon {
            font-size: 3rem;
            line-height: 1;
        }

        .sidebar-logo-text {
            font-size: 1rem;
            font-weight: 700;
            background: linear-gradient(135deg, #58a6ff, #a371f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-top: 0.4rem;
        }

        .sidebar-logo-sub {
            font-size: 0.72rem;
            color: #484f58;
            margin-top: 0.2rem;
        }

        /* ── Sidebar Info Cards ───────────────────────────────────────────── */
        .sidebar-info-card {
            background: #0d1117;
            border: 1px solid #21262d;
            border-radius: 10px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.75rem;
        }

        .sidebar-info-title {
            font-size: 0.7rem;
            font-weight: 600;
            color: #484f58;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.4rem;
        }

        .sidebar-info-value {
            font-size: 0.88rem;
            color: #8b949e;
        }

        /* ── Feature pills ────────────────────────────────────────────────── */
        .feature-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: rgba(88, 166, 255, 0.08);
            border: 1px solid rgba(88, 166, 255, 0.2);
            border-radius: 20px;
            padding: 0.3rem 0.75rem;
            font-size: 0.8rem;
            color: #58a6ff;
            margin: 0.2rem;
        }

        /* ── Divider ──────────────────────────────────────────────────────── */
        .custom-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #30363d, transparent);
            margin: 1.5rem 0;
        }

        /* ── Footer ───────────────────────────────────────────────────────── */
        .footer {
            background: #161b22;
            border: 1px solid #21262d;
            border-radius: 12px;
            padding: 1.25rem 2rem;
            text-align: center;
            margin-top: 2.5rem;
            color: #484f58;
            font-size: 0.82rem;
        }

        .footer a {
            color: #58a6ff;
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        /* ── Expander ─────────────────────────────────────────────────────── */
        [data-testid="stExpander"] {
            background: #161b22 !important;
            border: 1px solid #21262d !important;
            border-radius: 10px !important;
            margin-bottom: 0.75rem;
        }

        [data-testid="stExpander"] summary {
            color: #e6edf3 !important;
            font-weight: 500;
        }

        /* ── Scrollbar ────────────────────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0d1117; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #484f58; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar() -> tuple[str, str]:
    """
    Render the sidebar with logo, settings, and info.

    Returns:
        tuple: (selected_language, selected_mode)
    """
    with st.sidebar:
        # Logo block
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="sidebar-logo-icon">🧑‍🏫</div>
                <div class="sidebar-logo-text">CodeExplain</div>
                <div class="sidebar-logo-sub">Plain-English Code Tutor</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Language selector
        st.markdown(
            '<p class="section-label">⚙️ &nbsp;Settings</p>',
            unsafe_allow_html=True,
        )

        selected_language = st.selectbox(
            "Programming Language",
            options=["Python", "Java", "JavaScript", "C++", "C"],
            index=0,
            help="Select the language of the code you are pasting.",
            key="language_selector",
        )

        selected_mode = st.selectbox(
            "Explanation Depth",
            options=["Beginner", "Intermediate", "Advanced"],
            index=0,
            help="Choose how detailed the explanation should be.",
            key="mode_selector",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Features info
        st.markdown(
            '<p class="section-label">✨ &nbsp;Features</p>',
            unsafe_allow_html=True,
        )
        features = [
            ("📖", "Plain-English Summary"),
            ("🔍", "Line-by-Line Breakdown"),
            ("⏱️", "Time Complexity"),
            ("💾", "Space Complexity"),
            ("💡", "Improvement Tips"),
            ("🧠", "Quiz Generator"),
        ]
        pills_html = "".join(
            f'<span class="feature-pill">{icon} {label}</span>'
            for icon, label in features
        )
        st.markdown(pills_html, unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # How to use
        st.markdown(
            '<p class="section-label">📋 &nbsp;How to Use</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="sidebar-info-card">
                <div class="sidebar-info-title">Step 1</div>
                <div class="sidebar-info-value">Paste your code in the editor</div>
            </div>
            <div class="sidebar-info-card">
                <div class="sidebar-info-title">Step 2</div>
                <div class="sidebar-info-value">Select programming language</div>
            </div>
            <div class="sidebar-info-card">
                <div class="sidebar-info-title">Step 3</div>
                <div class="sidebar-info-value">Click <strong>Explain Code</strong> or <strong>Generate Quiz</strong></div>
            </div>
            <div class="sidebar-info-card">
                <div class="sidebar-info-title">Step 4</div>
                <div class="sidebar-info-value">Read the AI-generated analysis below</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Version info
        st.markdown(
            """
            <div style="text-align:center; color:#484f58; font-size:0.75rem;">
                v1.0.0 &nbsp;·&nbsp; Powered by Gemini &nbsp;·&nbsp; 🇮🇳
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_language, selected_mode


# ── Hero Banner ───────────────────────────────────────────────────────────────
def render_hero() -> None:
    """Render the top hero banner with title and subtitle."""
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-badge">AI-Powered · Google Gemini</div>
            <h1 class="hero-title">🧑‍🏫 CodeExplain</h1>
            <p class="hero-subtitle">
                Paste any code snippet and instantly get a plain-English explanation,
                complexity analysis, improvement suggestions, and an interactive quiz —
                all powered by Google Gemini AI.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Code Input Area ───────────────────────────────────────────────────────────
def render_code_input(language: str) -> str:
    """
    Render the code editor with a styled topbar.

    Args:
        language: Selected programming language (for filename hint).

    Returns:
        str: The code entered by the user.
    """
    extension_map = {
        "Python": "main.py",
        "Java": "Main.java",
        "JavaScript": "index.js",
        "C++": "main.cpp",
        "C": "main.c",
    }
    filename = extension_map.get(language, "code.txt")

    # Styled editor topbar (decorative)
    st.markdown(
        f"""
        <div class="code-editor-wrapper">
            <div class="editor-topbar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="editor-filename">{filename}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Placeholder samples per language
    placeholder_map = {
        "Python": (
            "# Paste your Python code here\n\n"
            "def bubble_sort(arr):\n"
            "    n = len(arr)\n"
            "    for i in range(n):\n"
            "        for j in range(0, n - i - 1):\n"
            "            if arr[j] > arr[j + 1]:\n"
            "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
            "    return arr"
        ),
        "Java": (
            "// Paste your Java code here\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"Hello, World!\");\n"
            "    }\n"
            "}"
        ),
        "JavaScript": "// Paste your JavaScript code here\n\nconsole.log('Hello, World!');",
        "C++": "// Paste your C++ code here\n\n#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << \"Hello!\" << endl;\n    return 0;\n}",
        "C": "// Paste your C code here\n\n#include <stdio.h>\n\nint main() {\n    printf(\"Hello!\\n\");\n    return 0;\n}",
    }

    code = st.text_area(
        label="Code Editor",
        placeholder=placeholder_map.get(language, "Paste your code here..."),
        height=320,
        key="code_input",
        label_visibility="collapsed",
    )
    return code


# ── Action Buttons ────────────────────────────────────────────────────────────
def render_action_buttons() -> tuple[bool, bool, bool]:
    """
    Render the Explain, Quiz, and Clear action buttons.

    Returns:
        tuple: (explain_clicked, quiz_clicked, clear_clicked)
    """
    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:
        explain_clicked = st.button(
            "⚡ Explain Code",
            key="btn_explain",
            use_container_width=True,
        )
    with col2:
        quiz_clicked = st.button(
            "🧠 Generate Quiz",
            key="btn_quiz",
            use_container_width=True,
        )
    with col3:
        clear_clicked = st.button(
            "🗑️ Clear",
            key="btn_clear",
            use_container_width=True,
        )

    return explain_clicked, quiz_clicked, clear_clicked


# ── Output Section (Placeholder) ──────────────────────────────────────────────
def render_output_placeholder() -> None:
    """
    Display placeholder output cards before any code is analysed.
    Real output rendering is implemented in Module 4.
    """
    sections = [
        ("📖", "Summary",                   "A plain-English overview of what the code does."),
        ("🔍", "Line-by-Line Explanation",  "Each line explained in simple terms."),
        ("⏱️", "Time Complexity",            "Big-O notation and performance analysis."),
        ("💾", "Space Complexity",           "Memory usage breakdown."),
        ("💡", "Suggested Improvements",    "Actionable tips to make the code better."),
        ("🧠", "Quiz",                       "Test your understanding with AI-generated questions."),
    ]

    st.markdown(
        '<div class="custom-divider"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="section-label">📊 &nbsp;Analysis Results</p>',
        unsafe_allow_html=True,
    )

    for icon, title, description in sections:
        with st.expander(f"{icon}  {title}", expanded=False):
            st.markdown(
                f"""
                <div class="output-placeholder">
                    <strong>{description}</strong><br><br>
                    Paste your code above and click <em>Explain Code</em> to see results here.
                </div>
                """,
                unsafe_allow_html=True,
            )


# ── Output Section (Filled) ───────────────────────────────────────────────────
def render_filled_output(results: dict) -> None:
    """
    Render filled analysis output after Gemini responds.
    Called by Module 4 — stub only here.

    Args:
        results: Dictionary with keys matching each output section.
    """
    # This function is intentionally left as a stub.
    # Full implementation is added in the Features module.
    st.info("Full output rendering will be connected in Module 4.", icon="🔧")


# ── Footer ────────────────────────────────────────────────────────────────────
def render_footer() -> None:
    """Render the app footer."""
    st.markdown(
        """
        <div class="footer">
            <strong>CodeExplain</strong> &nbsp;·&nbsp;
            Plain-English Code Tutor &nbsp;·&nbsp;
            Powered by
            <a href="https://ai.google.dev/" target="_blank">Google Gemini</a>
            &nbsp;·&nbsp;
            Built with
            <a href="https://streamlit.io" target="_blank">Streamlit</a>
            &nbsp;·&nbsp;
            🎓 College Project
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Main App ──────────────────────────────────────────────────────────────────
def main() -> None:
    """Main application entry point."""
    # 1. Load global styles
    load_css()

    # 2. Render sidebar — returns user selections
    language, mode = render_sidebar()

    # 3. Hero banner
    render_hero()

    # 4. Code input section
    st.markdown(
        '<p class="section-label">✏️ &nbsp;Code Editor</p>',
        unsafe_allow_html=True,
    )
    code = render_code_input(language)

    # 5. Action buttons
    explain_clicked, quiz_clicked, clear_clicked = render_action_buttons()

    # 6. Handle Clear button
    if clear_clicked:
        st.session_state["code_input"] = ""
        st.rerun()

    # 7. Handle Explain / Quiz buttons (Module 3+ will fill these in)
    if explain_clicked or quiz_clicked:
        if not code or not code.strip():
            st.warning(
                "⚠️  Please paste some code before clicking the button.",
                icon="⚠️",
            )
        else:
            action = "explanation" if explain_clicked else "quiz"
            st.info(
                f"✅  Code received ({len(code.splitlines())} lines · {language})  "
                f"— **{action.capitalize()}** will be generated once the "
                f"Gemini service is connected in Module 3.",
                icon="🔧",
            )

    # 8. Output area
    render_output_placeholder()

    # 9. Footer
    render_footer()


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
