"""End-to-end tests for the local web UI: real HTTP server on a random port."""

import json
import shutil
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from harnessquest.gamification import levels
from harnessquest.web import server

REFERENCE = Path(__file__).resolve().parent.parent / "examples" / "reference_harness"


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(levels, "_progression_engine", None)  # fresh progress in tmp dir
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"

    def call(path, body=None, headers=None):
        hdrs = {"Content-Type": "application/json", "X-HQ": "1", **(headers or {})}
        req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(),
                                     headers=hdrs if body is not None else {}, method="POST" if body is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode()
                return r.status, (json.loads(raw) if r.headers["Content-Type"].startswith("application/json") else raw)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode() or "{}")

    yield call, tmp_path
    httpd.shutdown()
    monkeypatch.setattr(levels, "_progression_engine", None)


def test_page_and_state(app):
    call, _ = app
    status, html = call("/")
    assert status == 200 and "HarnessQuest" in html
    status, st = call("/api/state")
    assert st["total_xp"] == 0 and len(st["quests"]) == 20
    assert st["quests"][0]["status"] == "in_progress" and st["quests"][1]["status"] == "locked"


def test_full_play_flow(app):
    call, tmp = app
    # locked quest cannot be passed
    assert call("/api/check", {"level": 2})[1]["ok"] is False
    # level 1 with the offline mock agent
    ok = call("/api/check", {"level": 1, "provider": "mock"})[1]
    assert ok["ok"] and ok["reward"]["xp"] == 100
    # level 2 now unlocked
    assert call("/api/check", {"level": 2})[1]["ok"]
    # level 3: stub fails, real AGENTS.md passes
    assert not call("/api/check", {"level": 3})[1]["ok"]
    call("/api/save", {"level": 3, "content": "# Map\n- src/: code\n- tests/: tests for the code\n"})
    assert call("/api/check", {"level": 3})[1]["ok"]
    # level 5 needs level 2 (done): starter fails, reference passes, no double XP
    q = call("/api/quest/5")[1]
    assert "NotImplementedError" in q["content"]
    assert not call("/api/check", {"level": 5})[1]["ok"]
    call("/api/save", {"level": 5, "content": (REFERENCE / "tools.py").read_text()})
    res = call("/api/check", {"level": 5})[1]
    assert res["ok"] and res["reward"]["xp"] == QUEST_XP[5]
    again = call("/api/check", {"level": 5})[1]
    assert again["ok"] and "reward" not in again
    st = call("/api/state")[1]
    assert st["completed"] == 4 and st["total_xp"] == 100 + QUEST_XP[2] + QUEST_XP[3] + QUEST_XP[5]
    assert (tmp / "my_harness" / "tools.py").exists()


QUEST_XP = {n: q.xp_reward for n, q in levels.QUESTS.items()}


def test_sandbox_playground(app):
    call, _ = app
    assert call("/api/sandbox", {"command": "echo hi"})[1]["stdout"] == "hi"
    assert "Security Violation" in call("/api/sandbox", {"command": "cat /etc/passwd"})[1]["error"]


def test_reference_endpoint(app):
    call, _ = app
    assert "def calculate" in call("/api/reference/5")[1]["content"]
    assert "error" in call("/api/reference/3")[1]


def test_post_requires_custom_header(app):
    call, _ = app
    status, _ = call("/api/sandbox", {"command": "ls"}, headers={"X-HQ": "0"})
    assert status == 403


def test_bad_requests_do_not_kill_server(app):
    call, _ = app
    assert call("/api/quest/999")[0] == 404
    assert call("/api/quest/abc")[0] == 500
    assert call("/api/state")[0] == 200  # still alive
