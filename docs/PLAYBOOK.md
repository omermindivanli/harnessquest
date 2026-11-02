# HarnessQuest Playbook: what to build at every level

Run all commands from the folder where you want your own harness to live (the
"workspace"). From Level 4 on, you build a small harness yourself in `./my_harness/`.
`harnessquest-quest <level>` then checks your files. No LLM is needed for levels 2-20.

```bash
mkdir my-harness-journey && cd my-harness-journey
harnessquest-quest --list
harnessquest-quest 1 --provider mock        # offline demo, or use ollama/openai/anthropic
```

A check passes when the expected file exists, is non-trivial, and contains the key
concept (the exact keywords are in `harnessquest/gamification/checks.py`). The checks
are deliberately light: the goal is the thinking. Build the real thing, not the minimum.

| Lv | Concept | Create in `./my_harness/` | Build this |
|----|---------|---------------------------|------------|
| 1 | The agent loop | n/a | Run any provider; the agent lists files and finishes. |
| 2 | Sandbox | n/a | Nothing to write. The check proves the built-in sandbox blocks `../` escapes, sibling-folder escapes and `rm -rf /`. Read `core/sandbox.py`. |
| 3 | Context map | `AGENTS.md` in the workspace root | A short map of your project (under 8000 chars). It must be injected into the system prompt. |
| 4 | Token budget | `context.py` | A function that trims or summarizes history to a token budget. |
| 5 | Tools | `tools.py` | A validated `calculate(a, b, op)` tool. Reject bad ops and divide-by-zero. |
| 6 | Constraints | `guardrails.py` | `max_turns` plus loop detection (same action 3x means stop). |
| 7 | Verification | `verify.py` | A gate that checks the agent's output before accepting "done". |
| 8 | Memory | `memory.py` | Save and resume state with JSON. |
| 9 | Providers | `providers.py` | Try a primary model, `except` and fall back to a secondary. |
| 10 | Local LLMs | `ollama_notes.md` | Notes from running a task on Ollama. |
| 11 | NIM | `nim_notes.md` | Notes from running a task on NVIDIA NIM. |
| 12 | Observability | `telemetry.py` | A `span` per turn with tokens and duration. |
| 13 | Multi-agent | `orchestrator.py` | A planner writes a plan and hands it off to an executor. |
| 14 | Specs | `feature_list.json` | Valid JSON with `features` and a status like `passing`. |
| 15 | Condensation | `condense.py` | Summarize old turns while keeping goals and failures. |
| 16 | Security | `security.py` | Detect and block prompt injection in tool output; log it. |
| 17 | Evals | `evals.py` | A benchmark with a `score`, run in CI. |
| 18 | Architecture | `ARCHITECTURE.md` | A design doc covering context, tools, constraints, verification, memory. |
| 19 | Hardening | `hardening.py` | Timeouts, cleanup and resource limits. |
| 20 | Capstone | `README.md` | Document a harness for your own domain, then publish it. |

## Exact contracts (what the checks actually run)

Levels 4-9, 12, 13, 15-17 and 19 **import your file and call your functions**. Level 14 validates
your JSON. Levels 10, 11, 18 and 20 are documentation levels (a non-trivial notes/design file).

| Lv | File | You must provide | Tested behaviour |
|----|------|------------------|------------------|
| 4 | `context.py` | `trim_history(messages, max_tokens) -> list` | Drops old messages when over budget, keeps the newest, returns input unchanged when under budget |
| 5 | `tools.py` | `calculate(a, b, op) -> dict` | `calculate(15, 23, "*") == {"ok": True, "result": 345}`; bad op and divide-by-zero return `{"ok": False, "error": ...}` |
| 6 | `guardrails.py` | `class LoopDetector(limit=3)` with `seen_loop(action) -> bool` | True on the 3rd identical action in a row; never for varied actions |
| 7 | `verify.py` | `verify(output: str) -> bool` | Rejects empty output and output without `[TASK_COMPLETE]` |
| 8 | `memory.py` | `save_state(path, state)`, `load_state(path)` | Round-trips a dict through disk |
| 9 | `providers.py` | `async complete_with_fallback(providers, messages, model)` | Skips failing providers, returns the first success, raises if all fail |
| 12 | `telemetry.py` | `class Tracer` with `span(turn, model, tokens, started, tools, status)` and `.spans` | Each span is a dict with those keys and a sensible duration |
| 13 | `orchestrator.py` | `make_plan(task) -> list[str]`, `run_plan(plan, executor) -> list` | Plan has 2+ steps; executor is called once per step, in order |
| 14 | `feature_list.json` | `{"features": [...5+ items...]}` | Each item has `id`, `description`, `status` (`failing`/`in_progress`/`passing`) |
| 15 | `condense.py` | `condense(messages) -> list` | Output far shorter than a 42-message input, keeps the first message (goal) and the latest failure |
| 16 | `security.py` | `scan(text) -> list` | Non-empty for "Ignore previous instructions...", empty for benign text |
| 17 | `evals.py` | `score(results: list[bool]) -> float` | Pass fraction; `score([]) == 0` |
| 19 | `hardening.py` | `run_with_timeout(func, seconds)` | Raises `TimeoutError` for a slow function, returns fast results |

Your code runs in a separate Python process (`python -I`, 15 s timeout), so bugs or infinite
loops cannot crash the game.

## Stuck?

Working solutions live in [`examples/reference_harness/`](../examples/reference_harness/). Try first, then peek.
