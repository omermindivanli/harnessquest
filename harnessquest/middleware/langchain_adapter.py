"""LangChain Integration Adapter for HarnessQuest."""

from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from harnessquest.core.sandbox import ExecutionSandbox
from harnessquest.gamification.xp import GamificationEngine

_sandbox = ExecutionSandbox(workspace_root=".")


@tool
def sandboxed_read_file(path: str) -> str:
    """Safely read a file from the workspace sandbox."""
    return _sandbox.read_file(path)


@tool
def sandboxed_run_cmd(command: str) -> str:
    """Safely run a terminal command inside the workspace sandbox."""
    res = _sandbox.run_command(command)
    return str(res)


class LangChainHarnessWrapper:
    """Wraps LangChain execution loops with HarnessQuest gamification telemetry."""

    def __init__(self, llm_instance: Any):
        self.llm = llm_instance
        self.tools = [sandboxed_read_file, sandboxed_run_cmd]
        self.gamification = GamificationEngine()

    def execute_quest(self, user_query: str) -> Dict[str, Any]:
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an agent operating inside a Gamified LangChain Harness."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(agent=agent, tools=self.tools, verbose=False)

        import time
        t0 = time.time()
        response = executor.invoke({"input": user_query})
        duration = time.time() - t0

        stats = self.gamification.evaluate_run(
            turns=2,
            total_tokens=1500,
            duration_seconds=duration,
            faults=0
        )

        return {
            "output": response["output"],
            "gamification": stats
        }
