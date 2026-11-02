"""Level 8 reference: persist and resume agent state."""

import json


def save_state(path, state):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def load_state(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
