"""
utils/file_handler.py
----------------------
Reusable file-upload utilities for CodeExplain: Plain-English Code Tutor.

Public API
----------
    supported_extensions() -> tuple[str, ...]
        Returns all accepted file extensions.

    detect_language(filename: str) -> str
        Maps a filename's extension to a canonical language name.

    read_uploaded_file(uploaded_file) -> tuple[str, str]
        Validates and decodes an uploaded Streamlit UploadedFile object.
        Returns (content, error_message).  Exactly one of the two is
        non-empty — never both, never neither.

Design decisions
----------------
- All logic lives here so app.py contains no upload business rules.
- read_uploaded_file() returns a (content, error) tuple rather than
  raising exceptions so the Streamlit caller never needs a try/except.
- The 1 MB size limit is enforced before attempting to decode the bytes,
  so malformed large files never touch the decoder.
- UTF-8 is attempted first; latin-1 is used as a lossless fallback for
  files that contain extended ASCII characters (common in C/C++ source).
"""

from __future__ import annotations

# ── Constants ─────────────────────────────────────────────────────────────────

# Map of supported file extensions → canonical language display names.
# Keys must be lowercase and include the leading dot.
_EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py":   "Python",
    ".java": "Java",
    ".cpp":  "C++",
    ".c":    "C",
    ".js":   "JavaScript",
}

# 1 MB maximum upload size (in bytes).
_MAX_FILE_SIZE_BYTES: int = 1 * 1024 * 1024


# ── Public helpers ─────────────────────────────────────────────────────────────

def supported_extensions() -> tuple[str, ...]:
    """
    Return a tuple of all accepted file extensions (with leading dot).

    Used by the Streamlit file_uploader's ``type`` parameter.

    Returns:
        tuple[str, ...]: E.g. ``(".py", ".java", ".cpp", ".c", ".js")``.
    """
    return tuple(_EXTENSION_LANGUAGE_MAP.keys())


def detect_language(filename: str) -> str:
    """
    Detect the programming language from a filename's extension.

    Matching is case-insensitive so ``Main.JAVA`` is treated the same
    as ``Main.java``.

    Args:
        filename (str): The original filename (e.g. ``"bubble_sort.cpp"``).

    Returns:
        str: Canonical language name (e.g. ``"C++"``) or ``"Plain Text"``
             for any unrecognised extension.  Never raises.
    """
    if not filename:
        return "Plain Text"

    # rsplit keeps only the last extension, handling names like "file.bak.py".
    parts = filename.rsplit(".", 1)
    if len(parts) < 2:
        return "Plain Text"

    ext: str = f".{parts[-1].lower()}"
    return _EXTENSION_LANGUAGE_MAP.get(ext, "Plain Text")


def read_uploaded_file(uploaded_file) -> tuple[str, str]:
    """
    Validate and decode a Streamlit ``UploadedFile`` object.

    Validation rules (in order):
        1. File must not be None.
        2. File must not be empty (0 bytes).
        3. File must not exceed 1 MB.
        4. File content must be decodable as UTF-8 or latin-1.

    Decoding strategy:
        - Try UTF-8 first (standard for modern source code).
        - Fall back to latin-1 (covers all 256 byte values losslessly)
          so extended-ASCII files (common in C/C++) are handled correctly.

    Args:
        uploaded_file: A ``streamlit.runtime.uploaded_file_manager.UploadedFile``
                       instance returned by ``st.file_uploader()``.
                       Accepts ``None`` safely.

    Returns:
        tuple[str, str]: ``(content, error_message)``.
            - On success: ``(non-empty string, "")``
            - On failure: ``("", user-friendly error string)``
    """
    # ── Guard 1: no file selected ─────────────────────────────────────────────
    if uploaded_file is None:
        return "", "No file was provided."

    # ── Guard 2: read raw bytes ───────────────────────────────────────────────
    try:
        raw_bytes: bytes = uploaded_file.read()
    except Exception as exc:
        return "", f"Could not read the file: {exc}"

    # ── Guard 3: empty file ───────────────────────────────────────────────────
    if not raw_bytes:
        return (
            "",
            f"The file '{uploaded_file.name}' is empty. "
            "Please upload a file that contains source code.",
        )

    # ── Guard 4: size limit ───────────────────────────────────────────────────
    size_bytes: int = len(raw_bytes)
    if size_bytes > _MAX_FILE_SIZE_BYTES:
        size_kb: float = size_bytes / 1024
        return (
            "",
            f"The file '{uploaded_file.name}' is too large "
            f"({size_kb:.1f} KB). "
            "Maximum allowed size is 1 MB. "
            "Please upload a smaller file.",
        )

    # ── Guard 5: decode ───────────────────────────────────────────────────────
    for encoding in ("utf-8", "latin-1"):
        try:
            content: str = raw_bytes.decode(encoding)
            return content, ""
        except (UnicodeDecodeError, ValueError):
            continue

    return (
        "",
        f"The file '{uploaded_file.name}' could not be decoded. "
        "Please ensure it is a plain-text source code file.",
    )
