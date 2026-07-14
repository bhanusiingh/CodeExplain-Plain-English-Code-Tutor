"""
services/monaco_editor.py
--------------------------
Monaco Editor integration for CodeExplain.

Declares and renders a professional Monaco (VS Code) editor as a proper,
bi-directional Streamlit Custom Component.

Public API
----------
    render_monaco_editor(value, language, disabled, height, key) -> str
        Renders the Monaco custom component. Returns the current editor contents
        directly to Python.
"""

from __future__ import annotations

import os
import streamlit as st
import streamlit.components.v1 as components

# Declare the component once
_PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BUILD_DIR = os.path.join(_PARENT_DIR, "monaco_component")

# Check if build directory exists
if not os.path.exists(_BUILD_DIR):
    os.makedirs(_BUILD_DIR, exist_ok=True)

# Register the Streamlit custom component
_monaco_component = components.declare_component("monaco_editor", path=_BUILD_DIR)


def render_monaco_editor(
    value:    str  = "",
    language: str  = "Python",
    disabled: bool = False,
    height:   int  = 400,
    key:      str | None = None,
) -> str:
    """
    Render a Monaco (VS Code) editor as a proper Streamlit Component.

    Args:
        value:    Current editor content (passed to frontend).
        language: CodeExplain language name (e.g. "Python", "Java").
        disabled: If True, editor is set to readOnly mode.
        height:   Height of the editor in pixels.
        key:      Stable widget key for state preservation.

    Returns:
        str: The current value of the editor directly from JS.
    """
    # Renders the custom component, returning its current state.
    # The default value is what gets returned initially before user input.
    editor_value = _monaco_component(
        value=value,
        language=language,
        disabled=disabled,
        height=height,
        key=key,
        default=value,
    )
    
    return editor_value if editor_value is not None else value
