# pyfixer

`pyfixer` is a drop-in replacement for `python` that runs your scripts normally but, when an error occurs, prints the real traceback and then uses AI to give you a plain-language explanation of what went wrong, why it happened, and how to fix it — all directly in your terminal.

Supports **Anthropic Claude** and **Google Gemini**. The provider is detected automatically from your API key.

## Installation

```bash
pip install pyfixer
```

## Usage

### Store your API key (once)

```bash
pyfixer login
```

Paste your Anthropic (`sk-ant-...`) or Gemini (`AIza...`) API key when prompted. The key is stored securely in your system keyring — never on disk or in any file.

### Run a script

```bash
pyfixer run script.py
pyfixer run script.py arg1 arg2     # extra args are forwarded to the script
pyfixer run script.py --no-explain  # show traceback only, skip AI
```

When an error occurs, pyfixer:
1. Prints the full traceback
2. Explains the error in plain English
3. Suggests a fix and opens a **VS Code diff** showing exactly what changed (green = added, red = removed)
4. Asks if you want to apply the fix directly to your file

### Change model

```bash
pyfixer set-model
```

### Remove your stored API key

```bash
pyfixer logout
```


