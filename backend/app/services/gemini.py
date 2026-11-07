"""Thin wrapper around the Google Gemini API.

The API key is read from the GEMINI_API_KEY env var (loaded from backend/.env
in app.main). Never hardcode the key in source.
"""
import os
from functools import lru_cache

from google import genai
from google.genai import errors, types

DEFAULT_MODEL = "gemini-3.8-flash"
# Tried in order when the primary model is overloaded (503) or rate-limited (429).
DEFAULT_FALLBACKS = "gemini-3.5-flash,gemini-3.1-flash-lite"


class GeminiNotConfigured(RuntimeError):
    pass


def models() -> list[str]:
    primary = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    fallbacks = os.getenv("GEMINI_FALLBACK_MODELS", DEFAULT_FALLBACKS).split(",")
    chain = [primary] + [m.strip() for m in fallbacks if m.strip()]
    return list(dict.fromkeys(chain))  # dedupe, keep order


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiNotConfigured("GEMINI_API_KEY is not set (see backend/.env.example)")
    # Bound latency: without this the SDK retries 5xx/overload errors with long backoff.
    # We fail fast per model and fall back to the next one instead.
    http_options = types.HttpOptions(
        timeout=25_000,  # ms
        retry_options=types.HttpRetryOptions(attempts=1),
    )
    vertexai = os.getenv("GEMINI_VERTEXAI", "false").lower() == "true"
    if vertexai:
        return genai.Client(api_key=api_key, vertexai=True, http_options=http_options)
    return genai.Client(api_key=api_key, http_options=http_options)


def generate(prompt: str, system_instruction: str | None = None) -> tuple[str, str]:
    """Return (text, model_used). Raises the last error if every model fails."""
    config = types.GenerateContentConfig(system_instruction=system_instruction)
    last_error: Exception | None = None
    for model in models():
        try:
            response = _client().models.generate_content(
                model=model, contents=prompt, config=config
            )
            return (response.text or "").strip(), model
        except errors.APIError as e:
            # 404 = model retired for this key, 429 = quota, 5xx = overloaded: try next.
            if e.code in (404, 429) or (e.code or 0) >= 500:
                last_error = e
                continue
            raise
    raise last_error  # type: ignore[misc]
