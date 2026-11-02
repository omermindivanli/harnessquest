# Tutorial 9: Observability (Level 12)

If you cannot see what the agent did, you cannot debug it. Record one **span per turn**: model, tokens, duration, tools called, status.

```python
import time

class Tracer:
    def __init__(self):
        self.spans = []

    def span(self, turn, model, tokens, started, tools, status):
        self.spans.append({"turn": turn, "model": model, "tokens": tokens,
                           "duration": round(time.time() - started, 3),
                           "tools": tools, "status": status})
```

Print it as a table, write JSON lines, or export to OpenTelemetry later.

**Exercise** (`my_harness/telemetry.py`): implement the tracer and call it from your own loop.
