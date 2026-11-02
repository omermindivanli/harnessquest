"""Interactive RPG CLI for HarnessQuest."""

import argparse
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.columns import Columns
from rich.text import Text

from harnessquest.core.runner import HarnessRunner
from harnessquest.core.providers import list_providers, get_all_models
from harnessquest.core.config import get_settings, validate_provider_config, get_provider_help

console = Console()


def print_banner():
    banner_text = "[bold cyan]HARNESSQUEST[/bold cyan] [dim]v1.0.0[/dim] - [bold green]Gamified Harness Engine[/bold green]"
    console.print(Panel(banner_text, expand=False, border_style="cyan"))


def print_provider_table():
    """Print available providers table."""
    providers = list_providers()
    table = Table(title="🌐 Available LLM Providers", border_style="bright_blue")
    table.add_column("Provider", style="bold cyan")
    table.add_column("Name", style="white")
    table.add_column("Default Model", style="yellow")
    table.add_column("API Key Required", style="red")
    table.add_column("Base URL Required", style="blue")
    
    for key, info in providers.items():
        table.add_row(
            key,
            info["name"],
            info["default_model"],
            "Yes" if info["requires_api_key"] else "No",
            "Yes" if info["requires_base_url"] else "No",
        )
    console.print(table)


def print_models_table(provider: str | None = None):
    """Print available models table."""
    all_models = get_all_models()
    
    if provider:
        if provider not in all_models:
            console.print(f"[red]Unknown provider: {provider}[/red]")
            return
        providers_to_show = {provider: all_models[provider]}
    else:
        providers_to_show = all_models
    
    for prov, models in providers_to_show.items():
        table = Table(title=f"🤖 Models: {prov}", border_style="bright_green")
        table.add_column("Model ID", style="bold cyan")
        table.add_column("Name", style="white")
        table.add_column("Context", style="yellow")
        table.add_column("Streaming", style="green")
        table.add_column("Tools", style="blue")
        table.add_column("Description", style="dim")
        
        for m in models:
            table.add_row(
                m.id,
                m.name,
                f"{m.context_window:,}",
                "✓" if m.supports_streaming else "✗",
                "✓" if m.supports_tools else "✗",
                m.description,
            )
        console.print(table)


async def run_cli(prompt: str, model: str, provider: str, max_turns: int, temperature: float):
    print_banner()
    
    # Validate provider
    valid, msg = validate_provider_config(provider)
    if not valid:
        console.print(f"[red]Provider configuration error: {msg}[/red]")
        console.print(get_provider_help(provider))
        sys.exit(1)
    
    runner = HarnessRunner(
        model=model,
        max_turns=max_turns,
        workspace=".",
        provider=provider,
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[yellow]Harness active... Executing task through sandbox...", total=None)
        result = await runner.run(prompt, temperature=temperature)
    
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
    table.add_row("Provider", result.get("provider", "unknown"))
    table.add_row("Model", result.get("model", "unknown"))
    
    badges_str = " ".join([f"{b.icon} {b.title}" for b in stats["all_badges"]]) or "None"
    table.add_row("Active Badges", badges_str)
    
    console.print(table)
    console.print(f"\n[bold white]Agent Output Summary:[/bold white]\n{result['output'][:500]}...\n")


def main():
    parser = argparse.ArgumentParser(
        description="HarnessQuest - Gamified AI Agent Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  harnessquest --prompt "List files in current directory" --provider ollama --model llama3.1:8b
  harnessquest --prompt "Write a hello world in Python" --provider openai --model gpt-4o-mini
  harnessquest --list-providers
  harnessquest --list-models --provider anthropic
  harnessquest --provider-help nim
        """
    )
    
    # Main execution args
    parser.add_argument("--prompt", type=str, help="Task prompt for the agent")
    parser.add_argument("--model", type=str, help="Model name (defaults to provider's default)")
    parser.add_argument("--provider", type=str, default="litellm", help="LLM provider (openai, anthropic, nim, ollama, litellm)")
    parser.add_argument("--max-turns", type=int, default=10, help="Maximum turns per run")
    parser.add_argument("--temperature", type=float, default=0.1, help="Sampling temperature")
    
    # Info commands
    parser.add_argument("--list-providers", action="store_true", help="List all available providers")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--provider-help", type=str, help="Show setup help for a provider")
    
    args = parser.parse_args()
    
    # Handle info commands
    if args.list_providers:
        print_banner()
        print_provider_table()
        return
    
    if args.list_models:
        print_banner()
        prov = args.provider if args.provider != "litellm" else None
        print_models_table(prov)
        return
    
    if args.provider_help:
        print_banner()
        console.print(Panel(get_provider_help(args.provider_help), title=f"Setup Help: {args.provider_help}", border_style="yellow"))
        return
    
    # Require prompt for execution
    if not args.prompt:
        parser.error("--prompt is required for execution (use --list-providers for info)")
    
    # Resolve model default
    settings = get_settings()
    model = args.model or settings.default_model
    provider = args.provider or settings.default_provider
    
    asyncio.run(run_cli(args.prompt, model, provider, args.max_turns, args.temperature))


if __name__ == "__main__":
    main()