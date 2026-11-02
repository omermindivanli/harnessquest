"""Unit tests for HarnessQuest core runner and sandbox."""

import pytest
from harnessquest.core.sandbox import ExecutionSandbox
from harnessquest.gamification.xp import GamificationEngine


def test_sandbox_path_validation():
    sandbox = ExecutionSandbox(workspace_root=".")
    assert sandbox._validate_path("AGENTS.md") is not None
    import pytest
    with pytest.raises(PermissionError):
        sandbox._validate_path("../../../etc/passwd")


def test_gamification_engine():
    engine = GamificationEngine()
    stats = engine.evaluate_run(turns=1, total_tokens=1000, duration_seconds=1.2, faults=0)
    assert stats["level"] >= 1
    assert len(stats["new_badges"]) > 0
