# Contributing to HarnessQuest

Thanks for helping! Good first contributions: a new provider, a new quest check, a tutorial, or a bug fix.

## Setup

```bash
git clone https://github.com/omermindivanli/harnessquest.git
cd harnessquest
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Tests run offline (no API key needed). Use `--provider mock` to try the CLI without a key.

## Guidelines

- Add a test for every bug fix or feature (`tests/`).
- Keep the sandbox strict: any change to `core/sandbox.py` needs tests for both blocked and allowed cases.
- New quest levels: add the quest to `gamification/levels.py`, a check to `gamification/checks.py`, and a row to `docs/PLAYBOOK.md`.
- Never commit `.env`, API keys, or progress files (`.harnessquest_*.json`).

## Pull requests

Describe what changed and why, and confirm `pytest` passes.
