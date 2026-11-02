# Understanding the Agent Loop

The **agent loop** is the heart of every harness. Understanding it is Level 1 of HarnessQuest.

## The Loop: Observe → Reason → Act → Repeat

```
┌─────────────────────────────────────────────────────────────┐
│                    HARNESS RUNNER                           │
├─────────────────────────────────────────────────────────────┤
│  turn = 0                                                   │
│  while turn < max_turns:                                    │
│      turn += 1                    ← TURN COUNTER            │
│      messages = assemble()      ← CONTEXT ENGINEERING       │
│      response = llm(messages)   ← LLM COMPLETION            │
│      if "[TASK_COMPLETE]" in response:                      │
│          return success         ← COMPLETION DETECTION      │
│      if "RUN: cmd" in response:                             │
│          result = sandbox(cmd)  ← TOOL EXECUTION            │
│      else:                                                  │
│          prompt continue        ← FEEDBACK                  │
└─────────────────────────────────────────────────────────────┘
```

## Turn-by-Turn Breakdown

### Turn 1: Initialization
- Runner creates `ContextEngine`, `ExecutionSandbox`, `GamificationEngine`
- `ContextEngine.load_repo_map()` reads `AGENTS.md` or generates tree
- System prompt assembled with repo context + rules

### Turn 2+: Agent Reasoning
- `assemble_context()` builds messages: system + history + user prompt
- `provider.complete()` sends to LLM (OpenAI, Anthropic, NIM, Ollama, etc.)
- Response parsed for:
  - `[TASK_COMPLETE]` → Success!
  - `RUN: <command>` → Execute in sandbox
  - Otherwise → Prompt to continue

### Tool Execution
- `sandbox.run_command(cmd)` validates path, checks forbidden list
- Runs with 15s timeout in workspace directory
- Returns stdout, stderr, exit_code
- Result fed back to agent as user message

### Completion
- On `[TASK_COMPLETE]`: `GamificationEngine.evaluate_run()`
- Calculates XP: base + turn bonus + token bonus + badge bonuses
- Awards badges: SNIPER, MINIMALIST, IRONCLAD, SPEEDSTER
- Returns result dict with stats

## Key Configuration Points

```python
runner = HarnessRunner(
    model="gpt-4o-mini",      # Model name
    max_turns=10,             # Loop limit (prevents infinite loops)
    workspace=".",            # Sandbox root
    provider="openai",        # Provider: openai, anthropic, nim, ollama, litellm
)
```

## Gamification Hooks

The loop integrates gamification at two points:

1. **Per-turn**: Token tracking, fault counting
2. **On completion**: `evaluate_run(turns, tokens, duration, faults)`

```python
# In GamificationEngine
base_xp = 100
turn_bonus = max(0, (5 - turns) * 25)        # Fewer turns = more XP
token_bonus = max(0, (2000 - tokens) * 0.1)  # Fewer tokens = more XP
badge_bonus = len(new_badges) * 50           # Badge bonuses
earned_xp = base_xp + turn_bonus + token_bonus + badge_bonus
level = total_xp // 250 + 1
```

## Badge Criteria

| Badge | Criteria | XP Bonus |
|-------|----------|----------|
| ⚡ **SNIPER** | Complete in exactly 1 turn | +50 |
| 🍃 **MINIMALIST** | < 1,200 total tokens | +50 |
| 🛡️ **IRONCLAD** | Zero faults (no errors, no blocked commands) | +50 |
| ⏱️ **SPEEDSTER** | < 2.0 seconds execution | +50 |

## Common Loop Patterns

### Pattern 1: File Exploration
```
User: "List files in current directory"
Agent: RUN: ls -la
Sandbox: [files listed]
Agent: [TASK_COMPLETE] Found 5 files...
```

### Pattern 2: Code Writing
```
User: "Create hello.py that prints hello world"
Agent: RUN: cat > hello.py << 'EOF'\nprint("Hello World")\nEOF
Sandbox: [file created]
Agent: RUN: python hello.py
Sandbox: Hello World
Agent: [TASK_COMPLETE] Created and verified hello.py
```

### Pattern 3: Multi-Step Task
```
User: "Create a Python script that reads a file and counts lines"
Agent: RUN: cat > count_lines.py << 'EOF'\n...\nEOF
Agent: RUN: echo "line1\nline2\nline3" > test.txt
Agent: RUN: python count_lines.py test.txt
Sandbox: 3 lines
Agent: [TASK_COMPLETE] Script created and tested
```

## Debugging the Loop

Enable verbose logging:
```bash
LOG_LEVEL=DEBUG harnessquest --prompt "..." --provider ollama
```

Watch for:
- **Turn count** — approaching max_turns?
- **Token usage** — growing too fast?
- **Sandbox errors** — path validation? forbidden commands?
- **Completion signal** — is agent outputting `[TASK_COMPLETE]`?

## Level 1 Quest Walkthrough

**Objective**: Run first agent task and observe complete loop

```bash
# Using Ollama (free, local)
harnessquest-quest 1 --provider ollama --model llama3.1:8b
```

**Expected flow**:
1. Quest explains theory (agent loop fundamentals)
2. Verification prompt: "List files and output [TASK_COMPLETE]"
3. Agent runs 1-2 turns, lists files, outputs completion marker
4. Gamification evaluates: awards XP, checks for badges
5. Dashboard shows Level 1 complete, 🌱 Initiate badge unlocked

**Success criteria**: Agent outputs `[TASK_COMPLETE]` with file listing

## Next: Level 2 — Sandbox Apprentice

Learn about execution boundaries, path validation, and command blocking.