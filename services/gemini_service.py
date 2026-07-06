"""
services/gemini_service.py
--------------------------
Handles all communication with the Google Gemini API.

Provides a single reusable function:
    generate_response(prompt: str) -> str

The Gemini client is initialised only once (module-level singleton)
so repeated calls inside the same Streamlit session are efficient.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# ── Load environment variables from .env ─────────────────────────────────────
# load_dotenv() reads the .env file in the project root and injects every
# KEY=VALUE pair into the process environment so os.getenv() can find them.
load_dotenv()

# ── Module-level constants ────────────────────────────────────────────────────
_MODEL_NAME: str = "gemini-1.5-flash"   # Fast, free-tier friendly model

# ── Sentinel to track whether the client has been set up already ─────────────
_client_initialised: bool = False


def _initialise_client() -> None:
    """
    Configure the Gemini SDK with the API key from the environment.

    This function is called at most once per process. If the key is missing
    it raises a clear RuntimeError so the caller can surface a helpful message.

    Raises:
        RuntimeError: When GEMINI_API_KEY is not found in the environment.
    """
    global _client_initialised

    if _client_initialised:
        # Already configured — nothing to do.
        return

    api_key: str | None = os.getenv("GEMINI_API_KEY")

    if not api_key or not api_key.strip():
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add it to your .env file:\n"
            "  GEMINI_API_KEY=your_key_here"
        )

    genai.configure(api_key=api_key.strip())
    _client_initialised = True


def generate_response(prompt: str) -> str:
    """
    Send a prompt to the Gemini API and return the plain-text response.

    Args:
        prompt (str): The full prompt string to send to Gemini.

    Returns:
        str: The model's plain-text reply, stripped of leading/trailing
             whitespace. On any failure, a user-friendly error message
             is returned instead of raising an exception.

    Example:
        >>> result = generate_response("Explain what a for-loop is.")
        >>> print(result)
    """
    # ── Guard: reject empty prompts before hitting the API ───────────────────
    if not prompt or not prompt.strip():
        return "Error: Prompt cannot be empty. Please provide some code or a question."

    try:
        # ── Step 1: ensure the client is ready ───────────────────────────────
        _initialise_client()

        # ── Step 2: create a model instance and send the prompt ──────────────
        model = genai.GenerativeModel(model_name=_MODEL_NAME)
        response = model.generate_content(prompt)

        # ── Step 3: extract and validate the text payload ────────────────────
        # response.text raises ValueError if the response was blocked by safety
        # filters, so we handle that separately below.
        raw_text: str = response.text

        if not raw_text or not raw_text.strip():
            return (
                "The model returned an empty response. "
                "Try rephrasing your prompt or using a different code snippet."
            )

        return raw_text.strip()

    # ── Error handling — ordered from most specific to most general ──────────

    except RuntimeError as exc:
        # Raised by _initialise_client() when the API key is absent.
        return f"Configuration Error: {exc}"

    except ValueError as exc:
        # Raised by response.text when the response was blocked (safety filter).
        return (
            "The model's response was blocked by a safety filter. "
            "Please modify the code snippet and try again.\n"
            f"Details: {exc}"
        )

    except genai.types.BlockedPromptException as exc:  # type: ignore[attr-defined]
        # Raised when the *prompt itself* is flagged before generation starts.
        return (
            "Your prompt was blocked by the Gemini safety system. "
            "Please check your input and try again.\n"
            f"Details: {exc}"
        )

    except Exception as exc:
        # Catch-all for network failures, invalid API keys, rate limits, etc.
        # We inspect the error message string because the google-generativeai
        # SDK wraps most errors in generic Exception / google.api_core.exceptions.
        error_message: str = str(exc).lower()

        if "api_key_invalid" in error_message or "invalid api key" in error_message:
            return (
                "Invalid API Key: The provided GEMINI_API_KEY is not recognised. "
                "Please check your .env file and verify the key at "
                "https://aistudio.google.com/app/apikey"
            )

        if "quota" in error_message or "rate" in error_message or "429" in error_message:
            return (
                "Rate Limit Reached: You have exceeded the Gemini API quota. "
                "Please wait a moment and try again, or check your usage at "
                "https://aistudio.google.com/app/apikey"
            )

        if (
            "network" in error_message
            or "connection" in error_message
            or "timeout" in error_message
            or "unreachable" in error_message
        ):
            return (
                "Network Error: Could not reach the Gemini API. "
                "Please check your internet connection and try again."
            )

        # Unknown / unexpected error — surface the raw message for debugging.
        return (
            f"Unexpected Error: {exc}\n\n"
            "If this keeps happening, please check your API key and internet connection."
        )
