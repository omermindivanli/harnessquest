# 🎮 HarnessQuest: Retro Arcade Branding Guide

## Brand vision and tone

**HarnessQuest** blends modern agent-infrastructure engineering with the nostalgia of a 16-bit retro arcade RPG.

Agents are powerful and unpredictable. Your harness is the forcefield and quest controller that keeps them disciplined, performant and safe.

Voice: playful but precise. Game language (quests, XP, badges) on the surface, honest engineering underneath. Never overclaim: the sandbox is a *teaching* sandbox, not a security product.

## Official color palette

| Token | Name | Hex | Usage |
| :--- | :--- | :--- | :--- |
| Primary CRT Dark | Obsidian Core | `#0a0914` / `#0d1117` | Backgrounds, window frames |
| Neon Green | Level Complete Green | `#00ff87` / `#10b981` | Completed quests, positive XP, progress bars |
| Neon Cyan | Cyber Mana Blue | `#00f2fe` / `#38bdf8` | Primary highlights, titles, active badges |
| Arcade Purple | Boss Arena Purple | `#9333ea` / `#c084fc` | Sandbox borders, security modules |
| Quest Gold | Trophy Amber | `#f59e0b` / `#fbbf24` | XP counters, levels, achievements |
| Retro Pink | Synthwave Flare | `#ff007f` | Headers, special badges, warning accents |

## Typography

- **Headings and titles:** monospace retro stack (`'Courier New'`, Consolas, Menlo).
- **Body and UI text:** clean sans-serif (`-apple-system`, `Segoe UI`, Roboto).
- **CLI:** high-contrast ANSI colors via the `rich` library.

## Visual assets

- Main banner: `assets/banner.svg`
- Architecture diagram: `assets/architecture.svg`
- Web UI: `harnessquest-play` serves the 20 quests, level progression and code editor at `http://127.0.0.1:7777`.
