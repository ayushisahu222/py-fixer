"""Prompt templates for Claude API calls."""

EXPLAIN_PROMPT_TEMPLATE = """\
You are a Python debugging assistant. A script raised an exception. \
Respond in exactly the following markdown structure. \
Keep the total response under 200 words. No preamble, no closing remarks.

### What went wrong
<one sentence describing the error>

### Why
<one or two sentences explaining the root cause>

### Fix
<one or two sentences describing what to change>

### Corrected code
```python
<corrected version of the relevant code>
```

---

Script source:
```python
{source}
```

Traceback:
```
{traceback}
```
"""
