"""Level 5 reference: a validated tool with structured output."""


def calculate(a, b, op):
    if op not in {"+", "-", "*", "/"}:
        return {"ok": False, "error": f"unknown op {op!r}; use + - * /"}
    if op == "/" and b == 0:
        return {"ok": False, "error": "division by zero"}
    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    else:
        result = a / b
    return {"ok": True, "result": result}
