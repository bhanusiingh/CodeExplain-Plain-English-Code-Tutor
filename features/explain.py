"""
features/explain.py
-------------------
Explain Code pipeline for CodeExplain: Plain-English Code Tutor.

Responsibilities
----------------
1. Validate the user's code input.
2. Build the structured prompt via services/prompts.py.
3. Call the Gemini API exactly once via services/gemini_service.py.
4. Parse the single Markdown response into five named sections.
5. Return a structured result dict ready for the UI to render.

Public API
----------
    run_explanation(code: str, language: str) -> dict[str, str]
        Full pipeline — validate → prompt → API call → parse → return.

    parse_sections(raw_response: str) -> dict[str, str]
        Parse a raw Gemini Markdown response into the five sections.
        Exposed separately so it can be unit-tested independently.
"""

import re
from services.prompts import build_explanation_prompt
from services.gemini_service import generate_response

# ── Section keys — used as dict keys throughout the app ──────────────────────
# Changing these here automatically propagates to the UI rendering layer.
SECTION_SUMMARY      = "summary"
SECTION_LINE_BY_LINE = "line_by_line"
SECTION_TIME         = "time_complexity"
SECTION_SPACE        = "space_complexity"
SECTION_IMPROVEMENTS = "improvements"

# ── Mapping: exact Gemini heading text  →  our internal section key ───────────
# The keys MUST match what build_explanation_prompt() instructs Gemini to use.
_HEADING_MAP: dict[str, str] = {
    "# Summary":                    SECTION_SUMMARY,
    "# Line-by-Line Explanation":   SECTION_LINE_BY_LINE,
    "# Time Complexity":            SECTION_TIME,
    "# Space Complexity":           SECTION_SPACE,
    "# Suggested Improvements":     SECTION_IMPROVEMENTS,
}

# Friendly fallback shown when a section is absent from the Gemini response.
_FALLBACK_MESSAGE: str = (
    "This section was not returned by the AI. "
    "Try rephrasing your code or submitting it again."
)


# ── Public helper ─────────────────────────────────────────────────────────────

def parse_sections(raw_response: str) -> dict[str, str]:
    """
    Split a raw Gemini Markdown response into five named sections.

    The parser works by finding each known heading and treating the text
    between two consecutive headings as that heading's content.
    Missing sections receive a friendly fallback string — the function
    never raises an exception.

    Args:
        raw_response (str): The full text returned by generate_response().

    Returns:
        dict[str, str]: Keys are the SECTION_* constants defined in this
                        module; values are stripped section content strings.
    """
    # Initialise every section with the fallback so missing ones are handled.
    sections: dict[str, str] = {key: _FALLBACK_MESSAGE for key in _HEADING_MAP.values()}

    if not raw_response or not raw_response.strip():
        return sections

    # Build a regex that matches any of the known headings at the start of a line.
    # re.escape handles the "#" character safely.
    heading_pattern = "|".join(re.escape(h) for h in _HEADING_MAP)
    # Split the raw text on each known heading, keeping the heading as a delimiter.
    parts = re.split(rf"^({heading_pattern})$", raw_response, flags=re.MULTILINE)

    # re.split with a capturing group returns: [pre_text, heading, content, heading, content, ...]
    # parts[0] is any text before the first heading — we discard it.
    # parts then alternates: heading at odd indices, content at even indices (starting from 1).
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()
        content = parts[i + 1].strip()
        section_key = _HEADING_MAP.get(heading)
        if section_key:
            sections[section_key] = content if content else _FALLBACK_MESSAGE
        i += 2

    return sections


# ── Public pipeline ───────────────────────────────────────────────────────────

def run_explanation(code: str, language: str) -> dict[str, str]:
    """
    Run the full Explain Code pipeline.

    Validates input, builds the prompt, makes a SINGLE Gemini API call,
    and parses the response into five sections.

    Args:
        code (str):     Raw source code pasted by the user.
        language (str): Language name from the UI selector (e.g. "Python").

    Returns:
        dict[str, str]: Parsed result sections. On any error the dict
                        contains an ``"error"`` key with a user-friendly
                        message, so the UI never receives an exception.

    Example:
        >>> result = run_explanation("print('hi')", "Python")
        >>> print(result["summary"])
    """
    # ── Step 1: Input validation ──────────────────────────────────────────────
    if not code or not code.strip():
        return {"error": "Please paste some code before clicking Explain Code."}

    if not language or not language.strip():
        return {"error": "Please select a programming language from the sidebar."}

    try:
        # ── Step 2: Build the structured prompt ───────────────────────────────
        prompt: str = build_explanation_prompt(code=code, language=language)

        # ── Step 3: ONE Gemini API call ───────────────────────────────────────
        raw_response: str = generate_response(prompt)

        # ── Step 4: Detect service-level errors returned as plain strings ─────
        # generate_response() returns error strings (not exceptions) on failure.
        # We detect them by checking for known error prefixes.
        error_prefixes = (
            "Error:",
            "Configuration Error:",
            "Invalid API Key:",
            "Rate Limit Reached:",
            "Network Error:",
            "Unexpected Error:",
            "The model's response was blocked",
            "Your prompt was blocked",
            "The model returned an empty response",
        )
        if any(raw_response.startswith(prefix) for prefix in error_prefixes):
            return {"error": raw_response}

        # ── Step 5: Parse the Markdown into sections ──────────────────────────
        sections: dict[str, str] = parse_sections(raw_response)

        return sections

    except ValueError as exc:
        # build_explanation_prompt raises ValueError for empty code.
        # This is a safety net in case caller skips Step 1.
        return {"error": f"Input Error: {exc}"}

    except Exception as exc:
        # Catch-all — never let an unhandled exception reach the Streamlit UI.
        return {
            "error": (
                f"An unexpected error occurred: {exc}\n\n"
                "Please try again. If the problem persists, check your API key."
            )
        }
