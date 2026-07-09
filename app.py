"""
app.py
------
CodeExplain: Plain-English Code Tutor
Entry point — Streamlit UI (Module 4)

Includes: sidebar, language selector, code editor,
          explain/quiz buttons, live Gemini output, footer.
Module 4: Explain Code pipeline fully connected.
"""

from pathlib import Path
import streamlit as st
from features.explain import (
    run_explanation,
    SECTION_SUMMARY,
    SECTION_LINE_BY_LINE,
    SECTION_TIME,
    SECTION_SPACE,
    SECTION_IMPROVEMENTS,
)
from features.quiz import run_quiz
from services.gemini_service import get_api_key_info
from utils.file_handler import (
    read_uploaded_file,
    detect_language,
    supported_extensions,
)
from utils.helpers import (
    generate_pdf,
    generate_markdown,
    format_export_text,
)

# ── Asset paths ───────────────────────────────────────────────────────────────
_ASSETS_DIR = Path(__file__).parent / "assets"
_LOGO_PATH  = _ASSETS_DIR / "logo.png"
_BANNER_PATH = _ASSETS_DIR / "banner.png"

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
        # Logo block — use real logo.png if available, else emoji fallback
        if _LOGO_PATH.exists():
            st.image(str(_LOGO_PATH), use_container_width=True)
        else:
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

        # Version + API key diagnostic (shows only first 8 chars — never full key)
        key_info: str = get_api_key_info()
        st.markdown(
            f"""
            <div style="text-align:center; color:#484f58; font-size:0.75rem;">
                v1.0.0 &nbsp;·&nbsp; Powered by Gemini &nbsp;·&nbsp; 🇮🇳
            </div>
            <div style="text-align:center; color:#30363d; font-size:0.68rem; margin-top:0.4rem;
                        font-family:'JetBrains Mono',monospace;">
                Key: {key_info}
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_language, selected_mode


# ── Hero Banner ───────────────────────────────────────────────────────────────
def render_hero() -> None:
    """Render the top hero banner — uses banner.png if present, else CSS fallback."""
    if _BANNER_PATH.exists():
        st.image(str(_BANNER_PATH), use_container_width=True)
    else:
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
def render_filled_output(results: dict[str, str]) -> None:
    """
    Render the five analysis sections returned by run_explanation().

    Each section is displayed inside an auto-expanded expander so the user
    can collapse sections they are not interested in.

    Args:
        results (dict[str, str]): Parsed sections from the explain pipeline.
                                  Keys are the SECTION_* constants from
                                  features/explain.py.
    """
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-label">📊 &nbsp;Analysis Results</p>',
        unsafe_allow_html=True,
    )

    sections_config: list[tuple[str, str, str]] = [
        ("📖", "Summary",                  SECTION_SUMMARY),
        ("🔍", "Line-by-Line Explanation", SECTION_LINE_BY_LINE),
        ("⏱️", "Time Complexity",           SECTION_TIME),
        ("💾", "Space Complexity",          SECTION_SPACE),
        ("💡", "Suggested Improvements",   SECTION_IMPROVEMENTS),
    ]

    for icon, title, key in sections_config:
        content: str = results.get(key, "Section not available.")
        with st.expander(f"{icon}  {title}", expanded=True):
            st.markdown(content)

    # Export buttons immediately below the analysis sections.
    render_export_buttons(results)


# ── Export Buttons ───────────────────────────────────────────────────────────────
def render_export_buttons(results: dict[str, str] | None = None) -> None:
    """
    Render the three export action buttons below Analysis Results.

    Buttons:
        • Download PDF      — uses generate_pdf()        from utils/helpers.py
        • Download Markdown — uses generate_markdown()   from utils/helpers.py
        • Copy Result       — uses format_export_text()  via st.components

    When results is None or empty the buttons are disabled and a friendly
    message is shown.  No exception is ever surfaced to the user.

    Args:
        results (dict[str, str] | None): Parsed explanation sections.
    """
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-label">📤 &nbsp;Export Results</p>',
        unsafe_allow_html=True,
    )

    has_results: bool = bool(results and isinstance(results, dict) and
                             "error" not in results)

    if not has_results:
        st.info(
            "Run **Explain Code** first to enable export options.",
            icon="ℹ️",
        )
        return

    # Gather context for exports.
    language: str  = st.session_state.get("language_select", "Python")
    code: str      = st.session_state.get("code_input", "")

    col_pdf, col_md, col_clip = st.columns(3)

    # ── PDF download ─────────────────────────────────────────────────────────
    with col_pdf:
        pdf_bytes = generate_pdf(results, language, code)
        if pdf_bytes:
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name="codeexplain_analysis.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="export_pdf_btn",
            )
        else:
            st.button(
                "📄 Download PDF",
                disabled=True,
                use_container_width=True,
                key="export_pdf_disabled",
                help="PDF generation failed. Check that reportlab is installed.",
            )

    # ── Markdown download ───────────────────────────────────────────────────
    with col_md:
        md_text: str = generate_markdown(results, language, code)
        st.download_button(
            label="📝 Download Markdown",
            data=md_text.encode("utf-8"),
            file_name="codeexplain_analysis.md",
            mime="text/markdown",
            use_container_width=True,
            key="export_md_btn",
        )

    # ── Clipboard copy ───────────────────────────────────────────────────────
    with col_clip:
        plain_text: str = format_export_text(results, language)

        # Root-cause fix for UnicodeEncodeError
        # ─────────────────────────────────────
        # Streamlit serialises st.components.v1.html() content as a UTF-8
        # protobuf string.  If we embed the explanation text (which may
        # contain characters from the Gemini response, or surrogate-pair
        # escape sequences like \ud83d\udccb) directly into the JS template
        # literal, Streamlit crashes with:
        #   UnicodeEncodeError: 'utf-8' codec can't encode characters:
        #   surrogates not allowed
        #
        # Safe approach: encode the text as base64 in Python (result is
        # pure 7-bit ASCII), pass that string to JavaScript, and let the
        # browser decode it with atob().  No raw text is ever embedded in
        # the HTML string at all.
        import base64 as _b64
        # errors="replace" strips any lone surrogates the API may have returned
        safe_bytes: bytes = plain_text.encode("utf-8", errors="replace")
        b64_payload: str  = _b64.b64encode(safe_bytes).decode("ascii")

        copy_js: str = (
            "<script>\n"
            "function copyToClipboard() {\n"
            f"  var b64 = '{b64_payload}';\n"
            "  var bin = atob(b64);\n"
            "  var bytes = new Uint8Array(bin.length);\n"
            "  for (var i = 0; i < bin.length; i++) { bytes[i] = bin.charCodeAt(i); }\n"
            "  var text = new TextDecoder('utf-8').decode(bytes);\n"
            "  navigator.clipboard.writeText(text)\n"
            "    .then(function() {\n"
            "      var btn = document.getElementById('clipBtn');\n"
            "      btn.innerText = 'Copied!';\n"
            "      setTimeout(function() { btn.innerText = 'Copy Result'; }, 2000);\n"
            "    })\n"
            "    .catch(function(err) { alert('Copy failed: ' + err); });\n"
            "}\n"
            "</script>\n"
            "<button id=\"clipBtn\" onclick=\"copyToClipboard()\" "
            "style=\"width:100%;padding:0.45rem 1rem;"
            "background:#21262d;color:#c9d1d9;"
            "border:1px solid #30363d;border-radius:6px;"
            "font-size:0.875rem;cursor:pointer;font-family:inherit;\">"
            "Copy Result</button>"
        )
        st.components.v1.html(copy_js, height=42)


# ── Quiz Output ─────────────────────────────────────────────────────────────────
def render_quiz_output(questions: list[dict]) -> None:
    """
    Render an interactive multiple-choice quiz from the parsed question list.

    For each question the user sees:
      - The question text
      - Four radio button options (A / B / C / D)
      - A "Submit Answer" button
      - Correct / Incorrect feedback with the explanation

    A running score is tracked in st.session_state["quiz_score"] and
    displayed as a final summary after the last question.

    Args:
        questions (list[dict]): Parsed questions from features/quiz.parse_quiz().
    """
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-label">🧠 &nbsp;Quiz</p>',
        unsafe_allow_html=True,
    )

    total: int = len(questions)

    # Initialise per-question answer tracking in session_state.
    # "quiz_submitted" is a list of bools — True once the user submits that Q.
    # "quiz_chosen"   is a list of the user's selected option letters.
    # "quiz_score"    is the running count of correct answers.
    if "quiz_submitted" not in st.session_state:
        st.session_state["quiz_submitted"] = [False] * total
    if "quiz_chosen" not in st.session_state:
        st.session_state["quiz_chosen"] = [None] * total
    if "quiz_score" not in st.session_state:
        st.session_state["quiz_score"] = 0

    for idx, q in enumerate(questions):
        q_num: int = idx + 1
        with st.expander(f"Question {q_num} of {total}", expanded=True):
            st.markdown(f"**{q['question']}**")

            # Build radio options in A / B / C / D order.
            option_labels: list[str] = [
                f"{letter}. {q['options'].get(letter, '')}"
                for letter in ("A", "B", "C", "D")
            ]

            # Only allow selection before submission.
            disabled: bool = st.session_state["quiz_submitted"][idx]

            chosen_label = st.radio(
                label=f"q{q_num}_radio",
                options=option_labels,
                index=None,
                key=f"quiz_radio_{idx}",
                disabled=disabled,
                label_visibility="collapsed",
            )

            # Derive the chosen letter from the selected label.
            chosen_letter: str | None = (
                chosen_label[0] if chosen_label else None
            )

            if not disabled:
                if st.button("Submit Answer", key=f"quiz_submit_{idx}"):
                    if chosen_letter is None:
                        st.warning("Please select an option before submitting.",
                                   icon="⚠️")
                    else:
                        st.session_state["quiz_chosen"][idx] = chosen_letter
                        st.session_state["quiz_submitted"][idx] = True
                        if chosen_letter == q["answer"]:
                            st.session_state["quiz_score"] += 1
                        st.rerun()

            # Show feedback after submission.
            if st.session_state["quiz_submitted"][idx]:
                user_ans: str = st.session_state["quiz_chosen"][idx] or ""
                correct_ans: str = q["answer"]
                if user_ans == correct_ans:
                    st.success(f"✓ Correct! The answer is **{correct_ans}**.")
                else:
                    st.error(
                        f"✗ Incorrect. You chose **{user_ans}**. "
                        f"The correct answer is **{correct_ans}**."
                    )
                st.info(f"**Explanation:** {q['explanation']}")

    # ── Final score (shown once all questions are submitted) ────────────────────
    all_done: bool = all(st.session_state["quiz_submitted"][:total])
    if all_done:
        score: int = st.session_state["quiz_score"]
        rating: str = (
            "Excellent 🌟" if score == 5
            else "Great 👍"   if score == 4
            else "Good 👌"    if score == 3
            else "Needs Practice 📚"
        )
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="text-align:center; padding:1.5rem;
                        background:#161b22; border:1px solid #30363d;
                        border-radius:12px; margin-top:1rem;">
                <div style="font-size:2rem; font-weight:700;
                            background:linear-gradient(135deg,#58a6ff,#a371f7);
                            -webkit-background-clip:text;
                            -webkit-text-fill-color:transparent;">
                    Score: {score} / {total}
                </div>
                <div style="color:#8b949e; font-size:1.1rem; margin-top:0.5rem;">
                    {rating}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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

    # 2. PENDING-CLEAR GUARD — must run before any widget is instantiated.
    # Streamlit forbids writing to st.session_state[widget_key] after the
    # widget has rendered in the same script run.  So we use a flag:
    # the Clear button sets "_clear_pending" = True and calls st.rerun().
    # On the very next run this block fires first, clears the text-area
    # state before render_code_input() creates the widget, then deletes
    # the flag so it never fires again.
    if st.session_state.get("_clear_pending"):
        st.session_state["code_input"] = ""
        del st.session_state["_clear_pending"]

    # 3. FILE-UPLOAD GUARD — applies loaded file content before widget renders.
    # When a file is successfully read, we store its content and detected
    # language under "_upload_pending" then call st.rerun().  On the very
    # next run this guard fires first, writes code_input before the text_area
    # widget is instantiated (safe), then deletes the flag.
    if st.session_state.get("_upload_pending"):
        pending = st.session_state.pop("_upload_pending")
        st.session_state["code_input"] = pending["content"]
        # Override the sidebar language selection to match the file type.
        if pending["language"] not in ("Plain Text", ""):
            st.session_state["language_select"] = pending["language"]

    # 4. Render sidebar — returns user selections
    language, mode = render_sidebar()

    # 5. Hero banner
    render_hero()

    # 6. File uploader (above the editor)
    st.markdown(
        '<p class="section-label">📁 &nbsp;Upload a File <span style="color:#484f58;font-size:0.8rem;font-weight:400;">(optional)</span></p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        label="Upload source code file",
        type=[ext.lstrip(".") for ext in supported_extensions()],
        key="file_uploader",
        label_visibility="collapsed",
        help="Supported: .py  .java  .cpp  .c  .js  — Max 1 MB",
    )
    if uploaded_file is not None:
        # ── Deduplication guard ────────────────────────────────────────────────
        # st.file_uploader returns the file object on EVERY script run until
        # the user removes it.  Without this guard the handler would call
        # st.rerun() on every run (including runs triggered by button clicks)
        # causing an infinite loop and discarding Explain / Quiz button events.
        # We track the last processed filename and skip re-processing when the
        # same file is still present in the widget.
        already_processed: bool = (
            uploaded_file.name == st.session_state.get("_last_upload_name", "")
        )
        if not already_processed:
            content, error = read_uploaded_file(uploaded_file)
            if error:
                st.error(error, icon="🚨")
            else:
                detected_lang: str = detect_language(uploaded_file.name)
                # Mark this file as processed before the rerun so the guard
                # above does not fire again for the same upload.
                st.session_state["_last_upload_name"] = uploaded_file.name
                # Store content for the pending guard to write before widgets render.
                st.session_state["_upload_pending"] = {
                    "content":  content,
                    "language": detected_lang,
                }
                # Clear stale AI results so output matches the new file.
                st.session_state.pop("explain_results", None)
                st.session_state.pop("quiz_questions",  None)
                st.session_state.pop("quiz_submitted",  None)
                st.session_state.pop("quiz_chosen",     None)
                st.session_state.pop("quiz_score",      None)
                lang_note = (
                    f"Language detected: **{detected_lang}**"
                    if detected_lang != "Plain Text"
                    else "Language could not be detected automatically."
                )
                st.success(
                    f"Loaded: **{uploaded_file.name}**  —  {lang_note}",
                    icon="✅",
                )
                st.rerun()

    # 7. Code input section
    st.markdown(
        '<p class="section-label">✏️ &nbsp;Code Editor</p>',
        unsafe_allow_html=True,
    )
    render_code_input(language)
    # Use session_state as the source of truth.
    # render_code_input() returns only what the user typed in the current
    # interaction; session_state["code_input"] is the canonical value and
    # already contains uploaded file content when the upload guard has run.
    code: str = st.session_state.get("code_input", "")

    # 8. Action buttons
    explain_clicked, quiz_clicked, clear_clicked = render_action_buttons()

    # 9. Handle Clear button — set a flag then rerun so the guard above
    # can safely clear the widget key before it is next instantiated.
    if clear_clicked:
        st.session_state["_clear_pending"] = True
        st.session_state.pop("explain_results",   None)
        st.session_state.pop("quiz_questions",    None)
        st.session_state.pop("quiz_submitted",    None)
        st.session_state.pop("quiz_chosen",       None)
        st.session_state.pop("quiz_score",        None)
        # Reset the upload deduplication key so the same file can be
        # re-uploaded after the editor is cleared.
        st.session_state.pop("_last_upload_name", None)
        st.rerun()

    # 10. Handle Explain Code button ─────────────────────────────────────────
    if explain_clicked:
        if not code or not code.strip():
            st.warning(
                "Please paste some code before clicking Explain Code.",
                icon="⚠️",
            )
        else:
            with st.spinner("Analysing your code with Gemini AI..."):
                results: dict[str, str] = run_explanation(
                    code=code, language=language
                )
            # Cache results in session_state so they survive widget reruns.
            st.session_state["explain_results"] = results

    # 8. Handle Quiz button ────────────────────────────────────────────
    if quiz_clicked:
        if not code or not code.strip():
            st.warning(
                "Please paste some code before clicking Generate Quiz.",
                icon="⚠️",
            )
        else:
            with st.spinner("Generating quiz with Gemini AI..."):
                quiz_result = run_quiz(code=code, language=language)
            # Reset per-question tracking for the new quiz.
            st.session_state.pop("quiz_submitted", None)
            st.session_state.pop("quiz_chosen",    None)
            st.session_state.pop("quiz_score",     None)
            st.session_state["quiz_questions"] = quiz_result

    # 9. Render Explain output ───────────────────────────────────────────────
    explain_results = st.session_state.get("explain_results")

    if explain_results:
        if "error" in explain_results:
            st.error(explain_results["error"], icon="🚨")
            render_output_placeholder()
        else:
            render_filled_output(explain_results)
    else:
        render_output_placeholder()

    # 10. Render Quiz output ───────────────────────────────────────────────
    quiz_data = st.session_state.get("quiz_questions")

    if quiz_data is not None:
        if isinstance(quiz_data, dict) and "error" in quiz_data:
            st.error(quiz_data["error"], icon="🚨")
        elif isinstance(quiz_data, list) and quiz_data:
            render_quiz_output(quiz_data)

    # 11. Footer
    render_footer()


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
