"""Execute user scripts via runpy and capture any exceptions."""

# stdlib
import runpy
import sys
import traceback
from pathlib import Path

# local
from pyfixer import explainer


def run_script(
    script_path: str,
    script_args: list[str],
    api_key: str,
    explain: bool = True,
) -> None:
    """Run a Python script in __main__ context, catching and explaining errors."""
    path = Path(script_path).resolve()

    # Make the user's script see the right sys.argv
    sys.argv = [str(path)] + script_args

    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit:
        # Honour sys.exit() calls from the user's script
        raise
    except BaseException:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)

        if explain:
            explainer.explain_error(str(path), exc_info, api_key)

        # TODO(phase-3): record error to journal before returning
