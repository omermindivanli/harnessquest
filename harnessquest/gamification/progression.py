"""Player progression tracking and XP persistence."""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field

from harnessquest.gamification.levels import (
    ProgressionEngine,
    Quest,
    QuestStatus,
    QUESTS,
    get_progression_engine,
)


@dataclass
class PlayerStats:
    """Current player statistics."""
    level: int = 1
    total_xp: int = 0
    quests_completed: int = 0
    badges: List[Dict[str, Any]] = field(default_factory=list)
    current_quest: int = 1
    started_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)


class PlayerProfile:
    """Manages persistent player profile with XP, badges, and quest progress."""
    
    def __init__(self, storage_path: str = ".harnessquest_player.json"):
        self.storage_path = Path(storage_path)
        self.profile = self._load()
    
    def _load(self) -> PlayerStats:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                return PlayerStats(**data)
            except Exception:
                pass
        return PlayerStats()
    
    def _save(self):
        self.profile.last_active = time.time()
        with open(self.storage_path, "w") as f:
            json.dump(asdict(self.profile), f, indent=2)
    
    def add_xp(self, xp: int) -> Dict[str, Any]:
        """Add XP and check for level up."""
        old_level = self.profile.level
        self.profile.total_xp += xp
        self.profile.level = (self.profile.total_xp // 500) + 1
        
        leveled_up = self.profile.level > old_level
        self._save()
        
        return {
            "xp_added": xp,
            "total_xp": self.profile.total_xp,
            "new_level": self.profile.level,
            "leveled_up": leveled_up,
            "xp_to_next": ((self.profile.level) * 500) - self.profile.total_xp,
        }
    
    def unlock_badge(self, badge_code: str, badge_title: str, badge_icon: str, level: int):
        """Unlock a new badge."""
        badge = {
            "code": badge_code,
            "title": badge_title,
            "icon": badge_icon,
            "level": level,
            "unlocked_at": time.time(),
        }
        # Avoid duplicates
        if not any(b["code"] == badge_code for b in self.profile.badges):
            self.profile.badges.append(badge)
            self._save()
    
    def complete_quest(self, level: int):
        """Mark quest as completed."""
        if level > self.profile.quests_completed:
            self.profile.quests_completed = level
        if level >= self.profile.current_quest:
            self.profile.current_quest = level + 1
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get formatted stats for display."""
        # Single source of truth: the ProgressionEngine (written by quest completion).
        # Previously this read a separate file that was never updated, so the dashboard
        # always showed 0 XP even after completing quests.
        data = get_progression_engine().player_data
        total_xp = data.get("total_xp", 0)
        level = total_xp // 500 + 1
        completed = len(data.get("completed_quests", []))
        return {
            "level": level,
            "total_xp": total_xp,
            "quests_completed": f"{completed}/20",
            "completion_pct": round(completed / 20 * 100, 1),
            "badges_count": len(data.get("unlocked_badges", [])),
            "current_quest": data.get("current_quest", 1),
            "xp_to_next_level": level * 500 - total_xp,
        }

    def get_badges(self) -> List[Dict[str, Any]]:
        """Get all unlocked badges sorted by level."""
        badges = get_progression_engine().player_data.get("unlocked_badges", [])
        return sorted(badges, key=lambda b: b["level"])
    
    def get_quest_progress(self) -> List[Dict[str, Any]]:
        """Get progress for all quests."""
        engine = get_progression_engine()
        progress = []
        for level in range(1, 21):
            quest = QUESTS[level]
            status = engine.get_quest_status(level)
            progress.append({
                "level": level,
                "code": quest.code,
                "title": quest.title,
                "status": status.value,
                "difficulty": quest.difficulty,
                "xp_reward": quest.xp_reward,
            })
        return progress


def format_xp_bar(current_xp: int, level: int, width: int = 30) -> str:
    """Format a visual XP progress bar."""
    xp_in_level = current_xp % 500
    xp_for_next = 500
    filled = int((xp_in_level / xp_for_next) * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = round(xp_in_level / xp_for_next * 100, 1)
    return f"[{bar}] {pct}% ({xp_in_level}/{xp_for_next} XP)"


def print_player_dashboard(profile: PlayerProfile):
    """Print a rich dashboard of player progress."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.columns import Columns
    
    console = Console()
    stats = profile.get_stats()
    
    # Header
    header = f"[bold cyan]HARNESSQUEST[/bold cyan] - [bold white]Player Profile[/bold white]\n"
    header += f"Level [bold yellow]{stats['level']}[/bold yellow] | "
    header += f"Total XP: [bold green]{stats['total_xp']:,}[/bold green] | "
    header += f"Quests: [bold magenta]{stats['quests_completed']}[/bold magenta] ({stats['completion_pct']}%)"
    
    console.print(Panel(header, border_style="cyan"))
    
    # XP Bar
    xp_bar = format_xp_bar(stats['total_xp'], stats['level'])
    console.print(f"\nProgress to Level {stats['level'] + 1}: {xp_bar}")
    console.print(f"XP needed: [yellow]{stats['xp_to_next_level']}[/yellow]\n")
    
    # Badges
    badges = profile.get_badges()
    if badges:
        badge_table = Table(title="🏆 Unlocked Badges", border_style="gold1")
        badge_table.add_column("Icon", justify="center")
        badge_table.add_column("Badge", style="bold")
        badge_table.add_column("Level", justify="center")
        
        for b in badges:
            badge_table.add_row(b["icon"], b["title"], str(b["level"]))
        console.print(badge_table)
    else:
        console.print("[dim]No badges yet. Complete quests to earn them![/dim]\n")
    
    # Quest Progress
    quest_progress = profile.get_quest_progress()
    quest_table = Table(title="📜 Quest Progress", border_style="bright_blue")
    quest_table.add_column("Lv", justify="center", style="bold", width=3)
    quest_table.add_column("Code", style="cyan", width=18)
    quest_table.add_column("Title", style="white")
    quest_table.add_column("Status", justify="center", width=12)
    quest_table.add_column("Difficulty", justify="center", width=10)
    quest_table.add_column("XP", justify="right", style="yellow", width=6)
    
    status_colors = {
        "completed": "green",
        "in_progress": "yellow",
        "available": "blue",
        "locked": "dim red",
    }
    status_icons = {
        "completed": "✅",
        "in_progress": "🔄",
        "available": "🔓",
        "locked": "🔒",
    }
    
    for q in quest_progress:
        status = q["status"]
        color = status_colors.get(status, "white")
        icon = status_icons.get(status, "❓")
        quest_table.add_row(
            str(q["level"]),
            q["code"],
            q["title"],
            f"[{color}]{icon} {status}[/{color}]",
            f"[{color}]{q['difficulty']}[/{color}]",
            f"+{q['xp_reward']}",
        )
    
    console.print(quest_table)