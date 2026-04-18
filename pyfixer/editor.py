"""Phase 2: auto-apply suggested fixes shown as a VS Code diff in the file."""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import click
from rich.console import Console

console = Console()

_PENDING_FIX = Path.home() / ".pyfixer-pending-fix.json"
_ACTIVE_FILE = Path.home() / ".pyfixer-extension-active"

_VSCODE_MAC = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"


def _extract_corrected_code(response_text: str) -> str | None:
    """Pull the Python code block from the ### Corrected code section."""
    match = re.search(
        r"###\s*Corrected code\s*```python\s*(.*?)```",
        response_text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return None


def _find_code_cli() -> str | None:
    """Find the VS Code 'code' CLI in PATH or the macOS app bundle."""
    if cli := shutil.which("code"):
        return cli
    if Path(_VSCODE_MAC).exists():
        return _VSCODE_MAC
    return None


def propose_fix(script_path: str, response_text: str) -> None:
    """Open a VS Code diff showing the suggested fix directly in the file."""
    suggested_code = _extract_corrected_code(response_text)
    if not suggested_code:
        return

    path = Path(script_path)
    try:
        path.read_text(encoding="utf-8")
    except OSError:
        return

    code_cli = _find_code_cli()
    if code_cli:
        _show_diff_in_vscode(path, suggested_code, code_cli)
    else:
        _apply_via_extension(path, suggested_code) if _ACTIVE_FILE.exists() else _apply_direct(path, suggested_code)


def _show_diff_in_vscode(path: Path, suggested_code: str, code_cli: str) -> None:
    """Write suggested fix to a temp file, open VS Code diff, then ask to apply."""
    suffix = path.suffix or ".py"
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=f".suggested{suffix}",
        prefix=path.stem + "_",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(suggested_code + "\n")
        tmp_path = Path(tmp.name)

    subprocess.Popen([
        code_cli,
        "--diff",
        str(path.resolve()),
        str(tmp_path),
    ])
    console.print(
        f"[bold cyan]Diff opened in VS Code[/bold cyan] — "
        f"[green]green = added[/green], [red]red = removed[/red]"
    )

    if click.confirm("\nApply this fix?", default=False):
        backup_dir = path.parent / ".pyfixer-backup"
        backup_dir.mkdir(exist_ok=True)
        shutil.copy2(path, backup_dir / path.name)
        path.write_text(suggested_code + "\n", encoding="utf-8")
        console.print(f"[bold green]Fix applied to {path.name}[/bold green]")
    else:
        console.print("[dim]Fix discarded.[/dim]")

    tmp_path.unlink(missing_ok=True)


def _apply_via_extension(path: Path, content: str) -> None:
    """Hand the fix to the VS Code extension as an unsaved edit."""
    _PENDING_FIX.write_text(
        json.dumps({"file": str(path.resolve()), "content": content + "\n"}),
        encoding="utf-8",
    )
    console.print("[bold green]Fix sent to VS Code — save (Ctrl+S) to accept or undo (Ctrl+Z) to reject[/bold green]")


def _apply_direct(path: Path, content: str) -> None:
    """Write the fix directly to disk when no editor integration is available."""
    backup_dir = path.parent / ".pyfixer-backup"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / path.name
    shutil.copy2(path, backup_path)

    path.write_text(content + "\n", encoding="utf-8")
    console.print(f"[bold green]Fix applied to {path.name}[/bold green]")
    console.print(f"[dim]Original backed up to {backup_path}[/dim]")
