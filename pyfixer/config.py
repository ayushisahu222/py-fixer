"""File-based storage for the API key and model preference."""

import json
import os
from pathlib import Path

_CONFIG_DIR = Path.home() / ".config" / "pyfixer"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

MODEL_OPTIONS: dict[str, list[tuple[str, str]]] = {
    "anthropic": [
        ("claude-opus-4-7",           "Opus 4.7 (latest)"),
        ("claude-sonnet-4-6",         "Sonnet 4.6 "),
        ("claude-haiku-4-5",         "Haiku 4.5"),
    ],
    "gemini": [
        ("gemini-2.5-pro",        "Gemini 2.5 Pro"),
        ("gemini-2.5-flash",      "Gemini 2.5 Flash"),
        ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite"),
    ],
    "openai": [
        ("gpt-5.4",      "GPT-5.4"),
        ("gpt-5.4-mini", "GPT-5.4 mini"),
        ("gpt-5.3-codex", "GPT-5.3 Codex"),
    ],
}

DEFAULT_MODEL: dict[str, str] = {
    "anthropic": "claude-sonnet-4-7",
    "gemini":    "gemini-2.5-pro",
    "openai":    "gpt-5.4",
}


def _load() -> dict:
    try:
        return json.loads(_CONFIG_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(data, indent=2))
    os.chmod(_CONFIG_FILE, 0o600)


def get_api_key() -> str | None:
    return _load().get("api_key") or None


def set_api_key(key: str) -> None:
    data = _load()
    data["api_key"] = key
    _save(data)


def delete_api_key() -> None:
    data = _load()
    data.pop("api_key", None)
    _save(data)


def get_model() -> str | None:
    return _load().get("model") or None


def set_model(model: str) -> None:
    data = _load()
    data["model"] = model
    _save(data)


def delete_model() -> None:
    data = _load()
    data.pop("model", None)
    _save(data)
