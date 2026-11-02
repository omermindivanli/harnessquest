"""XP System and Achievement Tracker."""

from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass
class Achievement:
    code: str
    title: str
    description: str
    icon: str


ACHIEVEMENTS = {
    "SNIPER": Achievement("SNIPER", "One-Shot Sniper", "Completed a task in exactly 1 turn", "⚡"),
    "MINIMALIST": Achievement("MINIMALIST", "Context Minimalist", "Used fewer than 1,200 total tokens", "🍃"),
    "IRONCLAD": Achievement("IRONCLAD", "Ironclad Sandbox", "Zero permission or execution faults", "🛡️"),
    "SPEEDSTER": Achievement("SPEEDSTER", "Sub-Second Harness", "Execution loop finished in < 2.0s", "⏱️"),
}


class GamificationEngine:
    """Calculates XP rewards, levels, and unlocks badges."""

    def __init__(self):
        self.total_xp: int = 0
        self.unlocked_badges: Set[str] = set()

    def evaluate_run(self, turns: int, total_tokens: int, duration_seconds: float, faults: int) -> Dict:
        base_xp = 100
        new_badges: List[Achievement] = []

        turn_bonus = max(0, (5 - turns) * 25)
        token_bonus = max(0, int((2000 - total_tokens) * 0.1)) if total_tokens < 2000 else 0

        if turns == 1 and "SNIPER" not in self.unlocked_badges:
            self.unlocked_badges.add("SNIPER")
            new_badges.append(ACHIEVEMENTS["SNIPER"])

        if total_tokens < 1200 and "MINIMALIST" not in self.unlocked_badges:
            self.unlocked_badges.add("MINIMALIST")
            new_badges.append(ACHIEVEMENTS["MINIMALIST"])

        if faults == 0 and "IRONCLAD" not in self.unlocked_badges:
            self.unlocked_badges.add("IRONCLAD")
            new_badges.append(ACHIEVEMENTS["IRONCLAD"])

        if duration_seconds < 2.0 and "SPEEDSTER" not in self.unlocked_badges:
            self.unlocked_badges.add("SPEEDSTER")
            new_badges.append(ACHIEVEMENTS["SPEEDSTER"])

        earned_xp = base_xp + turn_bonus + token_bonus + (len(new_badges) * 50)
        self.total_xp += earned_xp

        level = (self.total_xp // 500) + 1  # same 500 XP/level as the quest progression

        return {
            "earned_xp": earned_xp,
            "total_xp": self.total_xp,
            "level": level,
            "new_badges": new_badges,
            "all_badges": [ACHIEVEMENTS[b] for b in self.unlocked_badges]
        }
