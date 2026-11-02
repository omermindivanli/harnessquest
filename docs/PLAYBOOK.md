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

## Reality check

Levels 4-20 verify that you built something relevant, not that it is perfect. If you
want a stricter signal, point your own tests at `my_harness/` and run them in CI.
