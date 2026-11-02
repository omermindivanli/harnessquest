"""Main Engine Runner."""

import time
from typing import Any, Dict, List
import litellm

from harnessquest.core.context import ContextEngine
from harnessquest.core.sandbox import ExecutionSandbox
from harnessquest.gamification.xp import GamificationEngine


class HarnessRunner:
    """Core Execution Engine managing the agent loop, sandbox, and gamification."""

    def __init__(self, model: str = "gpt-4o", max_turns: int = 5, workspace: str = "."):
        self.model = model
        self.max_turns = max_turns
        self.context_engine = ContextEngine(workspace)
        self.sandbox = ExecutionSandbox(workspace)
        self.gamification = GamificationEngine()

    async def run(self, prompt: str, system_prompt: str = "You are an expert software agent.") -> Dict[str, Any]:
        start_time = time.time()
        history: List[Dict[str, str]] = []
        turn = 0
        total_tokens = 0
        faults = 0

        while turn < self.max_turns:
            turn += 1
            messages = self.context_engine.assemble_context(system_prompt, prompt, history)

            try:
                response = await litellm.acompletion(
                    model=self.model,
                    messages=messages,
                    temperature=0.1
                )
            except Exception as e:
                faults += 1
                return {"status": "error", "error": str(e), "turns": turn}

            usage = getattr(response, "usage", None)
            if usage:
                total_tokens += getattr(usage, "total_tokens", 300)
            else:
                total_tokens += 300

            content = response.choices[0].message.content
            history.append({"role": "assistant", "content": content})

            if "[TASK_COMPLETE]" in content:
                duration = time.time() - start_time
                quest_stats = self.gamification.evaluate_run(turn, total_tokens, duration, faults)
                return {
                    "status": "success",
                    "turns": turn,
                    "total_tokens": total_tokens,
                    "duration_seconds": round(duration, 2),
                    "output": content,
                    "gamification": quest_stats
                }

            if "RUN:" in content:
                cmd = content.split("RUN:")[1].split("\n")[0].strip()
                res = self.sandbox.run_command(cmd)
                if not res["success"]:
                    faults += 1
                history.append({"role": "user", "content": f"Tool Execution Result:\n{res}"})
            else:
                history.append({"role": "user", "content": "Please proceed or output [TASK_COMPLETE]."})

        duration = time.time() - start_time
        return {
            "status": "max_turns_exceeded",
            "turns": turn,
            "total_tokens": total_tokens,
            "duration_seconds": round(duration, 2),
            "gamification": self.gamification.evaluate_run(turn, total_tokens, duration, faults + 1)
        }
