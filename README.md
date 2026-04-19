# pyfixer

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-1.0.1-blue)](https://pypi.org/project/py-fixer/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

A drop-in replacement for `python` that runs your scripts normally — but when an error occurs, uses AI to explain what went wrong and suggest a fix, right in your terminal.

Supports **Anthropic Claude**, **Google Gemini**, and **OpenAI**. The provider is detected automatically from your API key.

---

## Key Features

- **AI Error Explanations**: Get plain-English explanations of tracebacks powered by Claude, Gemini, or OpenAI.
- **VS Code Diff View**: See suggested fixes as a side-by-side diff before applying anything.
- **One-Click Apply**: Accept or discard fixes interactively — originals are backed up automatically.
- **Multi-Provider**: Works with Anthropic (`sk-ant-...`), Google Gemini (`AIza...`), and OpenAI (`sk-...`) keys.
- **No lock-in**: Use `--no-explain` to skip AI entirely and behave like plain `python`.

---

## Installation

```bash
pip install py-fixer
```

---

## Quick Start

### 1. Store your API key

```bash
pyfixer login
```

Paste your API key when prompted — you'll also choose a model. Credentials are saved to `~/.config/pyfixer/config.json` (mode 600).

### 2. Run a script

```bash
pyfixer run script.py
```

When an error occurs, pyfixer:
1. Prints the full traceback
2. Explains the error in plain English
3. Opens a **VS Code diff** showing the suggested fix
4. Asks whether to apply it — original is backed up to `.pyfixer-backup/`

```bash
pyfixer run script.py arg1 arg2     # forward args to your script
pyfixer run script.py --no-explain  # traceback only, no AI
```

---

## Commands

| Command | Description |
|---|---|
| `pyfixer login` | Save your API key and choose a model |
| `pyfixer logout` | Remove your stored API key and model |
| `pyfixer run <script>` | Run a script with AI error explanations |
| `pyfixer set-model` | Switch models without re-entering your key |
| `pyfixer install-extension` | Install the VS Code extension for inline fixes |

---

## Requirements

- Python 3.10+
- An Anthropic, Google Gemini, or OpenAI API key
- VS Code (optional, for diff view)

---

## Contributing

Bug reports and pull requests are welcome! Please open an issue at [github.com/ayushisahu222/py-fixer/issues](https://github.com/ayushisahu222/py-fixer/issues).

---

## License

This project is licensed under the MIT License.
