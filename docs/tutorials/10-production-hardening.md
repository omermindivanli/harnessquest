# Tutorial 10: Production Hardening (Levels 16, 19)

- **Sandbox honestly.** HarnessQuest's sandbox is a teaching tool: path checks plus a command blocklist with `shell=True`. A blocklist is not isolation. For real use run commands in a container or VM with no network and no secrets.
- **Prompt injection.** Treat all tool output and file content as untrusted data, never as instructions. Detect phrases like "ignore previous instructions", strip or flag them, and log the event.
- **Timeouts and quotas** on every call; **cleanup** of temp files and sessions.
- **Compaction.** Summarize old turns but keep goals and failures.
- **CI.** Run offline tests on every PR (`.github/workflows/quest_eval.yml`).

**Exercise** (`my_harness/security.py`): write `scan(text) -> list[str]` returning detected injection phrases, and a `block()` that refuses to pass flagged text to the model.
