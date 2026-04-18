"""Keyring-backed storage for the API key and model preference."""

# stdlib
# (none)

# third-party
import keyring

SERVICE_NAME = "pyfixer"
USERNAME = "anthropic_api_key"
MODEL_USERNAME = "selected_model"

# Available models per provider — update as providers release new versions
MODEL_OPTIONS: dict[str, list[tuple[str, str]]] = {
    "anthropic": [
        ("claude-opus-4-7",           "Opus 4.7 (latest)    — most capable"),
        ("claude-opus-4-6",           "Opus 4.6             — most capable"),
        ("claude-opus-4-5",           "Opus 4.5             — most capable"),
        ("claude-sonnet-4-6",         "Sonnet 4.6           — balanced (recommended)"),
        ("claude-sonnet-4-5",         "Sonnet 4.5           — balanced"),
    ],
    "gemini": [
        ("gemini-3-pro",          "Gemini 3 Pro          — most capable"),
        ("gemini-3-flash",        "Gemini 3 Flash        — fast"),
        ("gemini-2.5-pro",        "Gemini 2.5 Pro        — balanced (recommended)"),
        ("gemini-2.5-flash",      "Gemini 2.5 Flash      — fast & cheap"),
        ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite — fastest / cheapest"),
    ],
}

DEFAULT_MODEL: dict[str, str] = {
    "anthropic": "claude-sonnet-4-6",
    "gemini":    "gemini-2.5-pro",
}


def get_api_key() -> str | None:
    """Return the stored API key, or None if not set."""
    return keyring.get_password(SERVICE_NAME, USERNAME)


def set_api_key(key: str) -> None:
    """Persist the API key in the system keyring."""
    keyring.set_password(SERVICE_NAME, USERNAME, key)


def delete_api_key() -> None:
    """Remove the API key from the system keyring."""
    keyring.delete_password(SERVICE_NAME, USERNAME)


def get_model() -> str | None:
    """Return the stored model ID, or None if not set."""
    return keyring.get_password(SERVICE_NAME, MODEL_USERNAME)


def set_model(model: str) -> None:
    """Persist the chosen model ID in the system keyring."""
    keyring.set_password(SERVICE_NAME, MODEL_USERNAME, model)


def delete_model() -> None:
    """Remove the stored model preference from the system keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, MODEL_USERNAME)
    except Exception:
        pass
