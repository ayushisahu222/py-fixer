"""Click CLI entry point: login, logout, set-model, and run commands."""

# stdlib
import importlib.resources
import shutil
import subprocess
import sys

# third-party
import click
from keyring.errors import PasswordDeleteError

# local
from bug_py import config, runner
from bug_py.explainer import _detect_provider


def _pick_model(provider: str) -> str:
    """Interactively prompt the user to choose a model for the given provider."""
    options = config.MODEL_OPTIONS.get(provider, [])
    if not options:
        return config.DEFAULT_MODEL.get(provider, "")

    click.echo(f"\nAvailable models for {provider}:")
    for i, (model_id, label) in enumerate(options, start=1):
        click.echo(f"  [{i}] {label}")

    default_idx = next(
        (i for i, (mid, _) in enumerate(options, start=1)
         if mid == config.DEFAULT_MODEL.get(provider)),
        1,
    )

    while True:
        raw = click.prompt(
            f"Choose a model",
            default=str(default_idx),
        )
        try:
            choice = int(raw)
            if 1 <= choice <= len(options):
                return options[choice - 1][0]
        except ValueError:
            pass
        click.echo(f"  Please enter a number between 1 and {len(options)}.")


@click.group()
def main() -> None:
    """pyfixer — run Python with AI error explanations."""


@main.command()
def login() -> None:
    """Store your API key and choose a model."""
    click.echo("Enter your API key (it will not be shown as you type):")
    key = click.prompt("API key", hide_input=True)
    try:
        config.set_api_key(key.strip())
        click.echo("API key saved.")
    except Exception:
        click.echo("Error: could not save the API key. Check your keyring configuration.", err=True)
        sys.exit(1)

    provider = _detect_provider(key.strip())
    click.echo(f"Detected provider: {provider}")
    model = _pick_model(provider)
    config.set_model(model)
    click.echo(f"Model set to: {model}")


@main.command()
def logout() -> None:
    """Remove the stored API key from the system keyring."""
    try:
        config.delete_api_key()
        config.delete_model()
        click.echo("API key and model preference removed.")
    except PasswordDeleteError:
        click.echo("No API key was stored.", err=True)
    except Exception:
        click.echo("Error: could not remove the API key.", err=True)
        sys.exit(1)


@main.command("set-model")
def set_model() -> None:
    """Change the AI model without re-entering your API key."""
    api_key = config.get_api_key()
    if not api_key:
        click.echo("No API key found. Run `pyfixer login` first.", err=True)
        sys.exit(1)

    provider = _detect_provider(api_key)
    click.echo(f"Provider: {provider}")
    model = _pick_model(provider)
    config.set_model(model)
    click.echo(f"Model set to: {model}")


@main.command("install-extension")
def install_extension() -> None:
    """Install the pyfixer VS Code extension for inline unsaved-edit fixes."""
    code = shutil.which("code")
    if not code:
        click.echo("VS Code CLI ('code') not found. Open VS Code → Command Palette → 'Shell Command: Install code in PATH', then retry.", err=True)
        sys.exit(1)

    try:
        ref = importlib.resources.files("bug_py.data").joinpath("pyfixer-vscode-0.1.0.vsix")
        with importlib.resources.as_file(ref) as vsix_path:
            result = subprocess.run(
                [code, "--install-extension", str(vsix_path)],
                capture_output=True, text=True,
            )
        if result.returncode == 0:
            click.echo("pyfixer VS Code extension installed. Reload VS Code to activate it.")
        else:
            click.echo(f"Installation failed:\n{result.stderr}", err=True)
            sys.exit(1)
    except FileNotFoundError:
        click.echo("Extension file not found in package. Re-install pyfixer.", err=True)
        sys.exit(1)


@main.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument("script")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option("--no-explain", is_flag=True, default=False, help="Print traceback only; skip AI.")
def run(script: str, args: tuple[str, ...], no_explain: bool) -> None:
    """Run SCRIPT with optional ARGS, explaining errors with AI."""
    api_key = config.get_api_key()

    if not no_explain and not api_key:
        click.echo(
            "No API key found. Run `pyfixer login` to set one, or use --no-explain to skip AI.",
            err=True,
        )
        sys.exit(1)

    try:
        runner.run_script(
            script_path=script,
            script_args=list(args),
            api_key=api_key or "",
            explain=not no_explain,
        )
    except SystemExit as exc:
        sys.exit(exc.code)
    except Exception:
        click.echo("pyfixer encountered an unexpected error. Please report this as a bug.", err=True)
        sys.exit(1)
