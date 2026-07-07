"""
features/quiz.py
----------------
Quiz generation pipeline for CodeExplain: Plain-English Code Tutor.

Responsibilities
----------------
1. Validate the user's code input.
2. Build the quiz prompt via services/prompts.build_quiz_prompt().
3. Call the Gemini API exactly once via services/gemini_service.generate_response().
4. Parse the single Markdown response into a list of question dicts.
5. Return the list ready for the Streamlit UI to render.

Public API
----------
    run_quiz(code: str, language: str) -> list[dict] | dict
        Full pipeline: validate -> prompt -> ONE API call -> parse -> return.
        On error returns {"error": "..."} matching the explain pipeline style.

    parse_quiz(raw_response: str) -> list[dict]
        Parse a raw Gemini Markdown quiz response into structured dicts.
        Exposed separately for unit testing.

Question dict schema
--------------------
    {
        "question":    str,
        "options":     {"A": str, "B": str, "C": str, "D": str},
        "answer":      str,   # single letter: "A" | "B" | "C" | "D"
        "explanation": str,
    }
"""

import re
from services.prompts import build_quiz_prompt
from services.gemini_service import generate_response

# ── Constants ─────────────────────────────────────────────────────────────────
_EXPECTED_QUESTIONS: int = 5
_VALID_OPTIONS: frozenset[str] = frozenset({"A", "B", "C", "D"})

# Error prefixes returned as plain strings by generate_response() on failure.
_ERROR_PREFIXES: tuple[str, ...] = (
    "Error:",
    "Configuration Error:",
    "Invalid API Key:",
    "Rate Limit Reached:",
    "Network Error:",
    "Unexpected Error:",
    "API Error",
    "The model's response was blocked",
    "Your prompt was blocked",
    "The model returned an empty response",
)


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_quiz(raw_response: str) -> list[dict]:
    """
    Convert a raw Gemini quiz Markdown response into a list of question dicts.

    Strategy
    --------
    1. Split the response on ``# Question N`` headings (regex).
    2. For each question block, extract fields by finding each field label
       (e.g. ``Question:``, ``A.``, ``Correct Answer:``, ``Explanation:``)
       and treating the text until the next label as that field's value.
    3. Validate each field; use a fallback string for any missing field so
       the function never raises — a partial quiz is better than a crash.

    Args:
        raw_response (str): The full text returned by generate_response().

    Returns:
        list[dict]: Parsed questions.  May be empty if the response is
                    completely malformed.
    """
    if not raw_response or not raw_response.strip():
        return []

    # Split on question headings — keep the text between them.
    # Pattern matches: # Question 1, # Question 2, ... (case-insensitive N)
    blocks: list[str] = re.split(
        r"(?im)^#\s*Question\s+\d+\s*$",
        raw_response,
    )
    # blocks[0] is any preamble before the first heading — discard it.
    question_blocks: list[str] = [b.strip() for b in blocks[1:] if b.strip()]

    questions: list[dict] = []

    for block in question_blocks:
        question = _extract_field(block, "Question:", ["A.", "B.", "C.", "D.",
                                                       "Correct Answer:", "Explanation:"])
        opt_a    = _extract_field(block, "A.",          ["B.", "C.", "D.",
                                                         "Correct Answer:", "Explanation:"])
        opt_b    = _extract_field(block, "B.",          ["C.", "D.",
                                                         "Correct Answer:", "Explanation:"])
        opt_c    = _extract_field(block, "C.",          ["D.",
                                                         "Correct Answer:", "Explanation:"])
        opt_d    = _extract_field(block, "D.",          ["Correct Answer:", "Explanation:"])
        raw_ans  = _extract_field(block, "Correct Answer:", ["Explanation:"])
        explanation = _extract_field(block, "Explanation:", [])

        # Normalise answer to a single uppercase letter; default to "A" if invalid.
        answer: str = raw_ans.strip().upper()[:1] if raw_ans.strip() else "A"
        if answer not in _VALID_OPTIONS:
            answer = "A"

        questions.append({
            "question":    question    or "Question not available.",
            "options": {
                "A": opt_a or "Option A not available.",
                "B": opt_b or "Option B not available.",
                "C": opt_c or "Option C not available.",
                "D": opt_d or "Option D not available.",
            },
            "answer":      answer,
            "explanation": explanation or "Explanation not available.",
        })

    return questions


def _extract_field(block: str, start_label: str, stop_labels: list[str]) -> str:
    """
    Extract the text between ``start_label`` and the earliest ``stop_label``
    found after it within ``block``.

    Args:
        block (str):             One question's raw Markdown text.
        start_label (str):       The field label to find (e.g. ``"Question:"``).
        stop_labels (list[str]): Labels that mark the end of this field.

    Returns:
        str: Stripped field value, or ``""`` if the label is not found.
    """
    pattern = re.escape(start_label)

    # Try line-level match first (label on its own line), then inline.
    # Two separate re.search calls avoid the "global flags not at start" error
    # that occurs when (?im) appears inside an alternation branch.
    line_match   = re.search(rf"(?im)^{pattern}\s*$", block)
    inline_match = re.search(rf"(?i){pattern}",        block)

    # Prefer the line-level match; fall back to inline.
    match = None
    if line_match and inline_match:
        match = line_match if line_match.start() <= inline_match.start() else inline_match
    elif line_match:
        match = line_match
    elif inline_match:
        match = inline_match

    if not match:
        return ""

    content_start: int = match.end()
    content_end: int   = len(block)

    # Find the earliest stop label after the start position.
    for stop in stop_labels:
        sp = re.escape(stop)
        # Same two-pattern strategy for stop labels.
        sl_match = re.search(rf"(?im)^{sp}\s*$", block[content_start:])
        si_match = re.search(rf"(?i){sp}",        block[content_start:])

        best_stop = None
        if sl_match and si_match:
            best_stop = sl_match if sl_match.start() <= si_match.start() else si_match
        elif sl_match:
            best_stop = sl_match
        elif si_match:
            best_stop = si_match

        if best_stop:
            candidate = content_start + best_stop.start()
            if candidate < content_end:
                content_end = candidate

    return block[content_start:content_end].strip()



# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_quiz(code: str, language: str) -> list[dict] | dict:
    """
    Run the full Quiz generation pipeline.

    Validates input, builds the prompt, makes a SINGLE Gemini API call,
    and parses the response into a list of question dicts.

    Args:
        code (str):     Raw source code pasted by the user.
        language (str): Language name from the UI selector (e.g. "Python").

    Returns:
        list[dict]: Parsed quiz questions on success.
        dict:       ``{"error": "..."}`` on any failure — never raises.

    Example:
        >>> result = run_quiz("print('hi')", "Python")
        >>> if isinstance(result, dict) and "error" in result:
        ...     print(result["error"])
        ... else:
        ...     print(result[0]["question"])
    """
    # ── Step 1: Input validation ──────────────────────────────────────────────
    if not code or not code.strip():
        return {"error": "Please paste some code before generating a quiz."}

    if not language or not language.strip():
        return {"error": "Please select a programming language from the sidebar."}

    try:
        # ── Step 2: Build the quiz prompt ─────────────────────────────────────
        prompt: str = build_quiz_prompt(code=code, language=language)

        # ── Step 3: ONE Gemini API call ───────────────────────────────────────
        raw_response: str = generate_response(prompt)

        # ── Step 4: Detect service-level errors ───────────────────────────────
        if any(raw_response.startswith(p) for p in _ERROR_PREFIXES):
            return {"error": raw_response}

        # ── Step 5: Parse the Markdown response ───────────────────────────────
        questions: list[dict] = parse_quiz(raw_response)

        if not questions:
            return {
                "error": (
                    "The AI returned a response but no questions could be parsed. "
                    "Please try again with a different code snippet."
                )
            }

        return questions

    except ValueError as exc:
        return {"error": f"Input Error: {exc}"}

    except Exception as exc:
        return {
            "error": (
                f"An unexpected error occurred: {exc}\n\n"
                "Please try again. If the problem persists, check your API key."
            )
        }
