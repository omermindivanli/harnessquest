"""Main Engine Runner.

Uses the provider abstraction layer for multi-provider LLM support.
"""

import time
from typing import Any, Dict, List, Optional

from harnessquest.core.config import get_settings, validate_provider_config
from harnessquest.core.providers import get_provider, LLMProvider
from harnessquest.core.context import ContextEngine
from harnessquest.core.sandbox import ExecutionSandbox
from harnessquest.gamification.xp import GamificationEngine


class HarnessRunner:
    """Core Execution Engine managing the agent loop, sandbox, and gamification."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_turns: int = 10,
        workspace: str = ".",
        provider: Optional[str] = None,
        provider_instance: Optional[LLMProvider] = None,
    ):
        self.model = model
        self.max_turns = max_turns
        self.context_engine = ContextEngine(workspace)
        self.sandbox = ExecutionSandbox(workspace)
        self.gamification = GamificationEngine()
        
        # Provider setup
        settings = get_settings()
        self.provider_name = provider or settings.default_provider
        self.provider: LLMProvider = provider_instance or get_provider(self.provider_name, settings)
        
        # Validate provider config
        valid, msg = validate_provider_config(self.provider_name)
        if not valid:
            # Don't fail here - let the actual call fail with a clear error
            pass

    async def run(
        self,
        prompt: str,
        system_prompt: str = "You are an expert software agent.",
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Run the agent loop with the configured provider."""
        settings = get_settings()
        temp = temperature if temperature is not None else settings.default_temperature
        
        start_time = time.time()
        history: List[Dict[str, str]] = []
        turn = 0
        total_tokens = 0
        faults = 0
        recent_cmds: List[str] = []

        while turn < self.max_turns:
            turn += 1
            messages = self.context_engine.assemble_context(system_prompt, prompt, history)

            try:
                response = await self.provider.complete(
                    messages=messages,
                    model=self.model,
                    temperature=temp,
                )
            except Exception as e:
                faults += 1
                duration = time.time() - start_time
                return {
                    "status": "error",
                    "error": str(e),
                    "output": f"Provider error: {e}",
                    "turns": turn,
                    "total_tokens": total_tokens,
                    "duration_seconds": round(duration, 2),
                    "gamification": None,
                    "provider": self.provider_name,
                    "model": self.model,
                }

            usage = getattr(response, "usage", None)
            if usage:
                total_tokens += getattr(usage, "total_tokens", 300)
            else:
                total_tokens += 300

            content = response.choices[0].message.content or ""
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
                    "gamification": quest_stats,
                    "provider": self.provider_name,
                    "model": self.model,
                }

            cmds = [ln.split("RUN:", 1)[1].strip() for ln in content.splitlines() if ln.strip().startswith("RUN:")]
            if cmds:
                results = []
                for cmd in cmds[:3]:  # cap tool calls per turn
                    recent_cmds.append(cmd)
                    if recent_cmds[-3:] == [cmd] * 3:
                        duration = time.time() - start_time
                        return {
                            "status": "loop_detected",
                            "output": f"Loop detected: '{cmd}' repeated 3 times in a row.",
                            "turns": turn,
                            "total_tokens": total_tokens,
                            "duration_seconds": round(duration, 2),
                            "gamification": self.gamification.evaluate_run(turn, total_tokens, duration, faults + 1),
                            "provider": self.provider_name,
                            "model": self.model,
                        }
                    res = self.sandbox.run_command(cmd)
                    if not res["success"]:
                        faults += 1
                    results.append(f"$ {cmd}\n{res}")
                history.append({"role": "user", "content": "Tool Execution Result:\n" + "\n\n".join(results)})
            else:
                history.append({"role": "user", "content": "Please proceed or output [TASK_COMPLETE]."})

        duration = time.time() - start_time
        return {
            "status": "max_turns_exceeded",
            "output": f"Agent did not emit [TASK_COMPLETE] within {self.max_turns} turns.",
            "turns": turn,
            "total_tokens": total_tokens,
            "duration_seconds": round(duration, 2),
            "gamification": self.gamification.evaluate_run(turn, total_tokens, duration, faults + 1),
            "provider": self.provider_name,
            "model": self.model,
        }