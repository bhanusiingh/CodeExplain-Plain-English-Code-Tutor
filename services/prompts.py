"""
services/prompts.py
-------------------
Prompt templates for CodeExplain: Plain-English Code Tutor.

All prompts are designed to produce consistent, structured,
beginner-friendly Markdown responses from the Gemini API.

Public functions
----------------
    build_explanation_prompt(code: str, language: str) -> str
        Returns the full prompt string to send to Gemini for a
        complete code analysis (summary, line-by-line, complexity,
        improvements).

    build_quiz_prompt(code: str, language: str) -> str
        Returns the full prompt string to send to Gemini for a
        five-question multiple-choice quiz based on the submitted code.

Design principles
-----------------
- Role assignment   : Tell Gemini exactly who it is.
- Hard constraints  : Tell Gemini what it must never do.
- Strict structure  : Require exact Markdown headings in a fixed order.
- Tone control      : Enforce beginner-friendly, jargon-free language.
- Grounding         : Prohibit hallucination; errors must be reported.
"""

# ---------------------------------------------------------------------------
# Supported languages with their canonical display names.
# Adding a new language here is the only change needed to extend support.
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES: dict[str, str] = {
    "python":     "Python",
    "java":       "Java",
    "javascript": "JavaScript",
    "c++":        "C++",
    "c":          "C",
}


def _normalise_language(language: str) -> str:
    """
    Return the canonical display name for a language string.

    Falls back to the original string (title-cased) when the language
    is not in SUPPORTED_LANGUAGES, so the function never crashes on an
    unexpected input.

    Args:
        language (str): Raw language name from the UI selector.

    Returns:
        str: Canonical display name, e.g. "Python", "Java".
    """
    return SUPPORTED_LANGUAGES.get(language.lower().strip(), language.strip().title())


# ---------------------------------------------------------------------------
# Section heading constants — defined once so they are never mistyped.
# The values MUST match the headings listed in the user-facing requirements.
# ---------------------------------------------------------------------------
_H_SUMMARY          = "# Summary"
_H_LINE_BY_LINE     = "# Line-by-Line Explanation"
_H_TIME_COMPLEXITY  = "# Time Complexity"
_H_SPACE_COMPLEXITY = "# Space Complexity"
_H_IMPROVEMENTS     = "# Suggested Improvements"


def build_explanation_prompt(code: str, language: str) -> str:
    """
    Build the full prompt to send to Gemini for a complete code analysis.

    The prompt instructs Gemini to act as a Senior Software Engineer and
    Programming Instructor and to produce five structured Markdown sections
    in a fixed order.

    Args:
        code (str):     The source code snippet pasted by the user.
        language (str): The programming language selected in the UI
                        (e.g. "Python", "Java").

    Returns:
        str: A complete, ready-to-send prompt string.

    Raises:
        ValueError: If ``code`` is empty or contains only whitespace.
    """
    if not code or not code.strip():
        raise ValueError(
            "code must not be empty. "
            "Validate the input before calling build_explanation_prompt()."
        )

    canonical_language: str = _normalise_language(language)

    # ------------------------------------------------------------------
    # The prompt is assembled from three logical sections:
    #   1. ROLE   — who Gemini must pretend to be.
    #   2. RULES  — hard constraints it must never break.
    #   3. TASK   — the exact output format it must produce.
    # ------------------------------------------------------------------

    role_block: str = (
        "You are a Senior Software Engineer and Programming Instructor "
        "with 15 years of experience teaching beginners how to read and "
        "understand code.\n"
        "Your job is to analyse the {language} code provided below and "
        "explain it clearly so that a complete beginner can understand it."
    ).format(language=canonical_language)

    rules_block: str = (
        "RULES — follow every rule exactly:\n"
        "1. Write in simple, plain English. Avoid or define any technical term you use.\n"
        "2. Never invent information that is not present in the code.\n"
        "3. If the code contains syntax errors or logical bugs, explain the errors "
        "   instead of pretending the code is correct.\n"
        "4. If the time or space complexity cannot be determined exactly, state your "
        "   assumption clearly (e.g. 'Assuming n is the length of the input list ...').\n"
        "5. Do not include emojis anywhere in your response.\n"
        "6. Do not add any introduction before the first heading.\n"
        "7. Do not add any conclusion or closing statement after the last section.\n"
        "8. Use only the Markdown headings listed in the OUTPUT FORMAT below. "
        "   Do not add extra headings or sub-headings at the top level.\n"
        "9. Keep every explanation concise but complete. Prefer short sentences.\n"
        "10. When explaining a line of code, always start with the line number "
        "    followed by a dash, for example:  Line 1 - ..."
    )

    output_format_block: str = (
        "OUTPUT FORMAT — produce exactly these five sections in this exact order.\n"
        "Use the heading text exactly as written (including the # character):\n\n"
        "{h_summary}\n"
        "Write 2 to 4 sentences describing what the code does as a whole. "
        "Focus on the purpose and outcome, not on implementation details.\n\n"
        "{h_line_by_line}\n"
        "Explain every line (or every logical block) individually. "
        "Use EXACTLY this format for each entry — three lines per entry, no bullet points:\n"
        "Line <number>\n"
        "`<the exact source code from that line>`\n"
        "<plain-English explanation in one or two sentences>\n\n"
        "For a group of consecutive lines that work together (e.g. a for-loop body), use:\n"
        "Lines <start>-<end>\n"
        "`<the source code for those lines>`\n"
        "<plain-English explanation in one or two sentences>\n\n"
        "Separate each entry with a single blank line. "
        "Do NOT use dashes between the label and explanation. "
        "Do NOT add extra headings, bullet points, or numbered lists between entries.\n\n"
        "{h_time_complexity}\n"
        "State the Big-O time complexity (e.g. O(n), O(n^2), O(1)).\n"
        "Explain in one or two plain-English sentences why the code has that complexity.\n"
        "If you cannot determine it exactly, state your assumptions.\n\n"
        "{h_space_complexity}\n"
        "State the Big-O space complexity.\n"
        "Explain in one or two plain-English sentences why the code uses that much memory.\n"
        "If you cannot determine it exactly, state your assumptions.\n\n"
        "{h_improvements}\n"
        "List 3 to 5 concrete, actionable improvements a beginner could make to this code.\n"
        "For each improvement:\n"
        "  - State what the problem or limitation is.\n"
        "  - State what the beginner should do to fix or improve it.\n"
        "Do not rewrite the full code. Short illustrative snippets are allowed.\n\n"
        "# Learning Assistant\n\n"
        "Concepts Used:\n"
        "- <list concepts used>\n\n"
        "Prerequisites:\n"
        "- <list prerequisites>\n\n"
        "Difficulty:\n"
        "<level and brief reasoning>\n\n"
        "Interview Questions:\n"
        "1. <question 1>\n"
        "2. <question 2>\n"
        "3. <question 3>\n\n"
        "Next Topic:\n"
        "<suggested next topic>"
    ).format(
        h_summary         = _H_SUMMARY,
        h_line_by_line    = _H_LINE_BY_LINE,
        h_time_complexity = _H_TIME_COMPLEXITY,
        h_space_complexity= _H_SPACE_COMPLEXITY,
        h_improvements    = _H_IMPROVEMENTS,
    )

    # Assemble the final prompt.
    # The code is placed at the end inside a fenced block so Gemini never
    # confuses the code for instructions.
    prompt: str = (
        "{role}\n\n"
        "{rules}\n\n"
        "{output_format}\n\n"
        "---\n\n"
        "CODE TO ANALYSE ({language}):\n"
        "```{language_lower}\n"
        "{code}\n"
        "```"
    ).format(
        role            = role_block,
        rules           = rules_block,
        output_format   = output_format_block,
        language        = canonical_language,
        language_lower  = canonical_language.lower(),
        code            = code.strip(),
    )

    return prompt


# ---------------------------------------------------------------------------
# Quiz prompt
# ---------------------------------------------------------------------------

def build_quiz_prompt(code: str, language: str) -> str:
    """
    Build the full prompt to send to Gemini for a five-question quiz.

    The prompt instructs Gemini to produce exactly five multiple-choice
    questions in a strict, machine-parseable Markdown format.  Questions
    cover: overall purpose, line-by-line logic, output prediction,
    complexity, and improvement concepts — never trivial syntax memorisation.

    Reuses _normalise_language() from this module.

    Args:
        code (str):     The source code snippet pasted by the user.
        language (str): The programming language selected in the UI.

    Returns:
        str: A complete, ready-to-send prompt string.

    Raises:
        ValueError: If ``code`` is empty or contains only whitespace.
    """
    if not code or not code.strip():
        raise ValueError(
            "code must not be empty. "
            "Validate the input before calling build_quiz_prompt()."
        )

    canonical_language: str = _normalise_language(language)

    role_block: str = (
        "You are a Senior Software Engineer and Programming Instructor "
        "who creates multiple-choice quizzes to help beginners understand code. "
        "Your quizzes focus on comprehension, logic, and reasoning — "
        "never on memorising syntax."
    )

    rules_block: str = (
        "RULES — follow every rule exactly:\n"
        "1. Generate EXACTLY five questions. No more, no fewer.\n"
        "2. Base every question strictly on the provided code. "
        "   Do not invent behaviour that is not in the code.\n"
        "3. If the code contains errors, ask questions about those errors.\n"
        "4. Each question must belong to a different category:\n"
        "   Q1 — overall purpose of the code\n"
        "   Q2 — what a specific line or block does\n"
        "   Q3 — what the output or return value would be\n"
        "   Q4 — time or space complexity\n"
        "   Q5 — how the code could be improved\n"
        "5. Each question must have exactly four options labelled A, B, C, D.\n"
        "6. Exactly one option must be correct.\n"
        "7. The 'Correct Answer:' field must contain ONLY the single letter "
        "   A, B, C, or D — nothing else.\n"
        "8. The 'Explanation:' must be one or two plain-English sentences.\n"
        "9. Do not add any text before '# Question 1' or after the last Explanation.\n"
        "10. Do not include emojis."
    )

    # The output format uses explicit field labels so the parser can split
    # on them reliably using simple string matching — no regex required for
    # the per-field extraction.
    output_format_block: str = (
        "OUTPUT FORMAT — repeat this block exactly five times "
        "(replacing N with 1, 2, 3, 4, 5):\n\n"
        "# Question N\n\n"
        "Question:\n"
        "<the question text>\n\n"
        "A.\n"
        "<option A text>\n\n"
        "B.\n"
        "<option B text>\n\n"
        "C.\n"
        "<option C text>\n\n"
        "D.\n"
        "<option D text>\n\n"
        "Correct Answer:\n"
        "<single letter: A, B, C, or D>\n\n"
        "Explanation:\n"
        "<one or two sentences explaining why the answer is correct>"
    )

    prompt: str = (
        "{role}\n\n"
        "{rules}\n\n"
        "{output_format}\n\n"
        "---\n\n"
        "CODE TO QUIZ ({language}):\n"
        "```{language_lower}\n"
        "{code}\n"
        "```"
    ).format(
        role           = role_block,
        rules          = rules_block,
        output_format  = output_format_block,
        language       = canonical_language,
        language_lower = canonical_language.lower(),
        code           = code.strip(),
    )

    return prompt
