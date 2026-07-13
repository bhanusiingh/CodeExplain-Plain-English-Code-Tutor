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
from utils.history_manager import (
    init_history,
    save_history,
    load_history,
    restore_history,
    delete_history,
    clear_history,
    group_history_by_date,
)
import re
from features.learning import parse_learning_assistant

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
            margin-bottom: 0.5rem;
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

        /* ── Modern Workspace Container ── */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #0d1117 !important;
            border: 1px solid #30363d !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.24) !important;
        }

        .editor-header-left {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            height: 100%;
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
            font-size: 0.85rem;
            color: #c9d1d9;
            margin-left: 0.5rem;
            font-weight: 500;
        }

        /* Seamless text area inside bordered container */
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTextArea"] textarea {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.92rem !important;
            background: #090d13 !important;
            color: #e6edf3 !important;
            border: 1px solid #21262d !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            line-height: 1.6 !important;
            min-height: 320px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTextArea"] textarea:focus {
            border-color: #58a6ff !important;
            box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.15) !important;
        }

        /* Compact File Uploader in Header */
        [data-testid="stFileUploader"] {
            padding: 0 !important;
            margin: 0 !important;
        }
        [data-testid="stFileUploader"] section {
            padding: 0.2rem 0.5rem !important;
            min-height: auto !important;
            background: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 6px !important;
        }
        [data-testid="stFileUploader"] section > div {
            display: none !important; /* Hide drag/drop label */
        }
        [data-testid="stFileUploader"] button {
            background: transparent !important;
            color: #58a6ff !important;
            border: none !important;
            font-weight: 500 !important;
            font-size: 0.82rem !important;
            margin: 0 !important;
            padding: 0.1rem 0.3rem !important;
            width: auto !important;
            height: auto !important;
        }

        /* ── Buttons ──────────────────────────────────────────────────────── */
        .stButton > button {
            width: 100% !important;
            height: 44px !important;
            padding: 0.5rem 1rem !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.4rem !important;
            border: none !important;
            cursor: pointer !important;
        }

        /* Primary — Explain button */
        div[data-testid="column"]:nth-child(2) .stButton > button {
            background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(31, 111, 235, 0.2) !important;
        }

        div[data-testid="column"]:nth-child(2) .stButton > button:hover {
            background: linear-gradient(135deg, #388bfd 0%, #58a6ff 100%) !important;
            box-shadow: 0 6px 20px rgba(31, 111, 235, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Secondary — Quiz button */
        div[data-testid="column"]:nth-child(3) .stButton > button {
            background: linear-gradient(135deg, #6e40c9 0%, #a371f7 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(110, 64, 201, 0.2) !important;
        }

        div[data-testid="column"]:nth-child(3) .stButton > button:hover {
            background: linear-gradient(135deg, #a371f7 0%, #d2a8ff 100%) !important;
            box-shadow: 0 6px 20px rgba(110, 64, 201, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Clear button */
        div[data-testid="column"]:nth-child(4) .stButton > button {
            background: transparent !important;
            color: #8b949e !important;
            border: 1px solid #30363d !important;
        }

        div[data-testid="column"]:nth-child(4) .stButton > button:hover {
            background: #21262d !important;
            color: #e6edf3 !important;
            border-color: #8b949e !important;
        }

        /* ── Selectbox ────────────────────────────────────────────────────── */
        [data-testid="stSelectbox"] > div > div {
            background: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
            color: #e6edf3 !important;
        }

        /* Action row selectbox height matching (44px) */
        div[data-testid="column"]:nth-child(1) [data-testid="stSelectbox"] > div > div {
            height: 44px !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
        }

        /* File Chip row selectbox height matching (34px) */
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] > div > div {
            height: 34px !important;
            min-height: 34px !important;
            display: flex !important;
            align-items: center !important;
            font-size: 0.85rem !important;
            border-radius: 6px !important;
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
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 1rem 0 !important;
            text-align: center;
            margin-top: 3rem;
            color: #8b949e !important;
            opacity: 0.65 !important;
            font-size: 0.8rem;
            box-shadow: none !important;
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

        /* ── Workspace Uploader & File Chip Redesign ── */
        .workspace-uploader [data-testid="stFileUploader"] section {
            background: #090d13 !important;
            border: 2px dashed #21262d !important;
            border-radius: 8px !important;
            padding: 1.5rem !important;
            text-align: center !important;
            transition: all 0.2s ease !important;
        }
        .workspace-uploader [data-testid="stFileUploader"] section:hover {
            border-color: #58a6ff !important;
            background: #0d1624 !important;
        }
        .workspace-uploader [data-testid="stFileUploader"] label {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: #c9d1d9 !important;
            margin-bottom: 0.5rem !important;
            display: block !important;
            text-align: center !important;
        }
        .workspace-uploader [data-testid="stFileUploader"] section > div {
            display: block !important;
        }

        /* Prevent default page-wide dimming during runs */
        [data-testid="stAppViewContainer"] {
            opacity: 1 !important;
        }
        [data-testid="stSidebar"] {
            opacity: 1 !important;
            filter: none !important;
        }
        .footer {
            filter: none !important;
        }

        /* ── File info chip toolbar — sits directly inside the outer workspace card ── */
        /* Columns inside the chip row: vertically center, no extra padding */
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            align-items: center !important;
        }
        /* Remove any stray inner wrapper styling so chips render flat */
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ✕ Remove-file button */
        button[data-testid="baseButton-secondary"][title="Remove code and results"],
        div[data-testid="column"]:last-child button {
            background: transparent !important;
            color: #f85149 !important;
            border: 1px solid #30363d !important;
            height: 34px !important;
            width: 34px !important;
            border-radius: 6px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 0.95rem !important;
            padding: 0 !important;
            margin: 0 !important;
            transition: background 0.2s ease, border-color 0.2s ease !important;
        }
        button[data-testid="baseButton-secondary"][title="Remove code and results"]:hover,
        div[data-testid="column"]:last-child button:hover {
            background: rgba(248, 81, 73, 0.15) !important;
            border-color: #f85149 !important;
            color: #ff6b6b !important;
        }

        /* History list styles */
        div.history-item-container {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 0.4rem !important;
            margin-bottom: 0.2rem !important;
        }
        div.history-item-container div[data-testid="column"] {
            display: flex !important;
            align-items: center !important;
            height: 28px !important;
        }
        /* Style title button */
        div.history-item-container div[data-testid="column"]:nth-child(1) button {
            background: transparent !important;
            color: #c9d1d9 !important;
            border: none !important;
            text-align: left !important;
            justify-content: flex-start !important;
            font-size: 0.85rem !important;
            font-weight: 400 !important;
            height: 28px !important;
            padding: 0 0.4rem !important;
            margin: 0 !important;
        }
        div.history-item-container div[data-testid="column"]:nth-child(1) button:hover {
            color: #58a6ff !important;
            background: rgba(88, 166, 255, 0.1) !important;
        }
        /* Style delete button */
        div.history-item-container div[data-testid="column"]:nth-child(2) button {
            background: transparent !important;
            color: #8b949e !important;
            border: none !important;
            font-size: 0.8rem !important;
            height: 28px !important;
            width: 28px !important;
            padding: 0 !important;
            margin: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        div.history-item-container div[data-testid="column"]:nth-child(2) button:hover {
            color: #f85149 !important;
            background: rgba(248, 81, 73, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar() -> tuple[str, str]:
    """
    Render the sidebar with logo, settings, history, and about.

    Returns:
        tuple: (selected_language, selected_mode)
    """
    # Ensure default values exist in session state
    if "language_selector" not in st.session_state:
        st.session_state["language_selector"] = "Python"
        st.session_state["language_select"] = "Python"
    if "mode_selector" not in st.session_state:
        st.session_state["mode_selector"] = "Beginner"

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

        # History Section
        st.markdown(
            '<p class="section-label">📜 &nbsp;History</p>',
            unsafe_allow_html=True,
        )

        # + New Chat button
        if st.button(
            "+ New Chat",
            key="new_chat_btn",
            use_container_width=True,
            help="Clear editor and results without erasing history",
        ):
            st.session_state["_clear_pending"] = True
            st.session_state.pop("explain_results",   None)
            st.session_state.pop("quiz_questions",    None)
            st.session_state.pop("quiz_submitted",    None)
            st.session_state.pop("quiz_chosen",       None)
            st.session_state.pop("quiz_score",        None)
            st.session_state.pop("_last_upload_name", None)
            st.session_state.pop("file_uploader",     None)
            st.rerun()

        st.markdown(
            '<hr style="border-color:#21262d;margin:0.5rem 0;">',
            unsafe_allow_html=True,
        )

        history = load_history()
        if not history:
            st.markdown(
                '<p style="color:#484f58;font-size:0.8rem;padding:0.4rem 0;">'  
                'No history yet. Explain some code to get started.</p>',
                unsafe_allow_html=True,
            )
        else:
            groups = group_history_by_date(history)
            for group_label, items in groups.items():
                st.markdown(
                    f'<p style="color:#8b949e;font-size:0.75rem;font-weight:700;'
                    f'text-transform:uppercase;letter-spacing:0.08em;'
                    f'margin:0.8rem 0 0.3rem 0;">{group_label}</p>',
                    unsafe_allow_html=True,
                )
                for item in items:
                    st.markdown('<div class="history-item-container">', unsafe_allow_html=True)
                    col_title, col_del = st.columns([5, 1])
                    with col_title:
                        if st.button(
                            f"📄 {item['title']}",
                            key=f"hist_{item['id']}",
                            use_container_width=True,
                            help=f"{item['language']} • {item['timestamp'].strftime('%H:%M')}",
                        ):
                            # Trigger restore on next run via pending flag
                            st.session_state["_restore_pending"] = item["id"]
                            st.rerun()
                    with col_del:
                        if st.button(
                            "✕",
                            key=f"del_{item['id']}",
                            help="Delete this entry",
                        ):
                            delete_history(item["id"])
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(
                '<hr style="border-color:#21262d;margin:0.6rem 0;">',
                unsafe_allow_html=True,
            )
            if st.button(
                "🗑️ Clear All History",
                key="clear_hist_btn",
                use_container_width=True,
                help="Permanently delete all history items",
            ):
                clear_history()
                st.rerun()

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # 3. About Section
        st.markdown(
            '<p class="section-label">ℹ️ &nbsp;About</p>',
            unsafe_allow_html=True,
        )

        with st.expander("✨ Features & Overview", expanded=False):
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

        with st.expander("📋 User Guide", expanded=False):
            st.markdown(
                """
                <div class="sidebar-info-card">
                    <div class="sidebar-info-title">Step 1</div>
                    <div class="sidebar-info-value">Paste code or upload a file</div>
                </div>
                <div class="sidebar-info-card">
                    <div class="sidebar-info-title">Step 2</div>
                    <div class="sidebar-info-value">Select language and click <strong>Explain Code</strong></div>
                </div>
                <div class="sidebar-info-card">
                    <div class="sidebar-info-title">Step 3</div>
                    <div class="sidebar-info-value">Try <strong>Generate Quiz</strong> to test memory</div>
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

    language = st.session_state.get("language_selector", "Python")
    mode = st.session_state.get("mode_selector", "Beginner")
    return language, mode


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
    Render the code editor.

    Args:
        language: Selected programming language (for filename hint).

    Returns:
        str: The code entered by the user.
    """

    code = st.text_area(
        label="Code Editor",
        placeholder="// Paste your code here...",
        height=380,
        key="code_input",
        label_visibility="collapsed",
    )
    return code


# ── Action Buttons ────────────────────────────────────────────────────────────
def render_action_buttons() -> tuple[bool, bool, bool]:
    """
    Render the Explanation Depth selectbox and the Explain, Quiz, and Clear action buttons.

    Returns:
        tuple: (explain_clicked, quiz_clicked, clear_clicked)
    """
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    is_processing = st.session_state.get("is_processing", False)
    
    with col1:
        options_mode = ["Beginner", "Intermediate", "Advanced"]
        current_mode = st.session_state.get("mode_selector", "Beginner")
        try:
            mode_index = options_mode.index(current_mode)
        except ValueError:
            mode_index = 0
            
        st.selectbox(
            "Explanation Depth",
            options=options_mode,
            index=mode_index,
            key="mode_selector",
            label_visibility="collapsed",
            help="Choose how detailed the explanation should be.",
        )
        
    with col2:
        explain_clicked = st.button(
            "✨ Explain",
            use_container_width=True,
            disabled=is_processing,
            help="Analyze the code and generate a plain-English explanation, complexity, and suggestions",
        )
    with col3:
        quiz_clicked = st.button(
            "🧠 Quiz",
            use_container_width=True,
            disabled=is_processing,
            help="Create a five-question interactive multiple-choice test based on the code",
        )
    with col4:
        clear_clicked = st.button(
            "🗑 Clear",
            use_container_width=True,
            disabled=is_processing,
            help="Reset the code editor and clear the generated results",
        )

    return explain_clicked, quiz_clicked, clear_clicked


# ── Output Section (Tab Content) ──────────────────────────────────────────────
def render_tab_content(active_tab: str, results: dict[str, str]) -> None:
    """
    Render active content tab for the explanation results.
    """
    if active_tab == "Summary":
        st.markdown('<p class="section-label">📖 &nbsp;Summary</p>', unsafe_allow_html=True)
        st.markdown(results.get(SECTION_SUMMARY, "Summary not available."))

    elif active_tab == "Breakdown":
        st.markdown('<p class="section-label">🔍 &nbsp;Line-by-Line Explanation</p>', unsafe_allow_html=True)
        st.markdown(results.get(SECTION_LINE_BY_LINE, "Breakdown not available."))

    elif active_tab == "Complexity":
        st.markdown('<p class="section-label">📊 &nbsp;Complexity Analysis</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("**⏱️ Time Complexity**")
                st.markdown(results.get(SECTION_TIME, "Time complexity not available."))
        with col2:
            with st.container(border=True):
                st.markdown("**💾 Space Complexity**")
                st.markdown(results.get(SECTION_SPACE, "Space complexity not available."))

    elif active_tab == "Suggestions":
        st.markdown('<p class="section-label">💡 &nbsp;Suggested Improvements</p>', unsafe_allow_html=True)
        st.markdown(results.get(SECTION_IMPROVEMENTS, "Suggestions not available."))

    elif active_tab == "Learning":
        st.markdown('<p class="section-label">🎓 &nbsp;Learning Assistant</p>', unsafe_allow_html=True)
        learning = results.get("learning")
        if learning and isinstance(learning, dict):
            subsections = [
                ("📚 Concepts Used", "concepts"),
                ("📖 Prerequisites", "prerequisites"),
                ("🎯 Difficulty", "difficulty"),
                ("💼 Interview Questions", "interview_questions"),
                ("➡ Next Topic", "next_topic"),
            ]
            for subtitle, subkey in subsections:
                with st.container(border=True):
                    st.markdown(f"**{subtitle}**")
                    st.markdown(learning.get(subkey, "Information not available."))
        else:
            st.info("Learning insights are not available for this run.", icon="🎓")


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


# ── Language Override Callback ───────────────────────────────────────────────
def on_language_override() -> None:
    """Callback to sync manual language override from the editor chip to sidebar selector."""
    new_lang = st.session_state.get("override_language")
    if new_lang:
        st.session_state["language_selector"] = new_lang
        st.session_state["language_select"] = new_lang


# ── Paste Language Heuristic Detection ─────────────────────────────────────────
def detect_pasted_language(code: str) -> str:
    """Heuristically detect language of pasted code snippet."""
    if not code or not code.strip():
        return "Python"

    code_lower = code.lower()

    # Check C++ indicators first
    cpp_indicators = ["#include <iostream>", "std::", "cout <<", "cin >>", "#include <vector>", "#include <string>"]
    if any(ind in code for ind in cpp_indicators):
        return "C++"

    # Check C indicators
    c_indicators = ["#include <stdio.h>", "printf(", "scanf("]
    if any(ind in code for ind in c_indicators):
        # Disambiguate C vs C++
        if "using namespace std" in code or "class " in code or "new " in code:
            return "C++"
    # Check Java indicators
    java_indicators = ["public class ", "public static void main", "System.out.print", "import java."]
    if any(ind in code for ind in java_indicators):
        return "Java"

    # Check JavaScript indicators
    js_indicators = ["console.log(", "const ", "let ", "document.get", "window.", "function ", "=>"]
    if any(ind in code_lower for ind in js_indicators):
        # Make sure it's not python def or import
        if "def " not in code and "import " not in code:
            return "JavaScript"

    # Check Python indicators
    py_indicators = ["def ", "import ", "print(", "elif ", "pass", "class ", "if __name__ =="]
    if any(ind in code for ind in py_indicators):
        return "Python"

    return "Python"  # Default fallback


# ── Main App ──────────────────────────────────────────────────────────────────
def main() -> None:
    """Main application entry point."""
    # 1. Load global styles
    load_css()

    # 1b. Initialise history (idempotent — safe to call every run)
    init_history()

    # 1c. Reset stuck is_processing flags at the start of every rerun
    st.session_state["is_processing"] = False

    # 2. PENDING-CLEAR GUARD
    if st.session_state.get("_clear_pending"):
        st.session_state["code_input"] = ""
        st.session_state.pop("file_uploader", None)
        del st.session_state["_clear_pending"]

    # 2b. RESTORE GUARD — fires before any widget is instantiated.
    # When the user clicks a history item the sidebar sets "_restore_pending"
    # to the item id and calls st.rerun().  This guard reads the item and
    # writes all state keys (code_input, language_select, explain_results,
    # quiz_questions, quiz tracking) before widgets render.
    if st.session_state.get("_restore_pending"):
        item_id: str = st.session_state.pop("_restore_pending")
        item = restore_history(item_id)
        if item:
            st.session_state["code_input"]    = item["code"]
            st.session_state["explain_results"] = item["analysis"]
            st.session_state["quiz_questions"]   = item["quiz"]
            # Set active tab depending on whether they saved explain or quiz
            if item.get("active_view") == "quiz":
                st.session_state["active_tab"] = "Quiz"
            else:
                st.session_state["active_tab"] = "Summary"
            # Reset quiz tracking so the restored quiz starts fresh
            st.session_state.pop("quiz_submitted", None)
            st.session_state.pop("quiz_chosen",    None)
            st.session_state.pop("quiz_score",     None)
            # Restore language selector if item has a known language
            if item.get("language"):
                st.session_state["language_selector"] = item["language"]
            # Restore uploaded filename hint, or clear it if restoring non-file snippet
            if item.get("filename"):
                st.session_state["_last_upload_name"] = item["filename"]
            else:
                st.session_state.pop("_last_upload_name", None)
                st.session_state.pop("file_uploader",     None)

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
            st.session_state["language_selector"] = pending["language"]
            st.session_state["language_select"] = pending["language"]
        st.session_state["_detected_language"] = pending["language"]

    # 3b. Initialize click warnings
    explain_warning: bool = False
    quiz_warning: bool = False

    # 4. Render sidebar — returns user selections
    language, mode = render_sidebar()

    # 5. Hero banner
    render_hero()

    # 6. Redesigned Workspace Editor Card (Single Unified Container)
    # Inject loading styles dynamically when is_processing is True
    if st.session_state.get("is_processing", False):
        st.markdown(
            """
            <style>
            /* Dim the active workspace card container during run */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                opacity: 0.65 !important;
                pointer-events: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    with st.container(border=True):
        last_upload_name = st.session_state.get("_last_upload_name")
        code_input = st.session_state.get("code_input", "")

        # Render status row/chip if file is uploaded OR pasted code is not empty
        if last_upload_name or (code_input and code_input.strip()):
            if last_upload_name:
                detected_lang = st.session_state.get("_detected_language")
                if not detected_lang:
                    detected_lang = detect_language(last_upload_name)
                    st.session_state["_detected_language"] = detected_lang
                chip_title = f"📄 {last_upload_name}"
            else:
                prev_detected = st.session_state.get("_detected_language")
                detected_lang = detect_pasted_language(code_input)
                st.session_state["_detected_language"] = detected_lang
                # Auto-update active language selection if a new language is auto-detected
                if prev_detected != detected_lang:
                    st.session_state["language_selector"] = detected_lang
                    st.session_state["language_select"] = detected_lang
                chip_title = "📝 pasted_code"

            # Chip toolbar — no Streamlit container border, pure inline HTML + selectbox/button
            # Build the detection badge HTML
            if detected_lang and detected_lang not in ("", "Plain Text"):
                lang_badge_html = (
                    f'<span style="display:inline-flex;align-items:center;gap:0.3rem;'
                    f'font-size:0.82rem;color:#8b949e;font-weight:500;white-space:nowrap;">'
                    f'<span style="color:#2ec27e;font-size:0.75rem;">●</span>'
                    f'{detected_lang} Detected</span>'
                )
            else:
                lang_badge_html = (
                    '<span style="font-size:0.82rem;color:#484f58;font-style:italic;">'
                    'No language detected</span>'
                )

            # Row layout: chip | detection | selectbox | remove button
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:0.4rem;padding:0.3rem 0;">'
                    f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.88rem;'
                    f'color:#e6edf3;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    f'{chip_title}</span></div>',
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;height:100%;">{lang_badge_html}</div>',
                    unsafe_allow_html=True,
                )
            with cols[2]:
                options = ["Python", "Java", "JavaScript", "C++", "C"]
                current_lang = st.session_state.get("language_selector")
                if not current_lang:
                    current_lang = detected_lang
                    st.session_state["language_selector"] = detected_lang
                    st.session_state["language_select"] = detected_lang

                try:
                    lang_index = options.index(current_lang)
                except ValueError:
                    lang_index = 0

                st.selectbox(
                    "Language Selector",
                    options=options,
                    index=lang_index,
                    key="override_language",
                    label_visibility="collapsed",
                    help="Manually override the detected language",
                    on_change=on_language_override,
                )
            with cols[3]:
                if st.button("✕", key="btn_remove_file", help="Remove code and results", use_container_width=True):
                    st.session_state["_clear_pending"] = True
                    st.session_state.pop("explain_results",   None)
                    st.session_state.pop("quiz_questions",    None)
                    st.session_state.pop("quiz_submitted",    None)
                    st.session_state.pop("quiz_chosen",       None)
                    st.session_state.pop("quiz_score",        None)
                    st.session_state.pop("_last_upload_name", None)
                    st.session_state.pop("file_uploader",     None)
                    st.session_state.pop("_detected_language", None)
                    st.session_state.pop("override_language",  None)
                    st.session_state["code_input"] = ""
                    st.session_state["language_selector"] = "Python"
                    st.session_state["language_select"] = "Python"
                    st.rerun()

        # If no file is uploaded and code is empty, show uploader at the top
        if not last_upload_name and not (code_input and code_input.strip()):
            st.markdown('<div class="workspace-uploader">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                label="📎 Upload Code File (Drag & Drop)",
                type=[ext.lstrip(".") for ext in supported_extensions()],
                key="file_uploader",
                disabled=st.session_state.get("is_processing", False),
            )
            st.markdown('</div>', unsafe_allow_html=True)

            if uploaded_file is not None and not st.session_state.get("is_processing", False):
                # Deduplication guard
                already_processed: bool = (
                    uploaded_file.name == st.session_state.get("_last_upload_name", "")
                )
                if not already_processed:
                    content, error = read_uploaded_file(uploaded_file)
                    if error:
                        st.error(error, icon="🚨")
                    else:
                        detected_lang: str = detect_language(uploaded_file.name)
                        st.session_state["_last_upload_name"] = uploaded_file.name
                        st.session_state["_detected_language"] = detected_lang
                        st.session_state["_upload_pending"] = {
                            "content":  content,
                            "language": detected_lang,
                        }
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

        # 7. Render code input section
        render_code_input(language)
        # Use session_state as the source of truth.
        code: str = st.session_state.get("code_input", "")

        # 8. Action buttons
        explain_clicked, quiz_clicked, clear_clicked = render_action_buttons()

        # Handle Explain click
        if explain_clicked:
            if not code or not code.strip():
                explain_warning = True
            else:
                st.session_state["is_processing"] = True
                try:
                    with st.spinner("Analysing your code with Gemini AI..."):
                        results = run_explanation(code=code, language=language)
                    
                    if "error" not in results:
                        # Extract Learning Assistant from improvements section
                        improvements_raw = results.get("improvements", "")
                        split_pattern = r"(?im)^#+\s*Learning\s+Assistant\s*$"
                        parts = re.split(split_pattern, improvements_raw)
                        
                        learning_raw = ""
                        if len(parts) > 1:
                            results["improvements"] = parts[0].strip()
                            learning_raw = parts[1].strip()
                        
                        # Parse learning raw text and store in results
                        results["learning"] = parse_learning_assistant(learning_raw)

                    st.session_state["explain_results"] = results
                    if "error" not in results:
                        st.session_state["active_tab"] = "Summary"
                        save_history(
                            code=code,
                            language=language,
                            analysis=results,
                            quiz=st.session_state.get("quiz_questions"),
                            filename=st.session_state.get("_last_upload_name", ""),
                            active_view="explain",
                        )
                finally:
                    st.session_state["is_processing"] = False
                st.rerun()

        # Handle Quiz click
        elif quiz_clicked:
            if not code or not code.strip():
                quiz_warning = True
            else:
                st.session_state["is_processing"] = True
                try:
                    with st.spinner("Generating quiz with Gemini AI..."):
                        quiz_result = run_quiz(code=code, language=language)
                    # Reset per-question tracking for the new quiz.
                    st.session_state.pop("quiz_submitted", None)
                    st.session_state.pop("quiz_chosen",    None)
                    st.session_state.pop("quiz_score",     None)
                    st.session_state["quiz_questions"] = quiz_result
                    if isinstance(quiz_result, list) and quiz_result:
                        st.session_state["active_tab"] = "Quiz"
                        save_history(
                            code=code,
                            language=language,
                            analysis=st.session_state.get("explain_results"),
                            quiz=quiz_result,
                            filename=st.session_state.get("_last_upload_name", ""),
                            active_view="quiz",
                        )
                finally:
                    st.session_state["is_processing"] = False
                st.rerun()

    # 9. Handle Clear button — set a flag then rerun so the guard above
    # can safely clear the widget key before it is next instantiated.
    if clear_clicked:
        st.session_state["_clear_pending"] = True
        st.session_state.pop("explain_results",   None)
        st.session_state.pop("quiz_questions",    None)
        st.session_state.pop("quiz_submitted",    None)
        st.session_state.pop("quiz_chosen",       None)
        st.session_state.pop("quiz_score",        None)
        # Reset the upload deduplication key and widget so same file can be
        # re-uploaded after the editor is cleared.
        st.session_state.pop("_last_upload_name", None)
        st.session_state.pop("file_uploader",     None)
        st.session_state.pop("_detected_language", None)
        st.session_state.pop("override_language",  None)
        st.rerun()

    # 10. Handle Warnings from Pre-render Stage
    if explain_warning:
        st.warning(
            "Code Editor is empty. Please enter or upload some source code before requesting an explanation.",
            icon="⚠️",
        )
    if quiz_warning:
        st.warning(
            "Code Editor is empty. Please enter or upload some source code before generating a quiz.",
            icon="⚠️",
        )

    # 11. Render Explain output (only when exists, hiding empty states)
    # 11. Render Tabbed Results Workspace (only when any results exist)
    explain_results = st.session_state.get("explain_results")
    quiz_data = st.session_state.get("quiz_questions")

    if explain_results or quiz_data:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Ensure active_tab is initialized
        if "active_tab" not in st.session_state:
            if explain_results:
                st.session_state["active_tab"] = "Summary"
            else:
                st.session_state["active_tab"] = "Quiz"

        active_tab = st.session_state["active_tab"]

        # Render Tab bar
        tab_indices = {
            "Summary": 1,
            "Breakdown": 2,
            "Complexity": 3,
            "Suggestions": 4,
            "Learning": 5,
            "Quiz": 6,
        }
        active_idx = tab_indices.get(active_tab, 1)

        st.markdown(
            f"""
            <style>
            /* Default styling for tab buttons */
            div.tab-bar-container div[data-testid="column"] .stButton > button {{
                background: #161b22 !important;
                color: #8b949e !important;
                border: 1px solid #21262d !important;
                height: 40px !important;
                font-size: 0.88rem !important;
                font-weight: 500 !important;
            }}
            /* Highlight active tab button */
            div.tab-bar-container div[data-testid="column"]:nth-child({active_idx}) .stButton > button {{
                background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
                color: #ffffff !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(31, 111, 235, 0.2) !important;
                font-weight: 600 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="tab-bar-container">', unsafe_allow_html=True)
        tab_cols = st.columns(6)
        with tab_cols[0]:
            if st.button("📖 Summary", key="tab_summary", use_container_width=True):
                st.session_state["active_tab"] = "Summary"
                st.rerun()
        with tab_cols[1]:
            if st.button("🔍 Breakdown", key="tab_breakdown", use_container_width=True):
                st.session_state["active_tab"] = "Breakdown"
                st.rerun()
        with tab_cols[2]:
            if st.button("📊 Complexity", key="tab_complexity", use_container_width=True):
                st.session_state["active_tab"] = "Complexity"
                st.rerun()
        with tab_cols[3]:
            if st.button("💡 Suggestions", key="tab_suggestions", use_container_width=True):
                st.session_state["active_tab"] = "Suggestions"
                st.rerun()
        with tab_cols[4]:
            if st.button("🎓 Learning", key="tab_learning", use_container_width=True):
                st.session_state["active_tab"] = "Learning"
                st.rerun()
        with tab_cols[5]:
            if st.button("📝 Quiz", key="tab_quiz", use_container_width=True):
                st.session_state["active_tab"] = "Quiz"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

        # Render Active Tab Content
        if active_tab == "Quiz":
            if quiz_data is not None:
                if isinstance(quiz_data, dict) and "error" in quiz_data:
                    st.error(quiz_data["error"], icon="🚨")
                elif isinstance(quiz_data, list) and quiz_data:
                    render_quiz_output(quiz_data)
            else:
                st.info("No quiz generated yet. Click **Generate Quiz** below the editor to create one.", icon="📝")
        else:
            if explain_results:
                if "error" in explain_results:
                    st.error(explain_results["error"], icon="🚨")
                else:
                    render_tab_content(active_tab, explain_results)
            else:
                st.info("No explanation generated yet. Click **Explain Code** below the editor to analyze the code.", icon="ℹ️")

        # Export buttons (render ONLY if valid explanation results exist)
        if explain_results and "error" not in explain_results:
            render_export_buttons(explain_results)

    # 11. Footer
    render_footer()


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
