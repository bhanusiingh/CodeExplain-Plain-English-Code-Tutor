"""
features/learning.py
--------------------
Learning Assistant parsing logic for CodeExplain: Plain-English Code Tutor.

Responsibilities
----------------
1. Parse the "# Learning Assistant" raw text block into five sub-sections.
2. Return a structured dictionary with safe fallback values.
"""

import re

# Fallback message shown when a sub-section is missing or empty
_FALLBACK_MESSAGE: str = "Information not available."

def parse_learning_assistant(raw_learning: str) -> dict[str, str]:
    """
    Parse a raw "# Learning Assistant" Markdown string into five subsections:
    concepts, prerequisites, difficulty, interview_questions, and next_topic.

    Uses a robust label extraction method with case-insensitive, flexible spacing matches.

    Args:
        raw_learning (str): The raw text under the "# Learning Assistant" heading.

    Returns:
        dict[str, str]: A dictionary with parsed subsection contents.
    """
    # Safe fallback initialization
    result = {
        "concepts": _FALLBACK_MESSAGE,
        "prerequisites": _FALLBACK_MESSAGE,
        "difficulty": _FALLBACK_MESSAGE,
        "interview_questions": _FALLBACK_MESSAGE,
        "next_topic": _FALLBACK_MESSAGE,
    }

    if not raw_learning or not raw_learning.strip():
        return result

    # Define the labels to locate and their stopping labels (the next logical labels)
    # in order to bound the search.
    labels_config = [
        ("concepts", "Concepts Used:", ["Prerequisites:", "Difficulty:", "Interview Questions:", "Next Topic:"]),
        ("prerequisites", "Prerequisites:", ["Difficulty:", "Interview Questions:", "Next Topic:"]),
        ("difficulty", "Difficulty:", ["Interview Questions:", "Next Topic:"]),
        ("interview_questions", "Interview Questions:", ["Next Topic:"]),
        ("next_topic", "Next Topic:", []),
    ]

    for key, start_label, stop_labels in labels_config:
        content = _extract_field(raw_learning, start_label, stop_labels)
        if content:
            result[key] = content

    return result

def _extract_field(block: str, start_label: str, stop_labels: list[str]) -> str:
    """
    Helper to extract text between start_label and the earliest stop_label.
    """
    pattern = re.escape(start_label)

    # Line-level or inline case-insensitive search
    line_match   = re.search(rf"(?im)^{pattern}\s*$", block)
    inline_match = re.search(rf"(?i){pattern}", block)

    match = None
    if line_match and inline_match:
        match = line_match if line_match.start() <= inline_match.start() else inline_match
    elif line_match:
        match = line_match
    elif inline_match:
        match = inline_match

    if not match:
        return ""

    content_start = match.end()
    content_end = len(block)

    for stop in stop_labels:
        sp = re.escape(stop)
        sl_match = re.search(rf"(?im)^{sp}\s*$", block[content_start:])
        si_match = re.search(rf"(?i){sp}", block[content_start:])

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
