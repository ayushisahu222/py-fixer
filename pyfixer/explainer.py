"""Call an AI API to explain a Python exception and render the result."""

# stdlib
import traceback as tb
from pathlib import Path

# third-party
from rich.console import Console
from rich.markdown import Markdown

# local
from pyfixer import config
from pyfixer.prompts import EXPLAIN_PROMPT_TEMPLATE

_MAX_TOKENS = 800

console = Console()


def _detect_provider(api_key: str) -> str:
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    if api_key.startswith("AIza"):
        return "gemini"
    if api_key.startswith("sk-"):
        return "openai"
    return "gemini"  # default fallback


def _call_anthropic(prompt: str, api_key: str, model: str) -> str:
    """Send prompt to Anthropic and return the response text."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_gemini(prompt: str, api_key: str, model: str) -> str:
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text


def _call_openai(prompt: str, api_key: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def explain_error(script_path: str, exc_info: tuple, api_key: str) -> None:
    """Detect provider, resolve model, call the AI API, and render the explanation."""
    path = Path(script_path)

    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        source = "<source unavailable>"

    exc_type, exc_value, exc_tb = exc_info
    traceback_str = "".join(tb.format_exception(exc_type, exc_value, exc_tb))

    prompt = EXPLAIN_PROMPT_TEMPLATE.format(source=source, traceback=traceback_str)
    provider = _detect_provider(api_key)

    # Use stored model preference, fall back to provider default
    model = config.get_model() or config.DEFAULT_MODEL.get(provider, "")

    try:
        if provider == "anthropic":
            response_text = _call_anthropic(prompt, api_key, model)
        elif provider == "openai":
            response_text = _call_openai(prompt, api_key, model)
        else:
            response_text = _call_gemini(prompt, api_key, model)
    except Exception as e:  # noqa: BLE001
        msg = f"{type(e).__name__}: {e}".replace(api_key, "[REDACTED]")
        console.print(f"\n[yellow]Could not reach AI — {msg}[/yellow]")
        return

    console.rule(f"[bold cyan]— AI explanation ({provider} / {model}) —[/bold cyan]")
    console.print(Markdown(response_text))

    from pyfixer import editor
    editor.propose_fix(script_path, response_text)

    # TODO(phase-3): log this error + explanation to the journal
