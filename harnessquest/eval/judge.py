"""Automated Evaluator for Quest Validation."""

from typing import Dict, Any
import litellm


class HarnessJudge:
    """Evaluates agent outputs against baseline benchmark expectations."""

    def __init__(self, judge_model: str = "gpt-4o"):
        self.judge_model = judge_model

    async def evaluate_output(self, task_prompt: str, agent_output: str, expected_criteria: str) -> Dict[str, Any]:
        eval_prompt = (
            f"You are a strict QA Judge evaluating an AI Harness Output.\n\n"
            f"Task: {task_prompt}\n"
            f"Expected Criteria: {expected_criteria}\n"
            f"Agent Output: {agent_output}\n\n"
            f"Respond strictly in JSON format:\n"
            f"{{\n"
            f'  "passed": true|false,\n'
            f'  "score": <0-100>,\n'
            f'  "reasoning": "<brief explanation>"\n'
            f"}}"
        )

        response = await litellm.acompletion(
            model=self.judge_model,
            messages=[{"role": "system", "content": "You are a JSON-only evaluator."}, {"role": "user", "content": eval_prompt}],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)
