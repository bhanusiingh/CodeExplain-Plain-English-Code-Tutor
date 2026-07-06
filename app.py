"""
app.py
------
Entry point for CodeExplain: Plain-English Code Tutor.
Full UI will be assembled in Module 2 (UI Shell).
"""

import streamlit as st

# ── Page configuration (must be the first Streamlit call) ────────────────────
st.set_page_config(
    page_title="CodeExplain — Plain-English Code Tutor",
    page_icon="🧑‍🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Temporary landing screen ─────────────────────────────────────────────────
st.title("🧑‍🏫 CodeExplain — Plain-English Code Tutor")
st.info(
    "**Module 1 complete.** Project structure and configuration files are set up. "
    "The full UI will be built in Module 2.",
    icon="🏗️",
)
