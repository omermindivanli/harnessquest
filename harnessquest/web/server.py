"""Local web UI server: `harnessquest-play`.

Binds to 127.0.0.1 only. Uses only the standard library plus the harnessquest package.
Your progress and files live in the folder you launch it from.
"""

import argparse
import asyncio
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from harnessquest.core.config import get_settings
from harnessquest.core.sandbox import ExecutionSandbox
from harnessquest.gamification.checks import run_check
from harnessquest.gamification.levels import QUESTS, QuestStatus, get_progression_engine
from harnessquest.web.content import CONTRACTS, PAGE, STARTERS

REFERENCE_DIR = Path(__file__).resolve().parents[2] / "examples" / "reference_harness"
LOCK = threading.Lock()
MAX_BODY = 200_000


def workspace() -> Path:
    return Path.cwd()


def _file_target(level: int) -> Optional[Tuple[str, Path, str]]:
    """(filename, absolute path, display folder) the learner edits for a level, or None."""
    if level not in STARTERS:
        return None
    name = STARTERS[level][0]
    if level == 3:
        return name, workspace() / name, ""
    return name, workspace() / "my_harness" / name, "my_harness/"


def api_state() -> Dict[str, Any]:
    eng = get_progression_engine()
    data = eng.player_data
    xp = data.get("total_xp", 0)
    return {
        "level": xp // 500 + 1,
        "total_xp": xp,
        "completed": len(data.get("completed_quests", [])),
        "badges": data.get("unlocked_badges", []),
        "quests": [
            {
                "level": n, "title": q.title, "difficulty": q.difficulty, "xp_reward": q.xp_reward,
                "status": eng.get_quest_status(n).value,
            }
            for n, q in sorted(QUESTS.items())
        ],
    }


def api_quest(level: int) -> Dict[str, Any]:
    q = QUESTS[level]
    out: Dict[str, Any] = {
        "level": level, "title": q.title, "concept": q.concept, "theory": q.theory.replace("\n", " "),
        "objective": q.objective, "difficulty": q.difficulty, "xp_reward": q.xp_reward, "hints": q.hints,
        "status": get_progression_engine().get_quest_status(level).value,
        "contract": CONTRACTS.get(level, ""), "file": None,
    }
    target = _file_target(level)
    if target:
        name, path, folder = target
        out.update(file=name, folder=folder, content=path.read_text(encoding="utf-8") if path.exists() else STARTERS[level][1])
    if level == 1:
        from harnessquest.core.providers import PROVIDER_REGISTRY
        out["providers"] = ["mock"] + [p for p in PROVIDER_REGISTRY if p != "mock"]
    return out


def api_save(body: Dict[str, Any]) -> Dict[str, Any]:
    level = int(body.get("level", 0))
    target = _file_target(level)
    content = body.get("content")
    if not target or not isinstance(content, str) or len(content) > 100_000:
        return {"ok": False, "message": "Nothing to save for this level."}
    _, path, _ = target
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"ok": True}


def api_check(body: Dict[str, Any]) -> Dict[str, Any]:
    level = int(body.get("level", 0))
    if level not in QUESTS:
        return {"ok": False, "message": "Unknown quest."}
    eng = get_progression_engine()
    status = eng.get_quest_status(level)
    if status == QuestStatus.LOCKED:
        need = ", ".join(map(str, QUESTS[level].prerequisites))
        return {"ok": False, "message": f"Locked. Complete level(s) {need} first."}
    eng.start_quest(level)

    if level == 1:
        ok, msg = _run_level_one(str(body.get("provider") or "mock"))
    else:
        ok, msg = run_check(level, str(workspace()))
    result: Dict[str, Any] = {"ok": ok, "message": msg}
    if ok and status != QuestStatus.COMPLETED:
        done = eng.complete_quest(level)
        if done.get("success"):
            result["reward"] = {"xp": done["xp_earned"], "badge": f"{done['badge']['icon']} {done['badge']['title']}"}
    elif ok:
        result["message"] += " (already completed, no extra XP)"
    return result


def _run_level_one(provider: str) -> Tuple[bool, str]:
    from harnessquest.core.config import validate_provider_config, get_provider_help
    from harnessquest.core.providers import PROVIDER_REGISTRY
    from harnessquest.core.runner import HarnessRunner

    if provider not in PROVIDER_REGISTRY:
        return False, f"Unknown provider {provider!r}."
    valid, msg = validate_provider_config(provider)
    if not valid:
        return False, f"{msg}\n{get_provider_help(provider)}\nTip: choose 'mock' to play offline."
    model = "mock" if provider == "mock" else get_settings().default_model
    runner = HarnessRunner(model=model, max_turns=15, workspace=str(workspace()), provider=provider)
    result = asyncio.run(runner.run("List the files in the current directory and output [TASK_COMPLETE]"))
    summary = f"status={result['status']}, turns={result['turns']}, tokens={result.get('total_tokens', 0)}\n{result.get('output', '')[:400]}"
    return result["status"] == "success", summary


def api_sandbox(body: Dict[str, Any]) -> Dict[str, Any]:
    return ExecutionSandbox(str(workspace())).run_command(str(body.get("command", "")))


def api_reference(level: int) -> Dict[str, Any]:
    target = _file_target(level)
    if not target or level == 3:
        return {"error": "No reference solution for this level."}
    path = REFERENCE_DIR / target[0]
    if not path.exists():
        return {"error": "Reference solutions are only included when you clone the repository."}
    return {"content": path.read_text(encoding="utf-8")}


class Handler(BaseHTTPRequestHandler):
    server_version = "HarnessQuest"

    def log_message(self, *args):  # keep the terminal clean
        pass

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def _send(self, code: int, payload: Any, ctype: str = "application/json") -> None:
        raw = payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {"error": "forbidden host"})
        path = self.path.split("?")[0]
        try:
            if path in ("/", "/index.html"):
                return self._send(200, PAGE, "text/html")
            with LOCK:
                if path == "/api/state":
                    return self._send(200, api_state())
                if path.startswith("/api/quest/"):
                    level = int(path.rsplit("/", 1)[1])
                    if level in QUESTS:
                        return self._send(200, api_quest(level))
                if path.startswith("/api/reference/"):
                    return self._send(200, api_reference(int(path.rsplit("/", 1)[1])))
        except Exception as e:  # never kill the server on a bad request
            return self._send(500, {"error": f"{type(e).__name__}: {e}"})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        # Custom header forces a CORS preflight, so other websites cannot drive this local server.
        if not self._host_ok() or self.headers.get("X-HQ") != "1":
            return self._send(403, {"error": "forbidden"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                return self._send(413, {"error": "too large"})
            body = json.loads(self.rfile.read(length) or b"{}")
            routes = {"/api/save": api_save, "/api/check": api_check, "/api/sandbox": api_sandbox}
            fn = routes.get(self.path)
            if fn is None:
                return self._send(404, {"error": "not found"})
            with LOCK:
                return self._send(200, fn(body))
        except Exception as e:
            return self._send(500, {"ok": False, "message": f"Server error: {type(e).__name__}: {e}"})


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="HarnessQuest web UI")
    parser.add_argument("--port", type=int, default=7777)
    parser.add_argument("--dir", default=".", help="folder to play in (progress and my_harness/ live here)")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)

    play_dir = Path(args.dir).expanduser()
    play_dir.mkdir(parents=True, exist_ok=True)  # create the play folder if it doesn't exist yet
    os.chdir(play_dir)
    server = None
    for port in range(args.port, args.port + 20):  # first free port at or after the requested one
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            print(f"Port {port} is busy, trying {port + 1}...")
    if server is None:
        raise SystemExit(f"No free port found from {args.port} to {args.port + 19}. Use --port to pick another.")
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"HarnessQuest is running at {url}")
    print(f"Playing in: {Path.cwd()}  (your code goes in ./my_harness/)   Ctrl+C to stop")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBye! Your progress is saved.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
