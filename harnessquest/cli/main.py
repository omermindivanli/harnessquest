"""Interactive RPG CLI for HarnessQuest."""

import argparse
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from harnessquest.core.runner import HarnessRunner

console = Console()


def print_banner():
    banner_text = "[bold cyan]HARNESSQUEST[/bold cyan] [dim]v1.0.0[/dim] - [bold green]Gamified Harness Engine[/bold green]"
    console.print(Panel(banner_text, expand=False, border_style="cyan"))


async def run_cli(prompt: str, model: str):
    print_banner()

    runner = HarnessRunner(model=model, workspace=".")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[yellow]Harness active... Executing task through sandbox...", total=None)
        result = await runner.run(prompt)

    if result["status"] == "success":
        console.print("\n[bold green]Quest Completed Successfully![/bold green]\n")
    else:
        console.print("\n[bold red]Quest Failed or Exceeded Turn Limits![/bold red]\n")

    stats = result["gamification"]
    table = Table(title="🛡️ Quest Completion Stats & Rewards", border_style="bright_blue")
    
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="bold yellow")

    table.add_row("Player Level", f"Level {stats['level']}")
    table.add_row("XP Earned", f"+{stats['earned_xp']} XP (Total: {stats['total_xp']})")
    table.add_row("Execution Time", f"{result['duration_seconds']}s")
    table.add_row("Turns Used", f"{result['turns']}")
    table.add_row("Total Tokens", f"{result['total_tokens']}")

    badges_str = " ".join([f"{b.icon} {b.title}" for b in stats["all_badges"]]) or "None"
    table.add_row("Active Badges", badges_str)

    console.print(table)
    console.print(f"\n[bold white]Agent Output Summary:[/bold white]\n{result['output'][:300]}...\n")


def main():
    parser = argparse.ArgumentParser(description="HarnessQuest Interactive Engine")
    parser.add_argument("--prompt", type=str, required=True, help="Task prompt for the agent")
    parser.add_argument("--model", type=str, default="gpt-4o", help="LiteLLM provider model string")
    args = parser.parse_args()

    asyncio.run(run_cli(args.prompt, args.model))


if __name__ == "__main__":
    main()
