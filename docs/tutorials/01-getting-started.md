# Getting Started with HarnessQuest

Welcome to **HarnessQuest** — the gamified platform for learning **harness engineering** by building and running AI agent harnesses.

## What is Harness Engineering?

> **Harness Engineering** is the discipline of designing, building, and iterating on the scaffolding that surrounds a language model in an agentic system. It has four primary levers:
> 1. **Context Design** — What the model knows before it starts
> 2. **Tool Selection** — Which tools the model has access to
> 3. **Constraint Management** — Time budgets, loop detection, verification gates
> 4. **Production Hardening** — Sandboxing, memory compaction, observability

*The model is a commodity. The harness is the moat.*

## Quick Start (5 minutes)

### 1. Install HarnessQuest

```bash
git clone https://github.com/omermindivanli/harnessquest.git
cd harnessquest
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Configure a Provider (Choose One)

#### Option A: Ollama (Local, Free, Private) — Recommended for Learning
```bash
# Install Ollama: https://ollama.com
ollama serve
ollama pull llama3.1:8b

# Run your first quest
harnessquest-quest 1 --provider ollama --model llama3.1:8b
```

#### Option B: OpenAI
```bash
# Get API key: https://platform.openai.com/api-keys
echo "OPENAI_API_KEY=sk-your-key" > .env
harnessquest-quest 1 --provider openai --model gpt-4o-mini
```

#### Option C: Anthropic
```bash
# Get API key: https://console.anthropic.com/
echo "ANTHROPIC_API_KEY=sk-ant-your-key" > .env
harnessquest-quest 1 --provider anthropic --model claude-3-5-haiku-20241022
```

#### Option D: NVIDIA NIM
```bash
# Get API key: https://build.nvidia.com
echo "NVIDIA_API_KEY=nvapi-your-key" > .env
echo "NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1" >> .env
harnessquest-quest 1 --provider nim --model meta/llama-3.1-70b-instruct
```

### 3. Run Your First Quest

```bash
# List all quests
harnessquest-quest --list

# Show your dashboard
harnessquest-quest --dashboard

# Play Level 1
harnessquest-quest 1
```

## Understanding the Quest System

### 20 Levels, 4 Tiers

| Tier | Levels | Focus | Example Badges |
|------|--------|-------|----------------|
| **Foundation** | 1-4 | Core harness concepts | 🌱 Initiate, 🛡️ Sandbox, 🗺️ Context, 🍃 Token |
| **Engineering** | 5-9 | Tools, constraints, verification | 🔨 Tool Smith, ⛔ Guardrail, ⚖️ Verification, 💾 Memory, 🔮 Multi-Model |
| **Specialization** | 10-14 | Local LLMs, NIM, observability, multi-agent, specs | 🏔️ Local Ranger, 🚀 NIM, 🔮 Observability, ✈️ Parallel, 📋 Spec-Driven |
| **Mastery** | 15-20 | Advanced patterns, security, production, capstone | 📦 Context Condenser, 🛡️ Security, 📊 Eval, 🏗️ Architect, 🏭 Production, 👑 Grandmaster |

### Each Quest Has:
- **Theory** — 2-3 paragraphs explaining the concept
- **Objective** — Hands-on task to complete
- **Verification** — Automated test proving mastery
- **Badge** — Unique achievement with icon
- **XP Reward** — Scales with difficulty (100-1000 XP)

### Progression Rules
- Complete prerequisites to unlock next level
- Earn XP → Level up (every 500 XP = 1 level)
- Unlock badges for achievements
- Track progress with `harnessquest-quest --dashboard`

## Core CLI Commands

```bash
# Main harness runner
harnessquest --prompt "List files" --provider ollama --model llama3.1:8b

# List providers
harnessquest --list-providers

# List models for a provider
harnessquest --list-models --provider openai

# Get provider setup help
harnessquest --provider-help ollama

# Quest mode
harnessquest-quest --list
harnessquest-quest --dashboard
harnessquest-quest 1 --provider ollama
```

## Project Structure

```
harnessquest/
├── harnessquest/
│   ├── core/           # Runner, Context, Sandbox, Config, Providers
│   ├── gamification/   # XP, Levels, Quests, Progression
│   ├── cli/            # Main CLI + Quest CLI
│   ├── eval/           # LLM-as-Judge evaluation
│   └── middleware/     # LangChain adapter
├── tests/              # Unit tests
├── docs/               # Documentation & Architecture diagrams
│   ├── architecture/   # SVG diagrams
│   ├── tutorials/      # Step-by-step guides
│   ├── quests/         # Quest walkthroughs
│   ├── providers/      # Provider-specific guides
│   └── best-practices/ # Harness engineering principles
└── .github/workflows/  # CI/CD evaluation
```

## Next Steps

1. **Complete Level 1** — Run your first agent and understand the loop
2. **Read Tutorial 2** — Understanding the Agent Loop (`docs/tutorials/02-understanding-the-loop.md`)
3. **Explore Architecture** — View diagrams in `docs/architecture/`
4. **Try Different Providers** — Compare OpenAI vs Anthropic vs Ollama vs NIM
5. **Build Custom Tools** — Level 5 teaches tool design

## Resources

- **Harness Engineering References:**
  - [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)
  - [Anthropic: Effective Harnesses](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)
  - [WalkingLabs: Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/en/)
  - [LangChain: Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)

- **Course:** [WalkingLabs Learn Harness Engineering](https://github.com/walkinglabs/learn-harness-engineering) — Project-based course with Electron app

## Getting Help

- `harnessquest --help` — Main CLI help
- `harnessquest-quest --help` — Quest mode help
- `harnessquest --provider-help <name>` — Provider setup instructions
- GitHub Issues: [Report bugs or request features](https://github.com/omermindivanli/harnessquest/issues)
- Discussions: [Ask questions, share progress](https://github.com/omermindivanli/harnessquest/discussions)

---

**Ready to begin?** Run `harnessquest-quest 1` and start your journey to becoming a **Harness Grandmaster**! 👑