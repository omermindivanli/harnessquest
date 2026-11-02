"""Quest Mode CLI - Interactive gamified learning experience."""

import asyncio
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.text import Text
from rich.markdown import Markdown

from harnessquest.core.runner import HarnessRunner
from harnessquest.core.providers import list_providers
from harnessquest.core.config import get_settings, validate_provider_config, get_provider_help
from harnessquest.gamification import (
    get_progression_engine,
    PlayerProfile,
    print_player_dashboard,
    QUESTS,
    QuestStatus,
)

console = Console()


def print_quest_header(quest):
    """Print quest header with details."""
    theory_md = Markdown(quest.theory)
    
    console.print(Panel(
        f"[bold cyan]LEVEL {quest.level}: {quest.title}[/bold cyan]\n"
        f"[bold]{quest.concept}[/bold]\n\n"
        f"[yellow]Objective:[/yellow] {quest.objective}\n"
        f"[yellow]XP Reward:[/yellow] +{quest.xp_reward} XP\n"
        f"[yellow]Difficulty:[/yellow] {quest.difficulty.title()}",
        title=f"🎮 Quest: {quest.code}",
        border_style="bright_blue",
    ))
    
    console.print("\n[bold]📚 Theory:[/bold]")
    console.print(theory_md)
    
    if quest.hints:
        console.print("\n[bold]💡 Hints:[/bold]")
        for i, hint in enumerate(quest.hints, 1):
            console.print(f"  {i}. {hint}")
    
    if quest.prerequisites:
        console.print(f"\n[bold]🔗 Prerequisites:[/bold] Levels {', '.join(map(str, quest.prerequisites))}")


async def run_quest_verification(quest, runner: HarnessRunner) -> bool:
    """Verify a quest with a deterministic check (levels 2+) or a real agent run (level 1)."""
    from harnessquest.gamification.checks import run_check

    if quest.level != 1:
        ok, msg = run_check(quest.level, workspace=".")
        icon = "✅" if ok else "❌"
        console.print(f"\n[bold]🎯 Verification:[/bold] {icon} {msg}")
        return ok

    console.print(f"\n[bold]🎯 Running verification...[/bold]")
    console.print(f"Prompt: {quest.verification_prompt}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[yellow]Agent executing verification task...", total=None)
        result = await runner.run(quest.verification_prompt)
    
    if result["status"] == "success":
        console.print("\n[bold green]✅ Task completed successfully![/bold green]")
        console.print(f"Output: {result.get('output', '')[:300]}")
        return True
    else:
        console.print(f"\n[bold red]❌ Task failed: {result['status']}[/bold red]")
        console.print(f"Output: {result.get('output', result.get('error', ''))[:300]}")
        return False


async def play_quest(level: int, provider: str, model: str, auto_verify: bool = False):
    """Play a specific quest level."""
    engine = get_progression_engine()
    quest = QUESTS.get(level)
    
    if not quest:
        console.print(f"[red]Quest level {level} not found![/red]")
        return False
    
    # Check status
    status = engine.get_quest_status(level)
    if status == QuestStatus.LOCKED:
        console.print(f"[red]Quest locked! Complete prerequisites first.[/red]")
        if quest.prerequisites:
            console.print(f"Required: Levels {', '.join(map(str, quest.prerequisites))}")
        return False
    elif status == QuestStatus.COMPLETED:
        console.print(f"[yellow]Quest already completed! Replay anyway?[/yellow]")
        if not Confirm.ask("Replay quest?"):
            return False
    
    # Show quest details
    print_quest_header(quest)
    
    # Start quest
    engine.start_quest(level)
    
    # Only level 1 needs a live LLM; later levels are checked deterministically.
    runner = None
    if level == 1:
        valid, msg = validate_provider_config(provider)
        if not valid:
            console.print(f"[red]Provider error: {msg}[/red]")
            console.print(get_provider_help(provider))
            console.print("[yellow]Tip: no API key? Try --provider mock for an offline demo.[/yellow]")
            return False
        runner = HarnessRunner(model=model, max_turns=15, workspace=".", provider=provider)
    
    # Run verification
    success = await run_quest_verification(quest, runner)
    
    if success:
        # Complete quest
        result = engine.complete_quest(level)
        if result["success"]:
            console.print(Panel(
                f"[bold green]🎉 QUEST COMPLETE![/bold green]\n\n"
                f"[bold]XP Earned:[/bold] +{result['xp_earned']} XP\n"
                f"[bold]Total XP:[/bold] {result['total_xp']:,}\n"
                f"[bold]New Level:[/bold] {result['new_level']}\n"
                f"[bold]Badge Unlocked:[/bold] {result['badge']['icon']} {result['badge']['title']}",
                title="🏆 Victory!",
                border_style="gold1",
            ))
        else:
            console.print(f"[red]Error completing quest: {result['error']}[/red]")
        return True
    else:
        console.print("[red]Quest failed. Try again![/red]")
        return False


def show_quest_list():
    """Show all quests with status."""
    engine = get_progression_engine()
    profile = PlayerProfile()
    
    print_player_dashboard(profile)
    
    console.print("\n[bold]Available Commands:[/bold]")
    console.print("  [cyan]harnessquest-quest <level>[/cyan] - Play a quest")
    console.print("  [cyan]harnessquest-quest --list[/cyan] - Show this list")
    console.print("  [cyan]harnessquest-quest --dashboard[/cyan] - Show dashboard")


def quest_cli():
    """Quest mode CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HarnessQuest - Quest Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  harnessquest-quest --list                    # Show all quests
  harnessquest-quest --dashboard               # Show player dashboard
  harnessquest-quest 1                         # Play Level 1
  harnessquest-quest 5 --provider ollama       # Play with specific provider
  harnessquest-quest 10 --model llama3.1:70b   # Play with specific model
        """
    )
    
    parser.add_argument("level", type=int, nargs="?", help="Quest level to play (1-20)")
    parser.add_argument("--list", action="store_true", help="List all quests")
    parser.add_argument("--dashboard", action="store_true", help="Show player dashboard")
    parser.add_argument("--provider", type=str, default="litellm", help="LLM provider (mock = offline demo)")
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--auto-verify", action="store_true", help="Auto-verify without prompts")
    
    args = parser.parse_args()
    
    if args.list:
        show_quest_list()
        return
    
    if args.dashboard:
        profile = PlayerProfile()
        print_player_dashboard(profile)
        return
    
    if args.level is None:
        parser.error("Quest level required (1-20) or use --list/--dashboard")
    
    if not 1 <= args.level <= 20:
        parser.error("Quest level must be between 1 and 20")
    
    # Resolve model
    settings = get_settings()
    model = args.model or settings.default_model
    
    # Run quest
    asyncio.run(play_quest(args.level, args.provider, model, args.auto_verify))


if __name__ == "__main__":
    quest_cli()