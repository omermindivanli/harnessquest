"""Tests for deterministic quest checks, the offline mock provider and the agent loop."""

import asyncio

from harnessquest.core.config import validate_provider_config
from harnessquest.core.runner import HarnessRunner
from harnessquest.gamification.checks import ARTIFACTS, run_check


def test_level2_check_passes():
    ok, msg = run_check(2)
    assert ok, msg


def test_level3_requires_agents_md(tmp_path):
    ok, _ = run_check(3, str(tmp_path))
    assert not ok
    (tmp_path / "AGENTS.md").write_text("# Map\n- src/: code lives here\n- tests/: tests live here\n")
    ok, msg = run_check(3, str(tmp_path))
    assert ok, msg


def test_artifact_checks_fail_then_pass(tmp_path):
    ok, _ = run_check(5, str(tmp_path))
    assert not ok
    base = tmp_path / "my_harness"
    base.mkdir()
    (base / "tools.py").write_text("def calculate(a, b, op):\n    return a + b  # wrong: not structured\n")
    ok, msg = run_check(5, str(tmp_path))
    assert not ok and "calculate" in msg  # behaviour is tested, not just keywords
    (base / "tools.py").write_text(
        "def calculate(a, b, op):\n"
        "    if op not in '+-*/':\n        return {'ok': False, 'error': 'bad op'}\n"
        "    if op == '/' and b == 0:\n        return {'ok': False, 'error': 'div0'}\n"
        "    return {'ok': True, 'result': {'+': a+b, '-': a-b, '*': a*b, '/': a/b if b else 0}[op]}\n"
    )
    ok, msg = run_check(5, str(tmp_path))
    assert ok, msg


def test_every_artifact_level_has_a_check():
    for level in ARTIFACTS:
        ok, msg = run_check(level, "/nonexistent-dir")
        assert not ok and "my_harness" in msg


def test_bad_json_spec_rejected(tmp_path):
    base = tmp_path / "my_harness"
    base.mkdir()
    (base / "feature_list.json").write_text("{ this is not json, features passing }")
    ok, msg = run_check(14, str(tmp_path))
    assert not ok and "JSON" in msg


def test_mock_provider_valid():
    assert validate_provider_config("mock")[0]


def test_runner_with_mock_provider_completes(tmp_path):
    runner = HarnessRunner(model="mock", provider="mock", workspace=str(tmp_path), max_turns=5)
    result = asyncio.run(runner.run("List the files"))
    assert result["status"] == "success"
    assert result["turns"] == 2
    assert result["gamification"]["earned_xp"] > 0


def test_runner_detects_command_loop(tmp_path):
    class Looper:
        async def complete(self, **kw):
            from harnessquest.core.providers import _MockResponse
            return _MockResponse("RUN: echo hi")

    runner = HarnessRunner(model="m", provider="mock", workspace=str(tmp_path),
                           max_turns=10, provider_instance=Looper())
    result = asyncio.run(runner.run("x"))
    assert result["status"] == "loop_detected"
    assert result["turns"] == 3


def test_runner_provider_error_has_stable_shape(tmp_path):
    class Boom:
        async def complete(self, **kw):
            raise RuntimeError("no network")

    runner = HarnessRunner(model="m", provider="mock", workspace=str(tmp_path), provider_instance=Boom())
    result = asyncio.run(runner.run("x"))
    assert result["status"] == "error"
    assert "no network" in result["output"]
    assert result["gamification"] is None
