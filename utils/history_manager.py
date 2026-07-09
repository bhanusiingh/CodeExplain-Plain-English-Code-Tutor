"""
utils/history_manager.py
------------------------
In-session history manager for CodeExplain: Plain-English Code Tutor.

All history is stored exclusively in st.session_state — no files, no DB.
History survives Streamlit reruns but is lost when the browser tab closes
(which is intentional: this is a session-only feature).

Public API
----------
    init_history()
        Initialise st.session_state["history"] if it does not exist.
        Call once at the top of main() before any history read.

    save_history(code, language, analysis, quiz, filename, active_view)
        Append a new history item.  Duplicate-consecutive and failed
        requests are silently skipped.  Oldest item is removed when the
        list exceeds MAX_HISTORY_ITEMS.

    load_history() -> list[dict]
        Return the full history list (newest first).

    restore_history(item_id) -> dict | None
        Return the history item with the given id, or None if not found.

    delete_history(item_id)
        Remove the item with the given id from history.

    clear_history()
        Remove all history items.

    generate_history_title(code, language, filename) -> str
        Derive a human-readable title for a history item.

History item schema
-------------------
    {
        "id":          str,        # unique uuid4
        "timestamp":   datetime,   # Python datetime object
        "title":       str,        # human-readable label
        "language":    str,        # e.g. "Python"
        "code":        str,        # raw source code
        "analysis":    dict | None,# explain pipeline results dict
        "quiz":        list | None,# quiz question list
        "active_view": str,        # "explain" | "quiz" | "both"
        "filename":    str,        # uploaded filename, or ""
    }
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any

import streamlit as st

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_HISTORY_ITEMS: int = 30
_SESSION_KEY: str      = "history"

# Section keys from the explain pipeline (mirrors features/explain.py constants)
_SECTION_KEYS: tuple[str, ...] = (
    "summary",
    "line_by_line",
    "time_complexity",
    "space_complexity",
    "improvements",
)


# ── Initialisation ────────────────────────────────────────────────────────────

def init_history() -> None:
    """
    Initialise st.session_state["history"] to an empty list if not present.

    Must be called once at the very start of main(), before any history
    read or write.  Safe to call multiple times (idempotent).
    """
    if _SESSION_KEY not in st.session_state:
        st.session_state[_SESSION_KEY] = []


# ── Write ─────────────────────────────────────────────────────────────────────

def save_history(
    code: str,
    language: str,
    analysis: dict[str, str] | None = None,
    quiz: list[dict] | None = None,
    filename: str = "",
    active_view: str = "explain",
) -> None:
    """
    Append a new history item to st.session_state["history"].

    Rules:
      - Skips if both analysis and quiz are None/empty (failed request).
      - Skips if the most-recent item has identical code + language (dedup).
      - Trims the list to MAX_HISTORY_ITEMS by removing the oldest entry.

    Args:
        code (str):          Raw source code snippet.
        language (str):      Programming language name.
        analysis (dict):     Explain pipeline result, or None.
        quiz (list):         Quiz question list, or None.
        filename (str):      Uploaded filename if any, else "".
        active_view (str):   "explain" | "quiz" | "both".
    """
    init_history()

    # Skip failed requests: analysis has "error" key, or quiz dict has "error"
    if analysis and "error" in analysis:
        analysis = None
    if isinstance(quiz, dict) and "error" in quiz:
        quiz = None

    if not analysis and not quiz:
        return  # nothing useful to save

    history: list[dict] = st.session_state[_SESSION_KEY]

    # Duplicate-consecutive prevention
    if history:
        last = history[0]   # list is newest-first
        if (
            last["code"].strip() == code.strip()
            and last["language"] == language
        ):
            # Update in place: add new results without creating a duplicate
            if analysis:
                last["analysis"] = analysis
            if quiz:
                last["quiz"] = quiz
            last["active_view"] = active_view
            return

    title: str = generate_history_title(code, language, filename)
    item: dict[str, Any] = {
        "id":          str(uuid.uuid4()),
        "timestamp":   datetime.now(),
        "title":       title,
        "language":    language,
        "code":        code,
        "analysis":    analysis,
        "quiz":        quiz,
        "active_view": active_view,
        "filename":    filename,
    }

    # Insert at front (newest first)
    history.insert(0, item)

    # Trim to max size
    if len(history) > MAX_HISTORY_ITEMS:
        history.pop()   # remove oldest (last element)

    st.session_state[_SESSION_KEY] = history


# ── Read ──────────────────────────────────────────────────────────────────────

def load_history() -> list[dict]:
    """
    Return the full history list, newest first.

    Returns:
        list[dict]: May be empty. Never raises.
    """
    init_history()
    return list(st.session_state.get(_SESSION_KEY, []))


def restore_history(item_id: str) -> dict | None:
    """
    Return the history item with the given id, or None if not found.

    Args:
        item_id (str): The ``id`` field of the desired history item.

    Returns:
        dict | None: The full history item, or None.
    """
    for item in load_history():
        if item["id"] == item_id:
            return item
    return None


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_history(item_id: str) -> None:
    """
    Remove the item with the given id from history.

    Args:
        item_id (str): The ``id`` field of the item to remove.
    """
    init_history()
    st.session_state[_SESSION_KEY] = [
        item for item in st.session_state[_SESSION_KEY]
        if item["id"] != item_id
    ]


def clear_history() -> None:
    """Remove all history items."""
    st.session_state[_SESSION_KEY] = []


# ── Title generation ──────────────────────────────────────────────────────────

def generate_history_title(
    code: str,
    language: str,
    filename: str = "",
) -> str:
    """
    Derive a short, human-readable title for a history item.

    Priority order:
        1. Uploaded filename (e.g. "bubble_sort.py").
        2. First function name found in the code (e.g. "bubble_sort").
        3. First class name found in the code (e.g. "Calculator").
        4. Language + short timestamp (e.g. "Python  14:03").

    Args:
        code (str):      Raw source code.
        language (str):  Programming language name.
        filename (str):  Uploaded filename, or "".

    Returns:
        str: A short title, max ~40 characters, never raises.
    """
    try:
        # Priority 1: uploaded filename
        if filename and filename.strip():
            return filename.strip()[:40]

        stripped = code.strip()

        # Priority 2: first function name
        fn_match = re.search(
            r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)"       # Python
            r"|\bvoid\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("  # Java/C/C++ void
            r"|\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)"  # JS
            r"|\bstatic\s+\w+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",  # Java static
            stripped,
        )
        if fn_match:
            name = next(g for g in fn_match.groups() if g)
            return name[:40]

        # Priority 3: first class name
        cls_match = re.search(
            r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)",
            stripped,
        )
        if cls_match:
            return cls_match.group(1)[:40]

        # Priority 4: language + time
        ts = datetime.now().strftime("%H:%M")
        return f"{language}  {ts}"

    except Exception:
        return f"{language} Session"


# ── Grouping helper ───────────────────────────────────────────────────────────

def group_history_by_date(history: list[dict]) -> dict[str, list[dict]]:
    """
    Group a history list (newest-first) by relative date label.

    Labels: "Today", "Yesterday", or "DD Mon YYYY".

    Args:
        history (list[dict]): Output of load_history().

    Returns:
        dict[str, list[dict]]: Ordered dict: label → [items].
    """
    from collections import OrderedDict

    today     = datetime.now().date()
    groups: dict[str, list[dict]] = OrderedDict()

    for item in history:
        ts   = item["timestamp"]
        date = ts.date() if isinstance(ts, datetime) else today

        if date == today:
            label = "Today"
        elif (today - date).days == 1:
            label = "Yesterday"
        else:
            label = date.strftime("%d %b %Y")

        groups.setdefault(label, []).append(item)

    return groups
