# Tutorial 5: Constraint Management (Level 6)

Agents fail by looping, wandering and burning budget. Constraints are the harness's brakes.

- **Turn limit:** `HarnessRunner(max_turns=...)` stops runaway runs.
- **Loop detection:** HarnessQuest stops when the same command repeats 3 times (`status: "loop_detected"`).
- **Timeouts:** the sandbox kills commands after 15 seconds.
- **Verification gates:** never accept "done" without checking (Level 7).

**Exercise** (`my_harness/guardrails.py`): write a `LoopDetector` that remembers the last N actions and returns `True` when one repeats 3 times, plus a `max_turns` budget.

```python
class LoopDetector:
    def __init__(self, limit=3):
        self.limit, self.recent = limit, []

    def seen_loop(self, action: str) -> bool:
        self.recent.append(action)
        return self.recent[-self.limit:] == [action] * self.limit
```
