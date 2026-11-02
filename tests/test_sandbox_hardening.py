"""Tests for the hardened sandbox (allowlist, no shell, path arguments, env scrubbing)."""

import os

import pytest

from harnessquest.core.sandbox import ExecutionSandbox


@pytest.fixture
def sb(tmp_path):
    (tmp_path / "hello.txt").write_text("hello world\n")
    return ExecutionSandbox(str(tmp_path))


def test_allowed_commands_work(sb):
    assert sb.run_command("ls")["stdout"] == "hello.txt"
    assert sb.run_command("cat hello.txt")["stdout"] == "hello world"
    assert sb.run_command("echo 'quoted arg'")["stdout"] == "quoted arg"


@pytest.mark.parametrize("cmd", ["python3 -c 'print(1)'", "curl http://example.com", "bash -c ls", "/bin/ls", "git log"])
def test_non_allowlisted_commands_refused(sb, cmd):
    res = sb.run_command(cmd)
    assert not res["success"] and "not allowed" in res["error"]


@pytest.mark.parametrize("cmd", ["ls | head", "echo hi > out.txt", "ls && ls", "ls; ls"])
def test_shell_operators_refused(sb, cmd):
    res = sb.run_command(cmd)
    assert not res["success"] and "operators" in res["error"]


def test_no_command_substitution(sb):
    res = sb.run_command("echo $(whoami)")
    assert not res["success"]  # parentheses are refused, never executed
    assert sb.run_command("echo 'a|b;c'")["stdout"] == "a|b;c"  # quoted punctuation is just text


@pytest.mark.parametrize("cmd", ["cat /etc/passwd", "ls ..", "cat ../../etc/passwd", "ls ~", "grep --file=/etc/passwd x"])
def test_path_arguments_cannot_escape(sb, cmd):
    res = sb.run_command(cmd)
    assert not res["success"] and "Security Violation" in res["error"]


def test_symlink_escape_blocked(sb, tmp_path):
    outside = tmp_path.parent / "outside_secret.txt"
    outside.write_text("secret")
    os.symlink(str(outside), str(tmp_path / "link.txt"))
    res = sb.run_command("cat link.txt")
    assert not res["success"] and "Security Violation" in res["error"]
    with pytest.raises(PermissionError):
        sb.read_file("link.txt")


def test_find_exec_and_delete_refused(sb):
    assert not sb.run_command("find . -exec ls {} ;")["success"]
    assert not sb.run_command("find . -delete")["success"]


def test_environment_is_scrubbed(sb, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")
    sb2 = ExecutionSandbox(sb.workspace_root, allowed_commands={"env"} | {"echo"})
    out = sb2.run_command("env")["stdout"]
    assert "sk-secret" not in out and "OPENAI_API_KEY" not in out


def test_unparseable_and_empty(sb):
    assert not sb.run_command("echo 'unterminated")["success"]
    assert not sb.run_command("   ")["success"]


def test_custom_allowlist(tmp_path):
    sb = ExecutionSandbox(str(tmp_path), allowed_commands={"echo"})
    assert sb.run_command("echo ok")["success"]
    assert not sb.run_command("ls")["success"]
