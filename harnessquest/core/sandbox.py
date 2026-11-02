"""Isolated execution boundary for tool actions.

Defence in depth (a teaching sandbox, NOT a security boundary against a determined attacker;
for untrusted code run the harness in a container or VM with no network and no secrets):

1. Blocklist of obviously destructive commands (clear error message for learners).
2. Allowlist of command names. Anything else is refused.
3. No shell: the command is parsed with shlex and executed directly, so pipes, redirects,
   `&&`, `$(...)` and backticks have no special meaning.
4. Every path-like argument must resolve (symlinks included) inside the workspace.
5. Scrubbed environment (no API keys leak to child processes), stdin closed.
6. Wall-clock timeout plus CPU-time and file-size limits on POSIX.
"""

import os
import re
import shlex
import subprocess
from typing import Any, Dict, Iterable, Optional

try:  # POSIX only
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore

DEFAULT_ALLOWED_COMMANDS = frozenset({
    "ls", "cat", "echo", "pwd", "head", "tail", "wc", "grep", "find", "sort", "uniq",
    "stat", "file", "date", "whoami", "tree", "basename", "dirname",
})

# Arguments that let otherwise harmless commands execute or destroy things.
_DENIED_ARGS = frozenset({
    "-exec", "-execdir", "-ok", "-okdir", "-delete", "-fprint", "-fprintf", "-fls",
})

_FORBIDDEN_PATTERNS = [
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+(/|~|\$HOME)",
    r"\bmkfs\b", r"\bdd\s+if=", r"\bshutdown\b", r"\breboot\b", r"\bsudo\b",
    r":\(\)\s*\{.*\};\s*:",
]

_MAX_OUTPUT = 4000


def _limit_resources() -> None:  # pragma: no cover - runs in the child process
    if resource is None:
        return
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
        resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
    except (ValueError, OSError):
        pass


class ExecutionSandbox:
    """Execution layer with strict permission enforcement."""

    def __init__(
        self,
        workspace_root: str = ".",
        allowed_commands: Optional[Iterable[str]] = None,
        timeout: int = 15,
    ):
        # realpath so symlinks (e.g. macOS /tmp -> /private/tmp) cannot confuse the checks
        self.workspace_root = os.path.realpath(os.path.abspath(workspace_root))
        self.allowed_commands = frozenset(allowed_commands) if allowed_commands is not None else DEFAULT_ALLOWED_COMMANDS
        self.timeout = timeout

    # ------------------------------------------------------------------ paths
    def _inside(self, resolved: str) -> bool:
        try:
            return os.path.commonpath([self.workspace_root, resolved]) == self.workspace_root
        except ValueError:  # different drives on Windows
            return False

    def _validate_path(self, relative_path: str) -> str:
        target = os.path.realpath(os.path.join(self.workspace_root, relative_path))
        if not self._inside(target):
            raise PermissionError(f"Access Denied: Path '{relative_path}' escapes sandbox root.")
        return target

    def read_file(self, file_path: str) -> str:
        safe_path = self._validate_path(file_path)
        if not os.path.exists(safe_path):
            return f"Error: File '{file_path}' does not exist."
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, file_path: str, content: str) -> str:
        safe_path = self._validate_path(file_path)
        os.makedirs(os.path.dirname(safe_path) or ".", exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to {file_path}."

    # --------------------------------------------------------------- commands
    def _check_argument(self, arg: str) -> Optional[str]:
        """Return an error message if the argument points outside the workspace."""
        candidates = [arg]
        if arg.startswith("-") and "=" in arg:
            candidates.append(arg.split("=", 1)[1])
        for cand in candidates:
            if cand.startswith("~"):
                return f"Path '{cand}' is not allowed (home directory)."
            if cand.startswith("-"):
                continue  # a flag, not a path
            # Resolve EVERY other argument (symlinks included), even without a "/":
            # `cat link.txt` must not follow a symlink out of the workspace.
            full = cand if os.path.isabs(cand) else os.path.join(self.workspace_root, cand)
            if not self._inside(os.path.realpath(full)):
                return f"Path '{cand}' escapes the sandbox workspace."
        return None

    def run_command(self, command: str) -> Dict[str, Any]:
        """Execute one allowlisted command inside the workspace (no shell)."""
        if any(re.search(p, command) for p in _FORBIDDEN_PATTERNS):
            return {"success": False, "error": "Security Violation: Blocked dangerous command."}

        try:
            lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
            lexer.whitespace_split = True
            argv = list(lexer)
        except ValueError as e:
            return {"success": False, "error": f"Could not parse command: {e}"}
        if not argv:
            return {"success": False, "error": "Empty command."}

        # punctuation_chars splits unquoted ; | & < > ( ) into their own tokens
        if any(tok and all(c in "();<>|&" for c in tok) for tok in argv):
            return {
                "success": False,
                "error": "Shell operators (|, &&, ;, >, <) are not supported. Run one simple command per RUN: line.",
            }

        name = argv[0]
        if "/" in name or name not in self.allowed_commands:
            return {
                "success": False,
                "error": f"Command '{name}' is not allowed. Allowed: {', '.join(sorted(self.allowed_commands))}.",
            }

        for arg in argv[1:]:
            if arg in _DENIED_ARGS:
                return {"success": False, "error": f"Argument '{arg}' is not allowed."}
            problem = self._check_argument(arg)
            if problem:
                return {"success": False, "error": f"Security Violation: {problem}"}

        env = {
            "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
            "HOME": self.workspace_root,
            "LANG": "C.UTF-8",
        }
        try:
            result = subprocess.run(
                argv,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=self.timeout,
                env=env,
                stdin=subprocess.DEVNULL,
                preexec_fn=_limit_resources if resource is not None and os.name == "posix" else None,
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Execution Timed Out ({self.timeout}s limit)."}
        except FileNotFoundError:
            return {"success": False, "error": f"Command '{name}' not found on this system."}
        except OSError as e:
            return {"success": False, "error": f"Could not execute command: {e}"}

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip()[:_MAX_OUTPUT],
            "stderr": result.stderr.strip()[:_MAX_OUTPUT],
            "exit_code": result.returncode,
        }
