"""Every reference solution must pass its own quest check; broken code must fail it."""

import shutil
from pathlib import Path

import pytest

from harnessquest.gamification.checks import run_check

REFERENCE = Path(__file__).resolve().parent.parent / "examples" / "reference_harness"
ALL_LEVELS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]


@pytest.fixture
def workspace(tmp_path):
    shutil.copytree(REFERENCE, tmp_path / "my_harness")
    return tmp_path


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_reference_solution_passes(workspace, level):
    ok, msg = run_check(level, str(workspace))
    assert ok, f"level {level}: {msg}"


@pytest.mark.parametrize("level,filename", [
    (4, "context.py"), (5, "tools.py"), (6, "guardrails.py"), (7, "verify.py"), (8, "memory.py"),
    (9, "providers.py"), (12, "telemetry.py"), (13, "orchestrator.py"), (15, "condense.py"),
    (16, "security.py"), (17, "evals.py"), (19, "hardening.py"),
])
def test_stub_code_fails(workspace, level, filename):
    (workspace / "my_harness" / filename).write_text("# TODO: implement me later\n")
    ok, msg = run_check(level, str(workspace))
    assert not ok, f"level {level} should fail for a stub"


def test_syntax_error_reported_not_crashed(workspace):
    (workspace / "my_harness" / "tools.py").write_text("def calculate(:\n")
    ok, msg = run_check(5, str(workspace))
    assert not ok and msg


def test_infinite_loop_is_timed_out(workspace):
    (workspace / "my_harness" / "verify.py").write_text("while True:\n    pass\n")
    ok, msg = run_check(7, str(workspace))
    assert not ok and "timed out" in msg
