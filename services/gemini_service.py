"""
services/gemini_service.py
--------------------------
Handles all communication with the Google Gemini API.

Provides:
    generate_response(prompt: str) -> str
    get_api_key_info() -> str           (diagnostic — never logs full key)

DIAGNOSTIC MODE (temporary)
----------------------------
The catch-all Exception block now prints:
  - exception type name
  - exception class (full dotted path)
  - full exception message
  - HTTP status code (when available via .status_code or .code attribute)
and returns the raw error string instead of mapping to a generic message.
This lets us identify the real failure cause from the terminal log.
Remove the diagnostic prints once the real error is identified.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# ── Module-level constants ────────────────────────────────────────────────────
_MODEL_NAME: str = "gemini-2.5-flash"   # Fast, free-tier model (confirmed available)

# Track which key was last configured so we detect key rotation in .env.
# None means the client has never been configured.
_configured_key: str | None = None


# ── Diagnostic helper ─────────────────────────────────────────────────────────

def get_api_key_info() -> str:
    """
    Return a safe, partial representation of the current API key for
    diagnostic purposes.  The full key is NEVER returned or logged.

    Returns:
        str: E.g. "AIzaSyAB..." or "Key not set" if missing.
    """
    load_dotenv(override=True)
    key = (
        st.secrets.get("GEMINI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )
    if not key or not key.strip():
        return "Key not set"
    k = key.strip()
    return f"{k[:8]}... (length: {len(k)})"


# ── Private initialisation ────────────────────────────────────────────────────

def _initialise_client() -> None:
    """
    Configure the Gemini SDK using Streamlit Secrets (production)
    or .env (local development).
    """
    global _configured_key

    load_dotenv(override=True)

    api_key = (
        st.secrets.get("GEMINI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )

    if not api_key or not api_key.strip():
        raise RuntimeError(
            "GEMINI_API_KEY is missing.\n"
            "Add it to either:\n"
            "• Streamlit Secrets (deployment)\n"
            "• .env (local development)"
        )

    api_key = api_key.strip()

    if api_key == _configured_key:
        return

    genai.configure(api_key=api_key)
    _configured_key = api_key


# ── Public API ────────────────────────────────────────────────────────────────

def generate_response(prompt: str) -> str:
    """
    Send a prompt to the Gemini API and return the plain-text response.

    Args:
        prompt (str): The full prompt string to send to Gemini.

    Returns:
        str: The model's plain-text reply, or a diagnostic error string.
    """
    if not prompt or not prompt.strip():
        return "Error: Prompt cannot be empty. Please provide some code or a question."

    try:
        # ── Step 1: configure client ──────────────────────────────────────────
        _initialise_client()

        # ── Step 2: send prompt ───────────────────────────────────────────────
        model = genai.GenerativeModel(model_name=_MODEL_NAME)
        response = model.generate_content(prompt)

        # ── Step 3: extract text ──────────────────────────────────────────────
        raw_text: str = response.text

        if not raw_text or not raw_text.strip():
            return (
                "The model returned an empty response. "
                "Try rephrasing your prompt or using a different code snippet."
            )

        return raw_text.strip()

    # ── Specific handlers ────────────────────────────────────────────────────

    except RuntimeError as exc:
        return f"Configuration Error: {exc}"

    except ValueError as exc:
        return (
            "The model's response was blocked by a safety filter. "
            "Please modify the code snippet and try again.\n"
            f"Details: {exc}"
        )

    except genai.types.BlockedPromptException as exc:  # type: ignore[attr-defined]
        return (
            "Your prompt was blocked by the Gemini safety system. "
            "Please check your input and try again.\n"
            f"Details: {exc}"
        )

    # ── DIAGNOSTIC catch-all ─────────────────────────────────────────────────
    # Prints full exception details to the terminal so the real error can be
    # identified. Returns the raw error string to the UI instead of mapping
    # to a generic message. Remove prints once the cause is confirmed.

    except Exception as exc:
        exc_type_name: str  = type(exc).__name__
        exc_class_path: str = f"{type(exc).__module__}.{type(exc).__qualname__}"
        exc_message: str    = str(exc)

        # Extract HTTP status code if the exception carries one.
        status_code: int | None = (
            getattr(exc, "status_code", None)   # google.api_core style
            or getattr(exc, "code", None)        # grpc / alternate style
        )

        # ── Print to terminal ─────────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("GEMINI DIAGNOSTIC — real exception details")
        print("=" * 60)
        print(f"  Type name   : {exc_type_name}")
        print(f"  Class path  : {exc_class_path}")
        print(f"  HTTP status : {status_code if status_code is not None else 'N/A'}")
        print(f"  Message     :\n{exc_message}")
        print("=" * 60 + "\n")

        # ── Build a UI-safe, user-friendly summary ────────────────────────────
        exc_message_lower = exc_message.lower()
        exc_type_lower = exc_type_name.lower()

        if "connection" in exc_type_lower or "connection" in exc_message_lower or "dns" in exc_message_lower:
            return "Network Error: Cannot connect to Gemini API. Please check your internet connection and try again."

        if "timeout" in exc_type_lower or "deadline" in exc_type_lower or "timeout" in exc_message_lower:
            return "Request Timeout: The request to Gemini API timed out. Please try again in a moment."

        if status_code == 429:
            return "Rate Limit Reached: The Gemini API rate limit has been exceeded. Please wait a moment before trying again."

        if status_code == 403 or "unauthorized" in exc_message_lower or "invalid key" in exc_message_lower:
            return "Invalid API Key: The provided GEMINI_API_KEY is unauthorized or invalid. Please check the key in your .env file."

        if status_code == 400:
            return "Invalid Request: The request parameters are invalid. Check if your code input is too large or contains illegal characters."

        status_part: str = (
            f" [HTTP {status_code}]" if status_code is not None else ""
        )
        return (
            f"API Error{status_part}: {exc_type_name} - {exc_message}\n\n"
            "Please check your configuration or try again later."
        )
