"""Context Manager for HarnessQuest."""

from pathlib import Path
from typing import Dict, List


class ContextEngine:
    """Manages repository context maps and token-efficient memory injection."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def load_repo_map(self) -> str:
        """Loads AGENTS.md or generates a minimalist fallback repository map."""
        agents_map = self.root_dir / "AGENTS.md"
        if agents_map.exists():
            return agents_map.read_text(encoding="utf-8")
        
        tree = []
        for path in sorted(self.root_dir.rglob("*")):
            if any(part.startswith(".") or part in ["__pycache__", "venv"] for part in path.parts):
                continue
            depth = len(path.relative_to(self.root_dir).parts)
            spacer = "  " * (depth - 1)
            tree.append(f"{spacer}├── {path.name}")
            if len(tree) > 50:
                tree.append(f"{spacer}└── ... [truncated]")
                break
        return "Repository Tree Map:\n" + "\n".join(tree)

    def assemble_context(self, system_prompt: str, user_prompt: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Assembles systemic context with active injection guardrails."""
        repo_map = self.load_repo_map()
        
        combined_system = (
            f"{system_prompt}\n\n"
            f"=== REPOSITORY HARNESS CONTEXT ===\n"
            f"{repo_map}\n"
            f"===================================\n"
            f"Rules:\n"
            f"1. You must operate strictly within the provided harness boundary.\n"
            f"2. Signal completion by including '[TASK_COMPLETE]' in your message.\n"
        )

        messages = [{"role": "system", "content": combined_system}]
        # Task first, then the running conversation, so the model sees turns in order.
        messages.append({"role": "user", "content": user_prompt})
        messages.extend(history)
        return messages
