"""Reusable helper for talking to the Google Gemini API safely.

Keeps all API details in one place so every feature can simply call
get_gemini_response(prompt) and get back (success, text_or_error).
The API key never leaves this file - it is read from the .env file.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# Load environment variables from the .env file (API key, model name)
load_dotenv()

# Fallback to the currently configured model if GEMINI_MODEL is not set
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# Give up after 120 seconds so the app never hangs forever on one request
REQUEST_TIMEOUT_SECONDS = 120

_client = None


def _get_client():
    """Create the Gemini client once and reuse it for every request."""
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Friendly, user-facing message - never show the raw error here
            raise RuntimeError(
                "Missing API key. Add GEMINI_API_KEY to your .env file "
                "(see README for steps)."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def get_gemini_response(prompt: str) -> tuple[bool, str]:
    """Send one prompt to Gemini and return (success, text or friendly error).

    Every feature builds its own prompt and calls this single function,
    which keeps the API logic in exactly one place.
    """
    try:
        client = _get_client()

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_SECONDS * 1000),
            ),
        )

        answer = (response.text or "").strip()
        if not answer:
            return False, (
                "The AI returned an empty response. Please try again, "
                "or rephrase your input."
            )
        return True, answer

    except RuntimeError:
        # Missing API key message is already user-friendly
        raise

    except errors.APIError as err:
        return False, _friendly_api_error(err)

    except Exception:
        # Covers network failures and anything unexpected.
        # Never leak stack traces to the user.
        return False, "Unable to generate a response. Please try again."


def _friendly_api_error(err: errors.APIError) -> str:
    """Translate common Gemini API errors into short student-friendly text."""
    message = str(err.message or err)
    code = getattr(err, "code", None)

    if code == 429 or "quota" in message.lower() or "rate" in message.lower():
        return "Rate limit reached. Please wait a minute and try again."
    if code in (401, 403) or "api key" in message.lower():
        return "The API key is missing or invalid. Check your .env file."
    if code == 503 or "overload" in message.lower():
        return "The AI service is busy right now. Please try again shortly."
    if "deadline" in message.lower() or "timeout" in message.lower():
        return "The AI request took too long. Please try again with shorter notes."
    if code == 404 and "no longer available" in message.lower():
        return "The configured AI model is unavailable. Set GEMINI_MODEL in .env to an available model."
    return "Unable to generate a response. Please try again."
