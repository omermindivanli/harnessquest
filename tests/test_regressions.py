"""Regression tests for bugs found in the v1.1.0 review."""

import pytest

from harnessquest.core.context import ContextEngine
from harnessquest.core.sandbox import ExecutionSandbox
from harnessquest.gamification.levels import ProgressionEngine, QuestStatus


def test_sandbox_sibling_prefix_escape_blocked(tmp_path):
    ws = tmp_path / "ws"
    evil = tmp_path / "ws_evil"
    ws.mkdir()
    evil.mkdir()
    (evil / "secret.txt").write_text("SECRET")
    sb = ExecutionSandbox(str(ws))
    with pytest.raises(PermissionError):
        sb.read_file("../ws_evil/secret.txt")


def test_sandbox_write_bare_filename(tmp_path):
    sb = ExecutionSandbox(str(tmp_path))
    assert "Successfully" in sb.write_file("x.txt", "hi")


def test_sandbox_allows_harmless_words(tmp_path):
    sb = ExecutionSandbox(str(tmp_path))
    assert sb.run_command("echo add address")["success"]


@pytest.mark.parametrize("cmd", ["rm -rf /", "rm -rf ~", "sudo ls", "mkfs.ext4 /dev/x", "shutdown now"])
def test_sandbox_blocks_dangerous(tmp_path, cmd):
    res = ExecutionSandbox(str(tmp_path)).run_command(cmd)
    assert not res["success"] and "Security Violation" in res["error"]


def test_context_orders_task_before_history(tmp_path):
    msgs = ContextEngine(str(tmp_path)).assemble_context(
        "sys", "do the task", [{"role": "assistant", "content": "a"}]
    )
    assert [m["role"] for m in msgs] == ["system", "user", "assistant"]


def test_progression_flow(tmp_path):
    eng = ProgressionEngine(str(tmp_path / "p.json"))
    assert eng.get_quest_status(1) == QuestStatus.IN_PROGRESS
    assert eng.start_quest(1) is True
    assert eng.get_quest_status(2) == QuestStatus.LOCKED
    assert eng.complete_quest(1)["success"]
    assert eng.get_quest_status(2) != QuestStatus.LOCKED
    # survives a JSON reload (string keys)
    eng2 = ProgressionEngine(str(tmp_path / "p.json"))
    assert eng2.start_quest(2) is True
    # skipping ahead must not mark skipped levels complete
    assert eng2.get_quest_status(5) == QuestStatus.LOCKED
