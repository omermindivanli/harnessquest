"""Deterministic quest verifiers.

A quest used to pass whenever the LLM printed [TASK_COMPLETE], which verifies nothing.
Each check here inspects real behaviour or real learner artifacts and returns
``(passed, message)``. No network and no LLM are needed.

Levels 1-3 test the built-in harness. Levels 4+ are "build it yourself" quests: the
learner creates files under ``./my_harness/`` (see docs/QUESTS.md) and the check looks
for them and for the key concept inside them.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from harnessquest.core.context import ContextEngine
from harnessquest.core.sandbox import ExecutionSandbox

CheckResult = Tuple[bool, str]


def check_level_2(workspace: str) -> CheckResult:
    """The sandbox must block path escapes and dangerous commands but allow normal ones."""
    with tempfile.TemporaryDirectory() as tmp:
        ws = os.path.join(tmp, "ws")
        os.makedirs(ws)
        sb = ExecutionSandbox(ws)
        try:
            sb.read_file("../../../etc/passwd")
            return False, "Path traversal was NOT blocked."
        except PermissionError:
            pass
        os.makedirs(os.path.join(tmp, "ws_evil"))
        try:
            sb.read_file("../ws_evil/x")
            return False, "Sibling-prefix escape was NOT blocked."
        except PermissionError:
            pass
        if sb.run_command("rm -rf /").get("success") is not False:
            return False, "'rm -rf /' was NOT blocked."
        if not sb.run_command("echo ok")["success"]:
            return False, "A harmless command was wrongly blocked."
    return True, "Sandbox blocks traversal, sibling escapes and dangerous commands, and allows safe ones."


def check_level_3(workspace: str) -> CheckResult:
    """AGENTS.md must exist and be injected into the agent's context."""
    agents = Path(workspace) / "AGENTS.md"
    if not agents.exists():
        return False, "No AGENTS.md in the current directory. Create one (a short map, not an encyclopedia)."
    text = agents.read_text(encoding="utf-8")
    if len(text.strip()) < 40:
        return False, "AGENTS.md is nearly empty. Describe the directory layout."
    if len(text) > 8000:
        return False, "AGENTS.md is over 8000 chars. It should be a map, not a manual."
    msgs = ContextEngine(workspace).assemble_context("sys", "task", [])
    if text.strip()[:40] not in msgs[0]["content"]:
        return False, "AGENTS.md exists but was not injected into the system prompt."
    return True, f"AGENTS.md ({len(text)} chars) is injected into the agent context."


# (level -> (list of candidate paths relative to ./my_harness, keywords of which at least one must appear))
ARTIFACTS: Dict[int, Tuple[List[str], List[str], str]] = {
    4: (["context.py", "summarizer.py"], ["def "], "a summarizer/context trimmer function"),
    5: (["tools.py"], ["def ", "calculate"], "a validated 'calculate' tool"),
    6: (["guardrails.py", "loop_detector.py"], ["loop", "max_"], "loop detection / turn limits"),
    7: (["verify.py", "judge.py"], ["def ", "pass"], "a verification gate"),
    8: (["memory.py", "session.py"], ["json", "def "], "state persistence"),
    9: (["providers.py", "router.py"], ["fallback", "except"], "provider fallback"),
    10: (["ollama_notes.md", "local.py"], ["ollama"], "local model usage"),
    11: (["nim_notes.md", "nim.py"], ["nim", "nvidia"], "NVIDIA NIM usage"),
    12: (["telemetry.py", "tracing.py"], ["span", "tokens", "duration"], "per-turn tracing"),
    13: (["orchestrator.py", "multi_agent.py"], ["plan", "handoff"], "planner/executor handoff"),
    14: (["feature_list.json"], ["passing", "features"], "spec-driven feature list"),
    15: (["condense.py", "compaction.py"], ["def ", "summar"], "context condensation"),
    16: (["security.py", "injection.py"], ["inject", "block"], "prompt-injection defense"),
    17: (["evals.py", "benchmark.py"], ["def ", "score"], "an eval/benchmark suite"),
    18: (["ARCHITECTURE.md", "AGENTS.md"], ["#"], "an architecture document"),
    19: (["hardening.py", "stress_test.py"], ["def ", "timeout", "cleanup"], "production hardening"),
    20: (["README.md", "AGENTS.md"], ["harness"], "a documented capstone harness"),
}


def _artifact_check(level: int) -> Callable[[str], CheckResult]:
    files, keywords, what = ARTIFACTS[level]

    def check(workspace: str) -> CheckResult:
        base = Path(workspace) / "my_harness"
        if not base.is_dir():
            return False, f"Create ./my_harness/ and add {what} (see docs/QUESTS.md, Level {level})."
        for name in files:
            p = base / name
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="ignore").lower()
                if len(text.strip()) < 30:
                    return False, f"{p.name} is almost empty. Implement {what}."
                if name.endswith(".json"):
                    try:
                        json.loads(text)
                    except ValueError:
                        return False, f"{p.name} is not valid JSON."
                if not any(k.lower() in text for k in keywords):
                    return False, f"{p.name} found but it doesn't look like {what} (expected one of: {', '.join(keywords)})."
                return True, f"Found {p.name}: {what}."
        return False, f"Add one of {', '.join('my_harness/' + f for f in files)} implementing {what}."

    return check


CHECKS: Dict[int, Callable[[str], CheckResult]] = {2: check_level_2, 3: check_level_3}
for _lvl in ARTIFACTS:
    CHECKS[_lvl] = _artifact_check(_lvl)


def run_check(level: int, workspace: str = ".") -> CheckResult:
    """Run the deterministic verifier for a level (levels with no check pass on agent success)."""
    check = CHECKS.get(level)
    if check is None:
        return True, "No extra check for this level."
    return check(workspace)
