"""Level 12 reference: one span per agent turn."""

import time


class Tracer:
    def __init__(self):
        self.spans = []

    def span(self, turn, model, tokens, started, tools, status):
        self.spans.append({
            "turn": turn,
            "model": model,
            "tokens": tokens,
            "duration": round(time.time() - started, 3),
            "tools": tools,
            "status": status,
        })
