"""Level 13 reference: a planner hands a structured plan to an executor."""


def make_plan(task):
    parts = [p.strip() for p in task.replace(" and ", ",").split(",") if p.strip()]
    return parts if len(parts) >= 2 else [f"analyse: {task}", f"do: {task}"]


def run_plan(plan, executor):
    """Hand each step to the executor in order and collect the results."""
    return [executor(step) for step in plan]
