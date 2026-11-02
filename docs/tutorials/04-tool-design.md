# Tutorial 4: Tool Design (Level 5)

A tool is a function the model may ask the harness to run. The model proposes; the harness validates and executes.

**Principles**
1. **Few, sharp tools.** Every extra tool is extra context and extra ways to fail.
2. **Validate inputs.** Never trust model arguments. Check types, ranges and allowed values.
3. **Return structured, small output.** `{"ok": true, "result": 345}` beats a wall of text.
4. **Fail loudly and helpfully.** An error message is the model's only way to self-correct.

**Exercise** (`my_harness/tools.py`)

```python
def calculate(a: float, b: float, op: str) -> dict:
    if op not in {"+", "-", "*", "/"}:
        return {"ok": False, "error": f"unknown op {op!r}; use + - * /"}
    if op == "/" and b == 0:
        return {"ok": False, "error": "division by zero"}
    result = {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else None}[op]
    return {"ok": True, "result": result}
```

Then run `harnessquest-quest 5`.
