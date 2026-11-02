# HarnessQuest Enhancement Plan
## Transforming into a World-Class Educational Open Source Harness Engineering Project

---

## Vision
HarnessQuest becomes the **definitive educational platform** for learning harness engineering — combining:
- **Multi-provider LLM support** (OpenAI, Anthropic, NVIDIA NIM, Ollama/local)
- **20-level progressive gamification** teaching harness concepts step-by-step
- **Architecture diagrams & visual learning** (SVG)
- **Pedagogical documentation** with hands-on quests
- **Production-grade patterns** from OpenAI, Anthropic, Manus, LangChain, WalkingLabs

---

## Phase 1: Multi-Provider LLM Support (Core Infrastructure)

### 1.1 Provider Abstraction Layer
Create `harnessquest/core/providers.py` with:
- Abstract `LLMProvider` base class
- Concrete implementations:
  - `OpenAIProvider` (via LiteLLM)
  - `AnthropicProvider` (via LiteLLM)
  - `NVIDIANIMProvider` (NVIDIA NIM endpoints)
  - `OllamaProvider` (local LLMs)
  - `LiteLLMProvider` (unified fallback for 100+ providers)
- Factory pattern for provider selection
- Configuration via environment variables (NO credentials in repo)

### 1.2 Secure Configuration Management
- `harnessquest/core/config.py` - Pydantic settings with:
  - `Settings` class loading from `.env` (gitignored)
  - Environment variable mapping for all providers
  - Validation and helpful error messages
  - Example: `.env.example` template committed

### 1.3 CLI Integration
- Update `harnessquest/cli/main.py`:
  - `--provider` flag (openai, anthropic, nim, ollama, litellm)
  - `--model` flag (model name per provider)
  - `--list-providers` / `--list-models` commands
  - Interactive provider setup wizard

---

## Phase 2: 20-Level Progressive Gamification System

### Level Design Philosophy
Each level teaches **one core harness engineering concept** with:
- **Theory**: Brief explanation (2-3 paragraphs)
- **Hands-on Quest**: Runnable task demonstrating the concept
- **Verification**: Automated test proving mastery
- **Badge**: Unique achievement with icon
- **XP Reward**: Scaling with difficulty

### Level Progression (20 Levels)

| Level | Title | Concept Taught | Quest Objective |
|-------|-------|----------------|-----------------|
| 1 | **Initiate** | Hello Harness | Run first agent, understand loop |
| 2 | **Sandbox Apprentice** | Execution Boundaries | Sandbox path validation, command allow/deny |
| 3 | **Context Novice** | AGENTS.md & Repo Maps | Load and inject repository context |
| 4 | **Token Minimalist** | Context Engineering | Reduce tokens 20% via summarization |
| 5 | **Tool Smith** | Tool Design | Create custom tool with schema validation |
| 6 | **Guardrail Guardian** | Constraint Management | Add loop detection, turn limits, time budgets |
| 7 | **Verification Warden** | Self-Verification Gates | Implement eval/judge pattern |
| 8 | **Memory Keeper** | State Persistence | Save/restore session state across runs |
| 9 | **Multi-Model Mage** | Provider Abstraction | Switch providers mid-task seamlessly |
| 10 | **Local LLM Ranger** | Ollama Integration | Run quest with local model (privacy/offline) |
| 11 | **NIM Navigator** | NVIDIA NIM Cloud | Use NIM endpoints for specialized models |
| 12 | **Observability Oracle** | Telemetry & Tracing | Instrument runs with spans, metrics |
| 13 | **Parallel Pilot** | Multi-Agent Orchestration | Run sub-agents with handoff artifacts |
| 14 | **Spec-Driven Sage** | Spec-Driven Development | Execute from feature_list.json + AGENTS.md |
| 15 | **Context Condenser** | Advanced Context Engineering | KV-cache optimization, progressive disclosure |
| 16 | **Security Sentinel** | Prompt Injection Defense | MCP guardian, analyzers, sandbox hardening |
| 17 | **Eval Architect** | Benchmark Design | Build golden dataset, regression CI |
| 18 | **Harness Architect** | Full System Design | Design harness for a real project |
| 19 | **Production Hardener** | Production Hardening | Sandboxing, compaction, observability |
| 20 | **Harness Grandmaster** | Capstone | Build & document a complete harness from scratch |

### Implementation
- `harnessquest/gamification/levels.py` - Level definitions, quests, verification
- `harnessquest/gamification/progression.py` - Player state, XP, unlocks
- `harnessquest/cli/quest_mode.py` - Interactive quest CLI

---

## Phase 3: Architecture Diagrams (SVG)

### Diagrams to Create
1. **HarnessQuest System Architecture** - Overall component diagram
2. **Agent Loop Flow** - Runner → Context → Provider → Sandbox → Gamification
3. **Provider Abstraction** - Factory pattern with all 4 providers
4. **Gamification Progression** - Level tree with unlocks
5. **Context Engineering Pipeline** - AGENTS.md → Repo Map → Injection → Compression
6. **Sandbox Security Model** - Path validation, command filtering, timeout
6. **Multi-Agent Orchestration** - Parent → Sub-agents → Handoff artifacts
7. **CI/CD Evaluation Pipeline** - GitHub Actions → Benchmarks → Reports

### Location
`docs/architecture/` - All SVG files + `README.md` explaining each

---

## Phase 4: Pedagogical Documentation

### New Documentation Structure
```
docs/
├── architecture/          # SVG diagrams + explanations
├── tutorials/
│   ├── 01-getting-started.md
│   ├── 02-understanding-the-loop.md
│   ├── 03-context-engineering.md
│   ├── 04-tool-design.md
│   ├── 05-constraint-management.md
│   ├── 06-evaluation-patterns.md
│   ├── 07-multi-provider.md
│   ├── 08-local-llms.md
│   ├── 09-observability.md
│   └── 10-production-hardening.md
├── quests/
│   ├── level-01-initiate.md
│   ├── level-02-sandbox-apprentice.md
│   ... (all 20 levels)
├── providers/
│   ├── openai.md
│   ├── anthropic.md
│   ├── nvidia-nim.md
│   └── ollama.md
├── best-practices/
│   ├── harness-engineering-principles.md  # Synthesized from all references
│   ├── context-engineering.md
│   ├── tool-design.md
│   ├── constraint-management.md
│   └── production-hardening.md
└── CONTRIBUTING.md
```

### Key Reference Integration
Synthesize patterns from:
- **OpenAI (Codex)**: AGENTS.md as TOC, progressive disclosure, doc-gardening agents
- **Anthropic (Claude Code)**: Initializer agent, feature_list.json, self-verification, handoff artifacts
- **Manus**: KV-cache optimization, filesystem memory, tool masking
- **LangChain (DeepAgents)**: Middleware, orchestration, eval harness
- **WalkingLabs**: Course structure, CAR decomposition, HarnessCard
- **Snowan/Study Notes**: 4 architecture patterns, 10 mistakes, MVH (Minimum Viable Harness)

---

## Phase 5: Local LLM Connector (Ollama)

### Implementation
- `harnessquest/core/providers/ollama.py`:
  - Auto-detect Ollama installation
  - List available models (`ollama list`)
  - Pull models if missing (`ollama pull`)
  - Health check endpoint
  - Streaming support
- Fallback to LiteLLM's Ollama integration

---

## Phase 6: NVIDIA NIM Integration

### Implementation
- `harnessquest/core/providers/nim.py`:
  - NIM endpoint configuration (cloud or self-hosted)
  - Model catalog (Nemotron, Llama, Mistral, etc. via NIM)
  - API key management (NVIDIA_API_KEY)
  - Health check and model listing
  - Optimized for NVIDIA hardware

---

## Phase 7: CI/CD & GitHub Enhancements

### GitHub Actions
- `.github/workflows/quest_eval.yml` - Enhanced with:
  - Multi-provider test matrix (OpenAI, Anthropic, NIM)
  - Level progression tests
  - Benchmark regression detection
  - Badge generation for README

### GitHub Features
- Issue templates (bug, feature, quest request)
- PR template with checklist
- Discussion categories (Q&A, Showcase, Quest Help)
- Wiki for extended documentation

---

## Security & Credentials Policy

### NEVER Commit
- `.env` files
- API keys (OpenAI, Anthropic, NVIDIA)
- Any secrets

### Always Provide
- `.env.example` with all variables documented
- Clear setup instructions in README
- GitHub Actions secrets documentation

---

## Implementation Order

1. **Provider abstraction + config** (foundation)
2. **Ollama + NIM providers** (new capabilities)
3. **20-level gamification system** (core value)
4. **Architecture diagrams** (visual learning)
5. **Documentation overhaul** (pedagogical)
6. **CLI quest mode** (interactive learning)
7. **CI/CD enhancements** (quality gates)
8. **Polish & push** (release)

---

## Success Metrics

- [ ] All 20 levels playable and verifiable
- [ ] 4 providers working (OpenAI, Anthropic, NIM, Ollama)
- [ ] 7+ architecture SVGs rendered in docs
- [ ] 10+ tutorial guides
- [ ] CI passes on all providers (with secrets)
- [ ] Zero credentials in repo history
- [ ] README shows live badges (build, coverage, level)