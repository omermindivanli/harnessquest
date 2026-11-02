"""Level 6 reference: loop detection."""


class LoopDetector:
    def __init__(self, limit=3):
        self.limit = limit
        self.recent = []

    def seen_loop(self, action):
        """True when the same action has just been repeated `limit` times in a row."""
        self.recent.append(action)
        return self.recent[-self.limit:] == [action] * self.limit
