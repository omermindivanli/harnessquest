# Architecture Diagrams

This directory contains SVG architecture diagrams for HarnessQuest.

## Diagrams

| Diagram | Description |
|---------|-------------|
| [system-architecture.svg](system-architecture.svg) | Complete system architecture showing provider layer, core engine, gamification, and data flow |
| [agent-loop-flow.svg](agent-loop-flow.svg) | Detailed agent loop: initialization → loop (observe→reason→act) → completion & rewards |
| [provider-abstraction.svg](provider-abstraction.svg) | Provider abstraction layer with all 5 providers (OpenAI, Anthropic, NIM, Ollama, LiteLLM) |
| [gamification-progression.svg](gamification-progression.svg) | 20-level progression tree with tiers, prerequisites, XP rewards, and badges |
| [context-engineering-pipeline.svg](context-engineering-pipeline.svg) | Context engineering pipeline: source → load → assemble → inject → optimize |

## Viewing

SVG files can be viewed directly in:
- Web browsers
- VS Code (with SVG preview extension)
- GitHub (renders natively in README)
- Any SVG viewer

## Design Principles

All diagrams follow:
- **Dark theme** (`#11111b` background) matching modern IDEs
- **Color-coded layers**: 🟢 Core Engine, 🟠 Providers, 🟣 Gamification, 🔵 Context/Sandbox
- **Monospace fonts** (`JetBrains Mono`) for technical feel
- **Mermaid-compatible** structure for easy conversion
- **Accessible** with clear labels and legends

## Regenerating

Diagrams are hand-crafted SVG. To modify:
1. Edit the `.svg` file directly
2. Or use a tool like Figma/draw.io and export as SVG
3. Keep the same color scheme and fonts for consistency

## Colors Used

```css
/* Background */
--bg: #11111b;
--card: #1e1e2e;

/* Layer Colors */
--core: #a6e3a1;      /* Green - Core Engine */
--provider: #fab387;  /* Orange - Providers */
--gamify: #f5c2e7;    /* Pink - Gamification */
--context: #89b4fa;   /* Blue - Context/Sandbox */
--flow: #f9e2af;      /* Yellow - Data Flow */
--error: #f38ba8;     /* Red - Errors */
--success: #a6e3a1;   /* Green - Success */

/* Text */
--text: #cdd6f4;
--muted: #6c7086;
--title: #89b4fa;
```