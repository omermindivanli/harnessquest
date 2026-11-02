# Tutorial 6: Evaluation Patterns (Levels 7 and 17)

You cannot improve what you do not measure.

1. **Deterministic checks first.** File exists? Tests pass? JSON valid? Cheap and exact. This is how HarnessQuest verifies quests (`gamification/checks.py`).
2. **LLM-as-judge for fuzzy output.** `harnessquest.eval.judge.HarnessJudge` scores output against criteria and returns JSON. Use it where code cannot decide, and keep a golden set to catch judge drift.
3. **Benchmarks in CI.** Run a fixed task suite on every PR; fail on score regression.

**Exercise** (`my_harness/verify.py`): write `verify(output: str) -> bool` that rejects empty output and output missing a required marker. Then (`evals.py`) write a `score(cases)` that returns the fraction passing.
