"""Isolated execution boundary for tool actions."""

import os
import re
import subprocess
from typing import Any, Dict


class ExecutionSandbox:
    """Secure execution layer with strict permission enforcement."""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)

    def _validate_path(self, relative_path: str) -> str:
        target_path = os.path.abspath(os.path.join(self.workspace_root, relative_path))
        # commonpath avoids the prefix bug where /ws_evil passes a startswith("/ws") check
        if os.path.commonpath([self.workspace_root, target_path]) != self.workspace_root:
            raise PermissionError(f"Access Denied: Path '{relative_path}' escapes sandbox root.")
        return target_path

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

    def run_command(self, command: str) -> Dict[str, Any]:
        """Executes a command safely inside the sandbox."""
        # Word-boundary patterns: the old substring check blocked harmless text like "add" or "address".
        forbidden = [
            r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+(/|~|\$HOME)",
            r"\bmkfs\b", r"\bdd\s+if=", r"\bshutdown\b", r"\breboot\b", r"\bsudo\b",
            r":\(\)\s*\{.*\};\s*:",
        ]
        if any(re.search(p, command) for p in forbidden):
            return {"success": False, "error": "Security Violation: Blocked dangerous command."}

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution Timed Out (15s limit)."}
